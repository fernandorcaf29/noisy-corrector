from .metrics_calculator import ComprehensiveMetricsCalculator

def calculate_metrics(reference_lines, trans_lines, corr_lines):
    calculator = ComprehensiveMetricsCalculator()
    return calculator.calculate_metrics(reference_lines, trans_lines, corr_lines)

__all__ = ['calculate_metrics', 'ComprehensiveMetricsCalculator']