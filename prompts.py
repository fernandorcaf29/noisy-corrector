prompt_model_map = {
    "mistral-large-latest": lambda transcription: (
        f"""
        PARÂMETROS PARA CORREÇÃO MÍNIMA E FIDELIDADE MÁXIMA

        1. PROIBIÇÕES ABSOLUTAS:

        explicar, descrever ou justificar correções, retorne apenas a transcrição.

        remover ou alterar identificador do falante (início da frase)

        alterar flexão verbal, gênero, número, grau, tempo verbal ou conjugação.

        substituir termos coloquiais, gírias, regionalismos ou expressões de baixo calão por versões formais.

        reformatar, destacar ou alterar a estrutura visual do texto.

        adicionar, remover ou alterar pontuação de qualquer tipo, nem espaçamento (. , ! ? ...).

        alterar a capitalização das palavras na fala original para minúsculo

        completar palavras truncadas (ex: "tá" deve permanecer "tá", não "está").

        juntar ou separar palavras que foram ditas de uma forma específica.


        2. PRESERVAÇÃO DO TEXTO ORIGINAL:

        Mantenha inalterados: repetições, gaguejos, hesitações ("é... é..."), sons não lexicais ("ahn", "hum"), respirações audíveis e falsos inícios de frase.

        Preserve integralmente toda e qualquer expressão de oralidade, neologismo, palavra-valise e desvios gramaticais que sejam características da fala do indivíduo.

        Mantenha os dois pontos do identificador do falante exatamente onde estavam na fala original.

        Mantenha as letras maiúsculas da fala original para sinalizar pausa.

        Mantenha sem símbolo monetário caso a moeda seja indicada pelas palavras.

        3. INTERVENÇÃO MÍNIMA EXTREMA:

        Corrija apenas se uma palavra atender a um os critérios abaixo:
        a) CRITÉRIO FONÉTICO: Soar claramente como uma palavra aleatória (ex: "frilven" -> "frio vem", "T"->"tem").
        b) CRITÉRIO CONTEXTUAL: A palavra sem sentido impedir completamente a compreensão da ideia imediata da frase.

        NÃO CORRIJA se a palavra for um coloquialismo, um regionalismo, um estrangeirismo de uso comum ou um nome próprio.

        4. REGRA DE OURO PARA DÚVIDAS:

        EM CASO DE DÚVIDA, INCERTEZA OU AMBIGUIDADE: A ação padrão é NÃO MODIFICAR e manter a transcrição original.

        5. EXECUÇÃO FINAL:

        Passe a transcrição para texto cru

        Certifique-se de que o case das letras não foi alterada comparado ao da fala original.

        responda apenas com a transcrição:

        {transcription}
        """
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
