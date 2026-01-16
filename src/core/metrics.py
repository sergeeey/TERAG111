from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict
import os, numpy as np
from src.telemetry.journal import append_cycle
from src.core.cognitive_resonance import get_phase, update_phase

_state = {
  'RSS': 0.88,
  'COS': 0.86,
  'FAITH': 0.89,
  'Growth': 0.002,
  'Resonance': 0.92,
  'confidence': 0.90
}

SIM_MODE = os.getenv('SIM_MODE','true').lower()=='true'

def heartbeat():
    # простая симуляция дрейфа и стабилизации фаз
    phase_before = get_phase()
    update_phase()
    phase_after = get_phase()
    phase_drift = abs(phase_after - phase_before)
    _state['Resonance'] = float(max(0.0, min(1.0, 1.0 - min(phase_drift/3.14159, 1.0))))
    # лёгкая автоподстройка Growth к целевому
    target_growth = 0.003 if _state['Resonance'] > 0.9 else 0.001
    _state['Growth'] = float(_state['Growth'] + 0.25*(target_growth - _state['Growth']))
    # запись в журнал (можно дергать раз в секунду планировщиком)
    append_cycle({
        'cycle_id': int(datetime.now().timestamp()*1000),
        'RSS': _state['RSS'], 'COS': _state['COS'], 'FAITH': _state['FAITH'],
        'Growth': _state['Growth'], 'Resonance': _state['Resonance'],
        'phase': phase_after, 'confidence': _state['confidence']
    })

def get_metrics_snapshot() -> Dict:
    if SIM_MODE:
        heartbeat()
    return {
        'RSS': round(_state['RSS'], 3),
        'COS': round(_state['COS'], 3),
        'FAITH': round(_state['FAITH'], 3),
        'Growth': round(_state['Growth'], 6),
        'Resonance': round(_state['Resonance'], 3),
        'confidence': round(_state['confidence'], 3),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }




































