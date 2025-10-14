prompt_model_map = {
        "mistral-large-latest": lambda transcription: (
        "Modo literal: produza saída exatamente igual ao texto original, mantendo erros, repetições, pausas e pontuação existente. "
        "Não interprete, não normalize e não adicione nenhuma pontuação nova. "
        "Corrija apenas pseudopalavras (palavras inexistentes ou distorcidas foneticamente além do significado raiz) "
        "e palavras totalmente dissonantes com o contexto (erros evidentes de reconhecimento de fala). "
        "Em capitalização e nomes próprios, siga apenas a norma culta para diferenciar nomes próprios e comuns, "
        "sem alterar a primeira letra da frase. "
        "Se houver dúvida, mantenha o original. "
        "Primeiro nome de pessoa não deve ser expandido para nome completo. "
        "É estritamente proibido adicionar ou ajustar qualquer sinal de pontuação, exceto hifens e pontuação numérica já existentes. "
        "Texto entre colchetes deve ser preservado exatamente como está, sem alteração, remoção ou substituição. "
        "Saída deve ser literal, sem comentários, explicações ou pontuação (exceto hifens e pontuação numérica já existentes). "
        "TEXTO ORIGINAL (frase de uma ou mais palavras):\n"
        f"{transcription}"
        "\n\nNovamente: não adicione pontuação (exceto hifens e pontuação numérica já existentes), não interprete, mantenha o texto literal."
    ),
    "gemini-flash-latest": lambda transcription: (
        "Modo literal: produza saída exatamente igual ao texto original, mantendo erros, repetições, pausas e pontuação existente. "
        "Não interprete, não normalize e não adicione nenhuma pontuação nova. "
        "Corrija apenas pseudopalavras (palavras inexistentes ou distorcidas foneticamente além do significado raiz) "
        "e palavras totalmente dissonantes com o contexto (erros evidentes de reconhecimento de fala). "
        "Em capitalização e nomes próprios, siga apenas a norma culta para diferenciar nomes próprios e comuns, "
        "sem alterar a primeira letra da frase. "
        "Se houver dúvida, mantenha o original. "
        "Primeiro nome de pessoa não deve ser expandido para nome completo. "
        "É estritamente proibido adicionar ou ajustar qualquer sinal de pontuação, exceto hifens e pontuação numérica já existentes. "
        "Texto entre colchetes deve ser preservado exatamente como está, sem alteração, remoção ou substituição. "
        "Saída deve ser literal, sem comentários, explicações ou pontuação (exceto hifens e pontuação numérica já existentes). "
        "TEXTO ORIGINAL (frase de uma ou mais palavras):\n"
        f"{transcription}"
        "\n\nNovamente: não adicione pontuação (exceto hifens e pontuação numérica já existentes), não interprete, mantenha o texto literal."
    ),
}

def get_correction_prompt(text: str, model: str) -> str:
    return prompt_model_map[model](text)

def get_metadata_extraction_prompt(sample_text: str) -> str:
    return f"""
    ANALISE ESTE TEXTO E IDENTIFIQUE:

    **ENTIDADES PRINCIPAIS**: Nomes de pessoas, lugares, instituições, organizações (máximo 6)
    **TIPO DE CONVERSA**: entrevista, debate, discurso, reunião, aula, podcast, etc.
    **TEMA CENTRAL**: Assunto principal em 3-5 palavras

    **FORMATO EXATO PARA RESPOSTA**:
    ENTIDADES: nome1, nome2, nome3, nome4, nome5, nome6
    TIPO: [tipo específico da conversa]
    TEMA: [tema principal resumido]

    **TEXTO PARA ANALISAR**:
    {sample_text}
    """