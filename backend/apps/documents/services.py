"""
Document Verification & Fact Extraction Service Layer.
Implements the optional verification workflow:
user already has a self-declared profile -> chooses "Verify this information"
-> uploads supported document -> OCR/text extraction -> structured fact extraction
-> user review -> accepted facts become document-supported.

Invariants:
1. Preserve source document, page, and snippet.
2. NEVER overwrite profile silently.
3. Show extracted value vs current value.
4. User approves updates explicitly.
5. Mark extraction uncertainty (confidence score).
6. Report conflicts instead of deciding legal correctness.
7. Secure file handling with retention & deletion controls.
"""
import hashlib
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone

from .models import BusinessDocument, DocumentFactProposal, DocumentAuditLog
from apps.business_profiles.models import BusinessProfile, BusinessFact, ProfileFieldProvenance
from apps.business_profiles.services import BusinessProfileService
from .extraction_engine import DocumentTextExtractionService, ExtractedFactItem

logger = logging.getLogger(__name__)


class DocumentVerificationService:
    """
    Comprehensive service managing document ingest, native text/OCR extraction,
    fact proposal generation with conflict reporting, user acceptance review,
    and secure prototype retention/deletion.
    """

    @classmethod
    @transaction.atomic
    def process_uploaded_document(
        cls,
        document: BusinessDocument,
        raw_content: Optional[bytes] = None,
        performed_by=None
    ) -> Dict[str, Any]:
        """
        Processes an uploaded document:
        1. Calculates SHA-256 cryptographic checksum.
        2. Performs text extraction (preferring native PDF).
        3. Parses structured facts per document type.
        4. Generates DocumentFactProposal records comparing extracted vs current values.
        5. Reports conflicts without overwriting profile silently.
        """
        # 1. Tamper-evident checksum
        if raw_content:
            checksum = hashlib.sha256(raw_content).hexdigest()
            document.file_hash = checksum

        # 2. Text Extraction
        pages_text: List[str] = []
        method = "native_pdf"
        page_count = 1

        if document.file:
            pages_text, method, page_count = DocumentTextExtractionService.extract_text_from_file(
                document.file,
                document.document_type
            )
        elif raw_content:
            # Fallback if raw_content passed in memory
            try:
                pages_text = [raw_content.decode('utf-8', errors='ignore')]
            except Exception:
                pages_text = [str(raw_content)]

        document.page_count = page_count
        document.extraction_method = method
        document.raw_extracted_text = "\n--- PAGE BREAK ---\n".join(pages_text)[:10000]
        document.verification_status = 'processing'
        document.save()

        # 3. Extract facts using specialized parser
        extractor = DocumentTextExtractionService.get_extractor_for_type(document.document_type)
        extracted_items = extractor.extract_facts(pages_text, raw_bytes=raw_content)

        # 4. Compare with current self-declared profile values & generate proposals
        profile: BusinessProfile = document.business_profile
        proposals_created: List[DocumentFactProposal] = []
        extracted_dict: Dict[str, Any] = {}

        for item in extracted_items:
            extracted_dict[item.fact_key] = item.extracted_value
            curr_val = getattr(profile, item.fact_key, None)

            # Check for conflict
            has_conflict = False
            conflict_notes = ""
            if curr_val is not None:
                # Normalize string comparison
                str_curr = str(curr_val).strip().lower()
                str_ext = str(item.extracted_value).strip().lower()
                if str_curr != str_ext:
                    has_conflict = True
                    conflict_notes = f"Discrepancy noted: Current self-declared value '{curr_val}' diverges from document evidence '{item.extracted_value}'. System reports this conflict for user resolution without deciding legal correctness."

            proposal = DocumentFactProposal.objects.create(
                document=document,
                business_profile=profile,
                fact_key=item.fact_key,
                current_value=curr_val,
                extracted_value=item.extracted_value,
                source_page=item.source_page,
                evidence_snippet=item.evidence_snippet,
                confidence_score=item.confidence_score,
                has_conflict=has_conflict,
                conflict_notes=conflict_notes,
                status='pending_review'
            )
            proposals_created.append(proposal)

        document.extracted_facts = extracted_dict
        document.verification_status = 'unverified'  # Pending user review
        document.save()

        # Audit log
        DocumentAuditLog.objects.create(
            document=document,
            document_title=document.title,
            action='proposals_generated',
            details={
                'proposals_count': len(proposals_created),
                'extracted_keys': list(extracted_dict.keys()),
                'conflicts_count': sum(1 for p in proposals_created if p.has_conflict)
            },
            performed_by=performed_by
        )

        return {
            "status": "proposals_generated",
            "document_id": str(document.id),
            "page_count": page_count,
            "extraction_method": method,
            "proposals": [
                {
                    "proposal_id": str(p.id),
                    "fact_key": p.fact_key,
                    "current_value": p.current_value,
                    "extracted_value": p.extracted_value,
                    "source_page": p.source_page,
                    "evidence_snippet": p.evidence_snippet,
                    "confidence_score": p.confidence_score,
                    "has_conflict": p.has_conflict,
                    "conflict_notes": p.conflict_notes
                }
                for p in proposals_created
            ]
        }

    @classmethod
    @transaction.atomic
    def apply_user_review_decisions(
        cls,
        document: BusinessDocument,
        decisions: List[Dict[str, Any]],
        user=None
    ) -> Dict[str, Any]:
        """
        User reviews and explicitly accepts or rejects candidate facts.
        Only user-accepted facts mutate the profile and become 'document_supported'.
        Rejections or unaccepted facts leave the profile un-mutated.
        """
        profile: BusinessProfile = document.business_profile
        accepted_facts: Dict[str, Any] = {}
        provenance_updates: Dict[str, Dict[str, Any]] = {}
        processed_proposals = []

        for dec in decisions:
            proposal_id = dec.get('proposal_id')
            action = dec.get('action')  # 'accept' or 'reject'
            try:
                proposal = DocumentFactProposal.objects.get(id=proposal_id, document=document)
            except DocumentFactProposal.DoesNotExist:
                continue

            proposal.reviewed_at = timezone.now()
            proposal.reviewed_by = user if getattr(user, 'is_authenticated', False) else None

            if action == 'accept':
                proposal.status = 'accepted'
                proposal.save()

                accepted_facts[proposal.fact_key] = proposal.extracted_value

                # Prepare field provenance metadata
                doc_title = document.get_document_type_display()
                provenance_updates[proposal.fact_key] = {
                    "source_type": "document_supported",
                    "document_reference": f"{doc_title} (Doc ID: {document.id}, Page {proposal.source_page})",
                    "verified": True,
                    "verified_by": user.username if getattr(user, 'is_authenticated', False) else "User Self-Confirmation",
                    "notes": f"Verified via {document.title}. Snippet: {proposal.evidence_snippet[:150]}"
                }

                DocumentAuditLog.objects.create(
                    document=document,
                    document_title=document.title,
                    action='proposal_accepted',
                    details={
                        'proposal_id': str(proposal.id),
                        'fact_key': proposal.fact_key,
                        'applied_value': proposal.extracted_value
                    },
                    performed_by=user if getattr(user, 'is_authenticated', False) else None
                )

            elif action == 'reject':
                proposal.status = 'rejected'
                proposal.save()

                DocumentAuditLog.objects.create(
                    document=document,
                    document_title=document.title,
                    action='proposal_rejected',
                    details={
                        'proposal_id': str(proposal.id),
                        'fact_key': proposal.fact_key,
                        'retained_value': proposal.current_value
                    },
                    performed_by=user if getattr(user, 'is_authenticated', False) else None
                )

            processed_proposals.append({
                "proposal_id": str(proposal.id),
                "fact_key": proposal.fact_key,
                "status": proposal.status
            })

        # Apply accepted facts to profile via BusinessProfileService
        if accepted_facts:
            BusinessProfileService.update_profile(
                profile=profile,
                validated_data=accepted_facts,
                provenance_updates=provenance_updates,
                user=user,
                change_reason=f"Verified through {document.get_document_type_display()}",
                trigger_reeval=True
            )

        # Update document verification status
        total_proposals = document.fact_proposals.count()
        accepted_count = document.fact_proposals.filter(status='accepted').count()
        if accepted_count > 0:
            document.verification_status = 'verified'
            document.verified_at = timezone.now()
            document.verified_by = user if getattr(user, 'is_authenticated', False) else None
            document.save()

        return {
            "status": "review_completed",
            "document_id": str(document.id),
            "accepted_facts_count": len(accepted_facts),
            "processed_proposals": processed_proposals,
            "current_verification_status": document.verification_status
        }

    @classmethod
    @transaction.atomic
    def delete_document_secure(
        cls,
        document: BusinessDocument,
        user=None,
        reason: str = "User prototype retention purge"
    ) -> Dict[str, Any]:
        """
        Secure deletion & retention control:
        Purges physical file from disk/storage, removes associated fact proposals,
        and logs cryptographic deletion record in audit log.
        """
        doc_id = str(document.id)
        doc_title = document.title
        file_hash = document.file_hash

        # Remove physical file if exists
        if document.file and hasattr(document.file, 'path') and os.path.exists(document.file.path):
            try:
                os.remove(document.file.path)
            except Exception as e:
                logger.warning(f"Could not remove physical file for document {doc_id}: {e}")

        # Record audit log before deletion
        DocumentAuditLog.objects.create(
            document=None,
            document_title=doc_title,
            action='deleted',
            details={
                'deleted_document_id': doc_id,
                'file_hash': file_hash,
                'reason': reason
            },
            performed_by=user if getattr(user, 'is_authenticated', False) else None
        )

        document.delete()

        return {
            "status": "deleted",
            "document_id": doc_id,
            "purged_file_hash": file_hash,
            "message": "Document file and extraction records securely deleted per retention policy."
        }
