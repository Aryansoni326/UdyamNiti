"""
Action Plan Sequencing & Execution Service Layer.
Coordinates dependency-aware task generation, validation, and completion state machine.
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from .models import ActionTask, CompletionStatus
from .engine import ActionPlanEngine, ActionTaskData
from apps.strategy.models import Strategy
from apps.business_profiles.models import BusinessProfile
from apps.policies.models import Scheme


class ActionPlanService:
    """
    Typed service for generating, updating, and sequencing action tasks.
    """

    @classmethod
    @transaction.atomic
    def generate_tasks_for_strategy(
        cls,
        strategy: Strategy,
        evaluations_data: List[Dict[str, Any]],
        relationships_data: Optional[List[Dict[str, Any]]] = None,
        unknowns: Optional[List[Dict[str, Any]]] = None
    ) -> List[ActionTask]:
        """
        Derives an ordered sequence of action tasks using ActionPlanEngine.
        """
        # Clear existing tasks to ensure idempotency
        strategy.tasks.all().delete()

        bp: BusinessProfile = strategy.business_profile
        goal_data = {
            "primary_goal": strategy.goal.raw_goal_text,
            "objective": strategy.goal.parsed_objective,
            "investment_amount_lakhs": float(strategy.goal.parsed_investment_amount_lakhs or 0)
        }
        business_facts = {
            "business_name": bp.business_name,
            "has_udyam": bool(bp.udyam_registration_number),
            "udyam_registration_number": bp.udyam_registration_number,
            "investment_in_plant_machinery_lakhs": float(bp.investment_in_plant_machinery_lakhs or 0),
            "annual_turnover_lakhs": float(bp.annual_turnover_lakhs or 0),
            "state": bp.state,
            "district": bp.district,
            "has_zed_certification": False
        }

        engine = ActionPlanEngine()
        task_data_list: List[ActionTaskData] = engine.generate_plan(
            goal=goal_data,
            business_facts=business_facts,
            selected_opportunities=evaluations_data,
            unknowns=unknowns
        )

        tasks_to_create = []
        for t_data in task_data_list:
            scheme_obj = None
            if t_data.related_scheme_ids:
                scheme_obj = Scheme.objects.filter(scheme_code=t_data.related_scheme_ids[0]).first()

            tasks_to_create.append(ActionTask(
                id=t_data.id,
                strategy=strategy,
                business_profile=bp,
                scheme=scheme_obj,
                priority=t_data.priority,
                title=t_data.title,
                rationale=t_data.rationale,
                description=t_data.rationale,
                category=t_data.category,
                dependency_ids=t_data.dependency_ids,
                related_scheme_ids=t_data.related_scheme_ids,
                evidence_ids=t_data.evidence_ids,
                external_url=t_data.external_url,
                requires_user_action=t_data.requires_user_action,
                official_deadline=t_data.official_deadline or "",
                estimated_time=t_data.estimated_time,
                status=CompletionStatus.PENDING
            ))

        created = ActionTask.objects.bulk_create(tasks_to_create)
        return created

    @classmethod
    @transaction.atomic
    def complete_task(cls, task_id: str, force: bool = False) -> ActionTask:
        """
        Marks an action task as completed.
        Validates that all prerequisite tasks in dependency_ids are completed before allowing completion.
        """
        task = ActionTask.objects.get(pk=task_id)

        # Check dependencies unless forced
        if not force and task.dependency_ids:
            uncompleted_deps = ActionTask.objects.filter(
                strategy=task.strategy,
                id__in=task.dependency_ids
            ).exclude(status=CompletionStatus.COMPLETED)

            if uncompleted_deps.exists():
                unmet_titles = [d.title for d in uncompleted_deps]
                raise ValueError(
                    f"Cannot complete task '{task.title}'. The following prerequisite tasks must be completed first: "
                    + ", ".join(unmet_titles)
                )

        task.status = CompletionStatus.COMPLETED
        task.completed_at = timezone.now()
        task.save()
        return task

    @classmethod
    @transaction.atomic
    def reopen_task(cls, task_id: str) -> ActionTask:
        """
        Reopens a completed or skipped action task.
        """
        task = ActionTask.objects.get(pk=task_id)
        task.status = CompletionStatus.PENDING
        task.completed_at = None
        task.save()
        return task
