import nltk
from bert_score import BERTScorer
import torch
import threading

nltk.download('punkt_tab')

bert_scorer = None
bert_lock = threading.Lock()

def calculate_bleu(reference, hypothesis):
    if reference.strip() == hypothesis.strip():
        return 1.0
    reference_tokens = [nltk.word_tokenize(reference)]
    hypothesis_tokens = nltk.word_tokenize(hypothesis)
    smoothie = nltk.translate.bleu_score.SmoothingFunction().method1
    return nltk.translate.bleu_score.sentence_bleu(reference_tokens, hypothesis_tokens, smoothing_function=smoothie)

def get_bert_scorer():
    global bert_scorer
    with bert_lock:
        if bert_scorer is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            bert_scorer = BERTScorer(
                lang='pt',
                model_type='xlm-roberta-base',
                device=device,
                rescale_with_baseline=True
            )
    return bert_scorer

def calculate_bert_score(reference, hypothesis):
    if not reference.strip() or not hypothesis.strip():
        return 0.0
        
    if reference.strip() == hypothesis.strip():
        return 1.0
    
    try:
        scorer = get_bert_scorer()
        P, R, F1 = scorer.score([hypothesis], [reference])
        return F1.mean().item()
    except Exception as e:
        print(f"Error calculating BERTScore: {e}")
        return 0.0

def calculate_metrics(reference_lines, trans_lines, corr_lines):
    results_metrics = []
    
    for idx, (ref_line, corr_line, trans_line) in enumerate(zip(reference_lines, corr_lines, trans_lines), start=1):
        ref_line_clean = ref_line.strip()
        corr_line_clean = corr_line.strip()
        trans_line_clean = trans_line.strip()
        
        if not ref_line_clean or not corr_line_clean or not trans_line_clean:
            continue
            
        try:
            bleu_original = calculate_bleu(ref_line_clean, trans_line_clean)
            bert_original = calculate_bert_score(ref_line_clean, trans_line_clean)
            
            bleu_corrected = calculate_bleu(ref_line_clean, corr_line_clean)
            bert_corrected = calculate_bert_score(ref_line_clean, corr_line_clean)
            
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
            results_metrics.append({
                'index': idx,
                'bleu_original': 0,
                'bleu_corrected': 0,
                'bleu_diff': 0,
                'bert_original': 0,
                'bert_corrected': 0,
                'bert_diff': 0,
            })
            
    return results_metrics