from __future__ import annotations
from typing import Dict
from src.core.metrics import get_metrics_snapshot

def get_health() -> Dict:
    m = get_metrics_snapshot()
    status = 'ok'
    drift_proxy = 1.0 - m['Resonance']
    if drift_proxy > 0.2:
        status = 'warning'
    if drift_proxy > 0.35:
        status = 'critical'
    return {
        'status': status,
        'heartbeat': True,
        'resonance_phase_drift': round(drift_proxy,3)
    }




































