"""
Management Command: Run Hybrid Retrieval Evaluation Harness on 20 Statutory Golden Queries.
Outputs MRR, Recall@K, Precision@K, Tier-1 ratio, and fail-closed safety rate.
"""
from django.core.management.base import BaseCommand
from apps.rag.evaluation_harness import RetrievalEvaluationHarness


class Command(BaseCommand):
    help = 'Executes the 20-query statutory golden evaluation benchmark for Hybrid Policy Retrieval.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Hybrid Policy Retrieval Evaluation Harness..."))
        harness = RetrievalEvaluationHarness()
        eval_result = harness.run_evaluation(top_k=5)

        metrics = eval_result['metrics']
        self.stdout.write("\n================ HYBRID RETRIEVAL BENCHMARK REPORT ================")
        self.stdout.write(f"Total Queries Evaluated:    {eval_result['total_golden_queries']}")
        self.stdout.write(f"In-Domain Queries:          {eval_result['in_domain_queries']}")
        self.stdout.write(f"Out-of-Domain / OOD:        {eval_result['out_of_domain_queries']}")
        self.stdout.write("--------------------------------------------------------------------")
        self.stdout.write(f"Mean Reciprocal Rank (MRR): {metrics['mrr']:.4f}")
        self.stdout.write(f"Recall@1:                   {metrics['recall_at_1']:.4f}")
        self.stdout.write(f"Recall@3:                   {metrics['recall_at_3']:.4f}")
        self.stdout.write(f"Recall@5:                   {metrics['recall_at_5']:.4f}")
        self.stdout.write(f"Precision@1:                {metrics['precision_at_1']:.4f}")
        self.stdout.write(f"Tier-1 Gazette Ratio:       {metrics['tier1_gazette_ratio_percent']:.2f}%")
        self.stdout.write(f"Fail-Closed Safety Rate:    {metrics['fail_closed_safety_rate_percent']:.2f}%")
        self.stdout.write("====================================================================\n")

        self.stdout.write(self.style.SUCCESS("Individual Query Results:"))
        for q in eval_result['query_results']:
            if q.get('type') == 'out_of_domain':
                status = self.style.SUCCESS("PASS (Fail-Closed)") if q['passed_fail_closed'] else self.style.ERROR("FAIL (Leaked)")
                self.stdout.write(f" - {q['query_id']} [OOD]: {status}")
            else:
                hit = f"Hit Rank {q['hit_rank']}" if q['hit_rank'] > 0 else "NO HIT"
                style = self.style.SUCCESS if q['hit_rank'] == 1 else (self.style.WARNING if q['hit_rank'] > 0 else self.style.ERROR)
                self.stdout.write(f" - {q['query_id']}: {style(hit)} (RR: {q['reciprocal_rank']}, Tier: {q['top_source_tier']})")
