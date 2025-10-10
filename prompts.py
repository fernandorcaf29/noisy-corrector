prompt_model_map = {
    "mistral-large-latest": lambda transcription: (
        "REVISÃO DE TEXTO GERADO POR RECONHECIMENTO AUTOMÁTICO DE FALA\n"
        
        "CORRIGIR APENAS:\n"
        "* Pseudopalavras;\n"
        "* Erros fonéticos.\n\n"
        
        "PRESERVAR DA TRANSCRIÇÃO ORIGINAL:\n"
        "* Linguagem informal;\n"
        "* Ordem das palavras;\n"
        "* Flexões linguísticas (mesmo que soem estranhas);\n"
        "* Marcas de oralidade;\n"
        '* Repetição de palavras e gaguejamento (Ex:"um uma", "essa essa", "área uma área","pr pra");\n'
        "* Girias e estrangeirismos.\n\n"

        "PRESERVAR DA PALAVRA ORIGINAL:\n"
        "* Capitalização;\n"
        "* Flexão de gênero;\n"
        "* Flexão de número;\n"
        "* Conjugação.\n"
        
        "NUNCA:\n"
        "* Alterar DELIMITADORES NUMÉRICOS (Ex:'5.8', '1,5', 'R 400');\n"
        "* Gerar palavras adjacentes as corrigidas ou em elipses;\n"
        "* Trocar 'de reais' por 'R$' e casos equivalentes;\n"
        "* Rearranjar a estrutura frasal original;\n"
        "* Usar uppercase em palavras que não sejam nomes próprios;\n"
        "* Remover repetições das palavras, mesmo se uma delas tiver erro fonético.\n\n"
        
        "PARA FRASES CURTAS (< 5 palavras):\n"
        "* Só corrija se houver evidente erro de digitação;\n"
        "* Mantenha inalterado caso contrário.\n\n"

        "TRANSCRIÇÃO PODE SER UMA UNICA PALAVRA.\n\n"

        "Responda apenas com a transcrição corrigida, sem pontuação.\n\n"
        
        "TRANSCRIÇÃO ORIGINAL:\n"
        f"{transcription}"
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
