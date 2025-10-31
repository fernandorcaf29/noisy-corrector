prompt_model_map = {
    "mistral-large-latest": lambda transcription: (
        f"""
            Você é um pós-processador extremamente conservador de transcrições ASR no Brasil.

            Sua meta é maximizar a similaridade entre a fala original e o texto corrigido, como medido por métricas automáticas de fidelidade (BLEU e BERTScore).

            REGRAS PRINCIPAIS:
            - Preserve integralmente o estilo de fala, ritmo, coloquialismos e estrutura do texto original.
            - Corrija APENAS palavras inexistentes em português ou distorcidas foneticamente que tornem a frase incompreensível.
            - Se a palavra for compreensível, mesmo que pareça informal, NÃO a altere.

            MANTENHA SEMPRE:
            - As formas coloquiais.
            - O vocabulário e o tempo verbal originais, mesmo se gramaticalmente incorretos.

            NUNCA:
            - Substitua palavras corretas por outras apenas mais formais ou “melhores”.
            - Corrija concordância, ortografia estilizada ou expressões informais.

            O texto deve continuar soando como uma fala transcrita natural, apenas com palavras inexistentes corrigidas foneticamente.

            Retorne a transcrição corrigida completa, sem comentários, sem pontuação (exceto os dois pontos (:) que delimitam locutor e fala), sem negrito.

            TEXTO ORIGINAL (frase de uma ou mais palavras):
            {transcription}
        """
    ),
    "gemini-2.5-flash": lambda transcription: (
        f"""
            Você é um pós-processador de transcrições ASR do Brasil.

            Sua função é preservar a fala original ao máximo, corrigindo apenas o estritamente necessário, maximizando a similaridade entre o texto original e a fala real.

            INSTRUÇÕES FUNDAMENTAIS:
            - Corrija SOMENTE palavras inexistentes em português ou incoerentes com o contexto da entrevista.
            - Se a palavra for compreensível, mesmo que incoerente e incoesa, mantenha exatamente como está.

            PROIBIÇÕES ABSOLUTAS:
            - Não reformule frases.
            - Não corrija gramática, ortografia estilizada ou informalidade.
            - Não remova repetições.

            Retorne a transcrição corrigida completa, sem comentários, sem pontuação (exceto os dois pontos (:) que delimitam locutor e fala), sem negrito.

            TEXTO ORIGINAL (frase de uma ou mais palavras):
            {transcription}
        """
    ),
}
