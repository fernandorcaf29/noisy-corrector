import nltk
from bert_score import score

nltk.download('punkt_tab')

def calculate_bleu(reference, hypothesis):
    reference_tokens = [nltk.word_tokenize(reference)]
    hypothesis_tokens = nltk.word_tokenize(hypothesis)
    smoothie = nltk.translate.bleu_score.SmoothingFunction().method6
    return nltk.translate.bleu_score.sentence_bleu(reference_tokens, hypothesis_tokens, smoothing_function=smoothie)

def calculate_bert_score(references, hypotheses):
    try:
        if isinstance(references, str):
            references = [references]
        if isinstance(hypotheses, str):
            hypotheses = [hypotheses]

        # Forçar CPU e modelo mais leve se necessário
        P, R, F1 = score(
            hypotheses, references, 
            lang='pt', 
            model_type='xlm-roberta-base',
            device='cpu'
        )
        return F1.mean().item()
    except Exception as e:
        print(f"Error calculating BERTScore: {e}")
        return 0.0