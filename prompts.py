prompt_model_map = {
    "mistral-large-latest": lambda transcription: (
        "DIRETRIZES PRINCIPAIS:\n"
        "1. PRESERVE a fala original INTEGRALMENTE\n"
        "2. REVISE APENAS erros CLAROS e INEQUÍVOCOS de reconhecimento\n"
        "3. EM DÚVIDA, NÃO altere NADA\n\n"

        "CASOS ESPECÍFICOS PARA CORREÇÃO:\n"
        "* Palavras INEXISTENTES no português (ex: 'netero' → 'niteroienses')\n"
        "* Siglas OFICIAIS de instituições (ex: 'uf' → 'UFF')\n"
        "* Nomes de marcas/redes com grafia OFICIAL (ex: 'tiktok' → 'TikTok')\n"
        "* Palavras com significado claro a partir do contexto (ex: 'Aras' → 'haras' quando cavalos são mencionados, 'cin' → 'CLIN' quando no contexto de recolhimento de lixo)\n"
        "* APENAS quando houver EVIDÊNCIA CLARA do correto\n\n"

        "CASOS ESPECÍFICOS PARA PRESERVAÇÃO:\n"
        "* Pronúncia como transcrita ('te do', 'tá', 'né', 'eh')\n"
        "* TODAS repetições ('para esse esse', 'e eh', 'pras', 'uma')\n"
        "* Estrutura FRASAL COMPLETA (não altere ordem ou palavras)\n"
        "* Formatação NUMÉRICA EXATA (5.8, R5, 'de reais' - não adicione R$)\n"
        "* Nomes próprios COMO TRANSCRITOS ('Emusa', 'Aras', 'cin')\n"
        "* Hífens e pontuação COMO ESTÃO NO ORIGINAL (ex: 'maus-tratos')\n"
        "* Número gramatical ORIGINAL (singular/plural)\n\n"

        "PROIBIÇÕES ABSOLUTAS:\n"
        "* NÃO adicione, remova ou altere palavras, a menos que seja um dos casos específicos de correção\n"
        "* NÃO altere ordem das palavras ou estrutura frasal\n"
        "* NÃO modifique formatação numérica/monetária (preserve 'de reais', não adicione R$ ou R)\n"
        "* NÃO adicione pontuação ou símbolos\n"
        "* NÃO corrija repetições, hesitações ou oralidade\n"
        "* NÃO tente deduzir contextos, a menos que seja um dos casos específicos de correção\n\n"

        "REGRA FINAL: Se não for um dos casos específicos de correção, PRESERVE.\n\n"

        "Retorne apenas a transcrição revisada.\n\n"

        "TRANSCRIÇÃO ORIGINAL:\n\n"

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
    "header":(
        "Você é revisor especializado em transcrições ASR contextualizadas no Brasil."
    ),
}
