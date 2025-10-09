from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseMetricCalculator(ABC):
    """Interface base para todas as métricas"""
    
    @abstractmethod
    def calculate(self, reference: str, hypothesis: str) -> float:
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre a métrica"""
        pass

class BaseMetricsCalculator(ABC):
    """Interface para calculadoras que usam múltiplas métricas"""
    
    @abstractmethod
    def calculate_metrics(self, reference_lines: list, trans_lines: list, corr_lines: list) -> list:
        pass