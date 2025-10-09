import nltk
from .base import BaseMetricCalculator
from typing import Dict, Any

class BleuCalculator(BaseMetricCalculator):
    def __init__(self):
        self._ensure_punkt_downloaded()
    
    def _ensure_punkt_downloaded(self):
        try:
            nltk.data.find('tokenizers/punkt_tab')
            PUNKT_AVAILABLE = True
        except LookupError:
            PUNKT_AVAILABLE = False

        if not PUNKT_AVAILABLE:
            try:
                nltk.download('punkt_tab', quiet=True)
            except Exception as e:
                print(f"Warning: Could not download punkt_tab: {e}")
    
    def calculate(self, reference: str, hypothesis: str) -> float:
        if reference.strip() == hypothesis.strip():
            return 1.0
        
        reference_tokens = [nltk.word_tokenize(reference)]
        hypothesis_tokens = nltk.word_tokenize(hypothesis)
        smoothie = nltk.translate.bleu_score.SmoothingFunction().method1
        
        return nltk.translate.bleu_score.sentence_bleu(
            reference_tokens, hypothesis_tokens, smoothing_function=smoothie
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'BLEU',
            'description': 'Bilingual Evaluation Understudy - Medida de similaridade baseada em n-grams',
            'range': '0-1',
            'interpretation': 'Valores mais altos indicam maior similaridade léxica'
        }