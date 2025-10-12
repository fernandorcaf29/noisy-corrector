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
    "gemini-1.5-flash": lambda transcription: (
        "Considere o exemplo a seguir para correção de uma transcrição:\n\n"
        "Qual a correção para a transcrição abaixo? Siga rigorosamente estas regras em ordem numérica de prioridade:\n\n"
        f"{transcription}\n\n"
        "1. PROIBIÇÕES ABSOLUTAS:\n"
        "  - NUNCA remova ou altere identificador do falante (início da frase)\n"
        "  - NUNCA Altere flexão verbal, gênero, número ou grau das palavras\n"
        "  - NUNCA Troque termo coloquial por formal\n"
        "  - NUNCA adicione pontuação\n\n"
        "2. PRESERVAÇÃO DO TEXTO ORIGINAL:\n"
        "  - Mantenha sempre o identificador inicial da frase inalterado, isso inclui siglas, "
        "abreviações, pontuação e capitalização\n"
        "  - Mantenha as letras maiusculas da frase original\n"
        "  - Mantenha a flexão de genero original das palavras\n"
        "  - Mantenha repetições e gaguejos sobre palavras\n"
        '  - Mantenha sempre expressões e marcadores de oralidade (ex: "ufa!", "oh")\n'
        "  - Mantenha sempre Neologismos e palavras-valise\n\n"
        "3. INTERVENÇÃO MÍNIMA:\n"
        "  - Se a transcrição original for compreensível (mesmo com erros), NÃO CORRIJA\n"
        "  - Apenas corrija quando:\n"
        "    * A palavra NÃO existe no português\n"
        "    * Há claramente um erro de reconhecimento fonético\n"
        "    * O significado original foi completamente distorcido\n\n"
        "4. PARA FRASES CURTAS (<3 palavras):\n"
        "  - Só corrija se houver evidente erro de digitação\n"
        "  - Mantenha inalterado caso contrário\n\n"
        "5. EM CASO DE DÚVIDA:\n"
        "  - SEMPRE prefira manter a transcrição original\n\n"
        "Responda apenas com a correção."
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