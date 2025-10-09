from .base import BaseMetricsCalculator
from .bleu_calculator import BleuCalculator
from .bert_calculator import BertScoreCalculator
from typing import List, Dict, Any

class ComprehensiveMetricsCalculator(BaseMetricsCalculator):
    """Calculadora principal que orquestra todas as métricas"""
    
    def __init__(self):
        self.bleu_calculator = BleuCalculator()
        self.bert_calculator = BertScoreCalculator()
        self.metric_calculators = {
            'bleu': self.bleu_calculator,
            'bert': self.bert_calculator
        }
    
    def calculate_metrics(self, reference_lines: list, trans_lines: list, corr_lines: list) -> List[Dict[str, Any]]:
        results_metrics = []
        
        for idx, (ref_line, corr_line, trans_line) in enumerate(zip(reference_lines, corr_lines, trans_lines), start=1):
            ref_line_clean = ref_line.strip()
            corr_line_clean = corr_line.strip()
            trans_line_clean = trans_line.strip()
            
            if not ref_line_clean or not corr_line_clean or not trans_line_clean:
                continue
                
            try:
                # Cálculo para transcrição original
                bleu_original = self.bleu_calculator.calculate(ref_line_clean, trans_line_clean)
                bert_original = self.bert_calculator.calculate(ref_line_clean, trans_line_clean)
                
                # Cálculo para transcrição corrigida
                bleu_corrected = self.bleu_calculator.calculate(ref_line_clean, corr_line_clean)
                bert_corrected = self.bert_calculator.calculate(ref_line_clean, corr_line_clean)
                
                results_metrics.append({
                    'index': idx,
                    'bleu_original': round(bleu_original * 100, 1),
                    'bleu_corrected': round(bleu_corrected * 100, 1),
                    'bleu_diff': round((bleu_corrected - bleu_original) * 100, 1),
                    'bert_original': round(bert_original * 100, 1),
                    'bert_corrected': round(bert_corrected * 100, 1),
                    'bert_diff': round((bert_corrected - bert_original) * 100, 1),
                })
            except Exception as e:
                print(f"Error processing line {idx}: {e}")
                results_metrics.append(self._create_error_metrics(idx))
        
        return results_metrics
    
    def _create_error_metrics(self, index: int) -> Dict[str, Any]:
        """Cria entrada de métricas para casos de erro"""
        return {
            'index': index,
            'bleu_original': 0,
            'bleu_corrected': 0,
            'bleu_diff': 0,
            'bert_original': 0,
            'bert_corrected': 0,
            'bert_diff': 0,
        }
    
    def get_available_metrics(self) -> Dict[str, Any]:
        """Retorna metadados de todas as métricas disponíveis"""
        return {
            name: calculator.get_metadata()
            for name, calculator in self.metric_calculators.items()
        }