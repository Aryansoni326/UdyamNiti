from rest_framework import views, status, viewsets, permissions
from rest_framework.response import Response

from apps.eligibility.services import EligibilityEvaluationService
from apps.eligibility.models import EligibilityEvaluation
from apps.eligibility.serializers import (
    SingleSchemeEvaluationRequestSerializer,
    BatchEvaluationRequestSerializer,
    ReEvaluationRequestSerializer,
    EligibilityResponseSerializer
)
from apps.business_profiles.models import BusinessProfile
from apps.policies.models import Scheme


class SingleSchemeEvaluateAPIView(views.APIView):
    """
    Evaluates a single scheme against a business profile snapshot deterministically.
    Guarantees zero AI percentage hallucination.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SingleSchemeEvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = EligibilityEvaluationService()
        try:
            result = service.evaluate_scheme(
                profile_id=data['profile_id'],
                scheme_id=data['scheme_id'],
                goal_id=data.get('goal_id'),
                version_number=data.get('scheme_version')
            )
            return Response(result, status=status.HTTP_200_OK)
        except BusinessProfile.DoesNotExist:
            return Response({'error': f"BusinessProfile '{data['profile_id']}' not found."}, status=status.HTTP_404_NOT_FOUND)
        except Scheme.DoesNotExist:
            return Response({'error': f"Scheme '{data['scheme_id']}' not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({'error': f"Evaluation error: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchEvaluateAPIView(views.APIView):
    """
    Evaluates multiple candidate schemes in batch for a given business profile snapshot.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = BatchEvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = EligibilityEvaluationService()
        try:
            batch_result = service.evaluate_batch(
                profile_id=data['profile_id'],
                scheme_ids=data['scheme_ids'],
                goal_id=data.get('goal_id')
            )
            return Response(batch_result, status=status.HTTP_200_OK)
        except BusinessProfile.DoesNotExist:
            return Response({'error': f"BusinessProfile '{data['profile_id']}' not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({'error': f"Batch evaluation error: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReEvaluateAPIView(views.APIView):
    """
    Updates profile facts and re-evaluates all previously evaluated schemes,
    ensuring point-in-time consistency after a profile change.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ReEvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = EligibilityEvaluationService()
        try:
            result = service.re_evaluate_profile(
                profile_id=data['profile_id'],
                updated_facts=data.get('updated_facts'),
                goal_id=data.get('goal_id')
            )
            return Response(result, status=status.HTTP_200_OK)
        except BusinessProfile.DoesNotExist:
            return Response({'error': f"BusinessProfile '{data['profile_id']}' not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({'error': f"Re-evaluation error: {str(exc)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
