import torch
from bert_score import BERTScorer
from .base import BaseMetricCalculator
from typing import Dict, Any

class BertScoreCalculator(BaseMetricCalculator):
    def __init__(self):
        self._scorer = None
    
    @property
    def _scorer_instance(self):
        if self._scorer is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self._scorer = BERTScorer(
                lang='pt',
                model_type='xlm-roberta-base',
                device=device,
                rescale_with_baseline=True
            )
        return self._scorer
    
    def calculate(self, reference: str, hypothesis: str) -> float:
        if not reference.strip() or not hypothesis.strip():
            return 0.0
            
        if reference.strip() == hypothesis.strip():
            return 1.0
        
        try:
            scorer = self._scorer_instance
            P, R, F1 = scorer.score([hypothesis], [reference])
            return F1.mean().item()
        except Exception as e:
            print(f"Error calculating BERTScore: {e}")
            return 0.0
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'BERTScore',
            'description': 'Métrica semântica baseada em embeddings BERT',
            'range': '0-1', 
            'interpretation': 'Valores mais altos indicam maior similaridade semântica',
            'model': 'xlm-roberta-base'
        }