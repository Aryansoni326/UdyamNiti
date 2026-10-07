"""
Observability Endpoints & Interactive Diagnostics Dashboard.
Provides:
- GET /health/ or /api/v1/health/ : Liveness probe
- GET /health/ready/ or /api/v1/health/ready/ : Deep readiness probe
- GET /api/v1/diagnostics/ : Structured JSON metrics export
- GET /diagnostics/ : Visual, demo-friendly HTML diagnostics console
"""
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .health import HealthCheckService
from .metrics import ObservabilityRegistry


@api_view(['GET'])
@permission_classes([AllowAny])
def health_liveness_view(request):
    """Liveness probe for load balancers / container health."""
    data = HealthCheckService.check_liveness()
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_readiness_view(request):
    """Deep readiness probe checking database, cache, vector model, and LLM configuration."""
    all_ready, details = HealthCheckService.check_readiness()
    http_status = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(details, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def diagnostics_api_view(request):
    """Returns structured JSON summary of system metrics and recent request traces."""
    registry = ObservabilityRegistry()
    metrics = registry.get_metrics_summary()
    traces = registry.get_recent_traces(limit=30)
    metrics["recent_traces"] = traces
    return Response(metrics, status=status.HTTP_200_OK)


def diagnostics_dashboard_view(request):
    """
    Visual, dark-mode, high-polish HTML dashboard for live hackathon demonstration
    and real-time system failure diagnosis.
    """
    registry = ObservabilityRegistry()
    metrics = registry.get_metrics_summary()
    traces = registry.get_recent_traces(limit=25)
    _, readiness = HealthCheckService.check_readiness()

    # Build status badge colors
    def get_badge(code):
        if code < 300:
            return '<span style="background: #10B981; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600;">' + str(code) + '</span>'
        elif code < 400:
            return '<span style="background: #3B82F6; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600;">' + str(code) + '</span>'
        elif code < 500:
            return '<span style="background: #F59E0B; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600;">' + str(code) + '</span>'
        else:
            return '<span style="background: #EF4444; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600;">' + str(code) + '</span>'

    trace_rows = []
    for t in traces:
        badge = get_badge(t['status_code'])
        trace_rows.append(f"""
        <tr>
            <td style="font-family: monospace; color: #60A5FA;">{t['trace_id']}</td>
            <td><strong>{t['method']}</strong></td>
            <td style="font-family: monospace; font-size: 13px;">{t['path']}</td>
            <td>{badge}</td>
            <td>{t['duration_ms']} ms</td>
            <td style="color: #9CA3AF; font-size: 12px;">{t['timestamp'][11:19]}</td>
        </tr>
        """)

    trace_table_html = "".join(trace_rows) if trace_rows else "<tr><td colspan='6' style='text-align:center; padding: 20px;'>No request traces recorded yet.</td></tr>"

    # Component health items
    comp_items = []
    for c_name, c_data in readiness.get("components", {}).items():
        is_healthy = c_data.get("healthy", False)
        status_color = "#10B981" if is_healthy else "#F59E0B"
        comp_items.append(f"""
        <div style="background: #1E293B; padding: 14px; border-radius: 8px; border-left: 4px solid {status_color};">
            <div style="font-size: 12px; text-transform: uppercase; color: #94A3B8; font-weight: 700;">{c_name.replace('_', ' ')}</div>
            <div style="font-size: 16px; font-weight: 600; color: #F8FAFC; margin-top: 4px;">{c_data.get('status', 'OK')}</div>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">{c_data.get('latency_ms', '') and f"{c_data.get('latency_ms')} ms" or c_data.get('backend', '') or c_data.get('provider', '')}</div>
        </div>
        """)
    comp_html = "".join(comp_items)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UdyamNiti | System Observability & Telemetry</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background: #0F172A;
            color: #E2E8F0;
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .title {{
            font-size: 24px;
            font-weight: 700;
            color: #F8FAFC;
        }}
        .badge-live {{
            background: #064E3B;
            color: #34D399;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .badge-live::before {{
            content: "";
            width: 8px;
            height: 8px;
            background: #34D399;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 0.4; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.4; }}
        }}
        .grid-4 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 18px;
        }}
        .card-label {{
            font-size: 13px;
            color: #94A3B8;
            font-weight: 500;
        }}
        .card-value {{
            font-size: 28px;
            font-weight: 700;
            color: #F8FAFC;
            margin-top: 6px;
        }}
        .card-subtext {{
            font-size: 12px;
            color: #64748B;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            text-align: left;
            background: #0F172A;
            padding: 12px 14px;
            color: #94A3B8;
            border-bottom: 1px solid #334155;
            font-size: 12px;
            text-transform: uppercase;
        }}
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid #1E293B;
        }}
        tr:hover td {{
            background: #1E293B;
        }}
        .btn-refresh {{
            background: #3B82F6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="title">UdyamNiti System Telemetry & Diagnostics</div>
                <div style="color: #94A3B8; font-size: 14px; margin-top: 4px;">Real-time AI Orchestrator, RAG Latency, and Tenant Observability</div>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <span class="badge-live">LIVE TELEMETRY</span>
                <a href="/diagnostics/" class="btn-refresh">Refresh</a>
            </div>
        </div>

        <div style="margin-bottom: 24px;">
            <div style="font-size: 14px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 12px;">Component Readiness</div>
            <div class="grid-4">
                {comp_html}
            </div>
        </div>

        <div class="grid-4">
            <div class="card">
                <div class="card-label">Total API Invocations</div>
                <div class="card-value">{metrics['api_traffic']['total_requests']}</div>
                <div class="card-subtext">Avg Latency: {metrics['api_traffic']['latency_ms']['avg']} ms</div>
            </div>
            <div class="card">
                <div class="card-label">Latency p95 / p99</div>
                <div class="card-value">{metrics['api_traffic']['latency_ms']['p95']} <span style="font-size: 16px; color:#94A3B8;">/ {metrics['api_traffic']['latency_ms']['p99']} ms</span></div>
                <div class="card-subtext">Max Peak: {metrics['api_traffic']['latency_ms']['max']} ms</div>
            </div>
            <div class="card">
                <div class="card-label">LLM Calls & Tokens</div>
                <div class="card-value">{metrics['llm_observability']['total_calls']} <span style="font-size: 16px; color:#94A3B8;">({metrics['llm_observability']['total_tokens']} tok)</span></div>
                <div class="card-subtext">Avg LLM Latency: {metrics['llm_observability']['avg_latency_ms']} ms</div>
            </div>
            <div class="card">
                <div class="card-label">Fallback & Resilience Invocations</div>
                <div class="card-value" style="color: {'#10B981' if metrics['fallbacks_and_anomalies']['total_fallbacks_triggered'] == 0 else '#F59E0B'};">{metrics['fallbacks_and_anomalies']['total_fallbacks_triggered']}</div>
                <div class="card-subtext">Rule evaluations: {metrics['rule_engine_observability']['total_evaluations']}</div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="font-size: 16px; font-weight: 700; color: #F8FAFC;">Recent Request Traces (Last 25)</div>
                <div style="font-size: 12px; color: #94A3B8;">Uptime: {metrics['system']['uptime_formatted']}</div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Trace ID</th>
                        <th>Method</th>
                        <th>Path</th>
                        <th>Status</th>
                        <th>Latency</th>
                        <th>Time (UTC)</th>
                    </tr>
                </thead>
                <tbody>
                    {trace_table_html}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    return HttpResponse(html_content, content_type="text/html")


@api_view(['GET'])
@permission_classes([AllowAny])
def prototype_metrics_api_view(request):
    """
    Returns empirical, measured prototype test metrics for judge evaluation.
    Query param ?refresh=true forces a live re-evaluation of benchmarks.
    """
    from .evaluation_metrics import PrototypeEvaluationService
    force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'
    data = PrototypeEvaluationService.get_measured_prototype_metrics(force_refresh=force_refresh)
    return Response(data, status=status.HTTP_200_OK)


def prototype_metrics_dashboard_view(request):
    """
    Judge-Facing Interactive Prototype Test Results Dashboard.
    Presents empirical test outputs across the 10 required product quality dimensions.
    """
    from .evaluation_metrics import PrototypeEvaluationService
    force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
    data = PrototypeEvaluationService.get_measured_prototype_metrics(force_refresh=force_refresh)
    m = data.get('metrics', {})

    def metric_card(item_key, icon="📊"):
        item = m.get(item_key, {})
        val = item.get('value', 'Not measured yet')
        lbl = item.get('label', item_key.replace('_', ' ').title())
        details = item.get('details', '')
        is_measured = item.get('measured', False) and val != 'Not measured yet'

        val_color = "#10B981" if is_measured else "#94A3B8"
        status_pill = f'<span style="background: rgba(16, 185, 129, 0.2); color: #34D399; font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600;">MEASURED</span>' if is_measured else f'<span style="background: rgba(148, 163, 184, 0.2); color: #94A3B8; font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600;">UNMEASURED</span>'

        return f"""
        <div style="background: #1E293B; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">{lbl}</span>
                    {status_pill}
                </div>
                <div style="font-size: 24px; font-weight: 800; color: {val_color}; margin-bottom: 8px;">
                    {val}
                </div>
            </div>
            <div style="font-size: 12px; color: #94A3B8; line-height: 1.5; border-top: 1px solid rgba(255, 255, 255, 0.06); padding-top: 10px; margin-top: 8px;">
                {details}
            </div>
        </div>
        """

    cards_html = "".join([
        metric_card('curated_schemes'),
        metric_card('official_source_documents'),
        metric_card('rag_retrieval_recall'),
        metric_card('citation_correctness'),
        metric_card('deterministic_rule_test_pass_rate'),
        metric_card('evidence_coverage'),
        metric_card('relationship_cases_with_evidence'),
        metric_card('unlock_paths_detected'),
        metric_card('policy_impact_test_cases_passed'),
        metric_card('end_to_end_latency'),
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UdyamNiti | Prototype Empirical Test Results Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #0B0F19;
            color: #F8FAFC;
            font-family: 'Inter', sans-serif;
            padding: 32px 24px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1E293B;
            padding-bottom: 24px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .brand {{ display: flex; align-items: center; gap: 12px; }}
        .logo-badge {{
            background: linear-gradient(135deg, #2563EB, #1D4ED8);
            color: white;
            font-weight: 800;
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 16px;
            letter-spacing: 0.5px;
        }}
        .title-group h1 {{ font-size: 24px; font-weight: 800; color: #F8FAFC; }}
        .title-group p {{ font-size: 13px; color: #94A3B8; margin-top: 4px; }}
        .action-group {{ display: flex; gap: 12px; }}
        .btn {{
            background: #2563EB;
            color: white;
            padding: 9px 16px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.2s ease;
        }}
        .btn:hover {{ background: #1D4ED8; }}
        .btn-outline {{
            background: #1E293B;
            color: #CBD5E1;
            border: 1px solid #334155;
        }}
        .btn-outline:hover {{ background: #334155; color: white; }}
        .banner {{
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid #334155;
            border-left: 4px solid #3B82F6;
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 28px;
            font-size: 13px;
            color: #CBD5E1;
            line-height: 1.6;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #64748B;
            padding-top: 24px;
            border-top: 1px solid #1E293B;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="brand">
                <div class="logo-badge">UN</div>
                <div class="title-group">
                    <h1>Prototype Empirical Test Results</h1>
                    <p>Audited Quality, RAG Retrieval, & Deterministic Rule Execution Evidence</p>
                </div>
            </div>
            <div class="action-group">
                <a href="?refresh=true" class="btn">🔄 Re-evaluate Live</a>
                <a href="/api/v1/prototype-metrics/" target="_blank" class="btn btn-outline">Raw JSON API</a>
            </div>
        </div>

        <div class="banner">
            <strong>🛡️ Senior Product Analytics & ML Evaluation Standard:</strong>
            All figures shown below originate exclusively from live database scans, golden benchmark test executions, or deterministic rule engine assertions. If a metric has not been tested in this environment, it explicitly reports <em>"Not measured yet"</em> rather than an ungrounded or synthetic estimate.
        </div>

        <div class="grid">
            {cards_html}
        </div>

        <div class="footer">
            UdyamNiti System Telemetry &copy; 2026 • Evaluated at: {data.get('evaluated_at')} • Status: {data.get('status')}
        </div>
    </div>
</body>
</html>
"""
    return HttpResponse(html_content, content_type="text/html")

