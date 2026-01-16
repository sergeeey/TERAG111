"""
Expected Calibration Error (ECE) calculation
"""

import numpy as np
from typing import List


def calculate_ece(
    confidences: List[float],
    accuracies: List[float],
    n_bins: int = 10
) -> float:
    """
    Рассчитать Expected Calibration Error (ECE)
    
    ECE измеряет, насколько хорошо калиброваны confidence scores.
    Идеальное значение: 0.0 (confidence = accuracy)
    Target для TERAG: <0.1 (10%)
    
    Args:
        confidences: Список confidence scores [0.0, 1.0]
        accuracies: Список фактических accuracy (1.0 если правильно, 0.0 если неправильно)
        n_bins: Количество бинов для разбиения [0, 1]
    
    Returns:
        ECE значение (float)
    """
    if len(confidences) != len(accuracies):
        raise ValueError("confidences and accuracies must have the same length")
    
    if len(confidences) == 0:
        return 0.0
    
    confidences = np.array(confidences)
    accuracies = np.array(accuracies)
    
    # Границы бинов
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        # Находим индексы элементов в бине
        in_bin = np.where((confidences > bin_lower) & (confidences <= bin_upper))[0]
        
        if len(in_bin) > 0:
            # Средняя accuracy в бине
            bin_accuracy = np.mean(accuracies[in_bin])
            
            # Средняя confidence в бине
            bin_confidence = np.mean(confidences[in_bin])
            
            # Вклад бина в ECE (взвешенный по количеству элементов)
            ece += len(in_bin) * abs(bin_accuracy - bin_confidence)
    
    # Нормализуем на общее количество элементов
    ece = ece / len(confidences)
    
    return float(ece)


def calculate_brier_score(
    confidences: List[float],
    accuracies: List[float]
) -> float:
    """
    Рассчитать Brier Score
    
    Brier Score измеряет качество вероятностных предсказаний.
    Идеальное значение: 0.0
    Target для TERAG: <0.05
    
    Args:
        confidences: Список confidence scores [0.0, 1.0]
        accuracies: Список фактических accuracy (1.0 если правильно, 0.0 если неправильно)
    
    Returns:
        Brier Score (float)
    """
    if len(confidences) != len(accuracies):
        raise ValueError("confidences and accuracies must have the same length")
    
    if len(confidences) == 0:
        return 0.0
    
    confidences = np.array(confidences)
    accuracies = np.array(accuracies)
    
    # Brier Score = mean((confidence - accuracy)^2)
    brier = np.mean((confidences - accuracies) ** 2)
    
    return float(brier)
