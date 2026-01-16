from __future__ import annotations
from typing import Dict
from src.core import metrics as M

ALPHA=0.15

def accept_feedback(payload: Dict) -> bool:
    # payload: { 'target': {'RSS':0.9,'COS':0.9,'FAITH':0.92,'Resonance':0.95}} (поля опциональны)
    target = payload.get('target',{})
    for k,v in target.items():
        if k in M.__dict__.get('_state',{}):
            cur = M._state[k]
            M._state[k] = float(cur + ALPHA*(float(v)-float(cur)))
    return True




































