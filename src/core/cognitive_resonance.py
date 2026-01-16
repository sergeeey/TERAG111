from __future__ import annotations
import math, random

_phase = 0.0

def get_phase() -> float:
    return _phase

def update_phase():
    global _phase
    # фазовый сдвиг со слабым шумом, имитация согласования
    drift = 0.08 + random.uniform(-0.02, 0.02)
    _phase = (_phase + drift) % (2*math.pi)

def phase_alignment_index(history):
    # history: список фаз, чем ниже дисперсия модульного расстояния, тем выше PAI
    if not history:
        return 0.0
    # грубая оценка через среднеквадрат отклонений синуса/косинуса
    import statistics, math
    xs = [math.cos(x) for x in history]
    ys = [math.sin(x) for x in history]
    var = statistics.pvariance(xs)+statistics.pvariance(ys)
    score = max(0.0, min(1.0, 1.0 - min(var, 2.0)/2.0))
    return score




































