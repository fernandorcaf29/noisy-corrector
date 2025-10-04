prompt_model_map = {
    "mistral-large-latest": lambda transcription: (
        f"""
        1. PROIBIÇÕES ABSOLUTAS:

        - Não Adicionar, remover ou alterar pontuação de qualquer tipo (. , ! ? ...).
        - Não remover ou alterar o identificador do falante (início da frase).
        - Não alterar a flexão verbal, gênero, número, grau ou conjugação correta já presente.
        - Não substituir gírias, coloquialismos, regionalismos ou estrangeirismos.
        - Não mudar o uso de letras maiúsculas ou minúsculas em relação à fala original, mesmo que aparente ser sem sentido.
        - Não "fomalizar" palavras ("tá" não vira "está").
        - Não juntar nem separar palavras que já estão corretas.
        - Não adicionar símbolo monetário.

        2. PRESERVAÇÃO DO TEXTO ORIGINAL:

        - Mantenha repetições, gaguejos, hesitações ("é... é..."), sons não lexicais ("ahn", "hum"), respirações e falsos inícios.
        - Preserve oralidade, neologismos, palavras-valise e desvios gramaticais típicos da fala.
        - Preserve o identificador do falante com dois pontos exatamente onde estava.

        3. INTERVENÇÃO MÍNIMA:
        - Se a transcrição original for compreensível (mesmo com erros), NÃO CORRIJA
        - Apenas corrija quando:
            * A palavra NÃO existe no português
            * A palavra não faz nenhum sentido com o tema da fala

        TRANSCRIÇÃO:"{transcription}"
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
    "header":(
        """
            CONTEXTO: Você é um transcritor de um texto ASR, mas sua objetivo não é corrigir a gramatica ou ortografia dele, mas sim procurar ruídos da passagem de audio para texto.

            Veja um exemplo a baixo:

            Fala errada: "entrevistadora anonima: quais as propostas que os candidatos de Niterói T pra causa animal da cidade é isso que a gente quer saber nesse mês de setembro para definir o nosso Voto no dia 6 de outubro e toda essa política pública afeta os nossos Pets afeta os animais abandonados e os vítimas de maus tratos Então isso é nosso dia a dia e a gente quer saber como solucionar essas questões Então hoje eu tô aqui com o Bruno Lessa e eu quero que você se apresente por favor do as boas vindas ao Niterói Dog Best Frend obrigada por est aqui"

            Fala correta: "entrevistadora anonima: quais as propostas que os candidatos de Niterói têm pra causa animal da cidade é isso que a gente quer saber nesse mês de setembro pra definir o nosso Voto no dia 6 de outubro e toda essa política pública afeta os nossos Pets afeta os animais abandonados e os vítimas de maus tratos Então isso é nosso dia a dia e a gente quer saber como solucionar essas questões Então hoje eu tô aqui com o Bruno Lessa e eu quero que você se apresente por favor te do as boas vindas ao Niterói Dog Best Friend obrigada por tá aqui"

            Leia a transcrição e cumpra os pedidos do prompt sobre a mesma, retornando apenas o resultado final, sem negrito nas mudanças ou qualquer formatação de texto.
        """
    )
}
