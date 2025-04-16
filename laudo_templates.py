# laudo_templates.py
# Módulo com textos-base dos diversos modelos de laudo, usando placeholders {nome} e {data}

LAUDOS = {
    # Transtorno do Espectro Autista + TDAH
    "TEA_TDAH": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de distúrbio de comportamento, dificuldade na socialização, caracterizado por transtorno do espectro autista e Transtorno de Déficit de Atenção e Hiperatividade (TDAH), devendo ser considerado especial conforme a legislação.

Necessita de acompanhamento com equipe multidisciplinar composta por:
- Psicóloga: 1x/semana
- Terapeuta Ocupacional: 2x/semana
- Psicopedagoga: 2x/semana
- Cuidador(a) para auxiliar na inclusão educacional

CID-10: F84.0; F90
CID-11: 6A02; 6A05.0

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # TEA com convulsão
    "TEA_CONVULSAO": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de distúrbio de comportamento e seletividade alimentar severa, caracterizado por Transtorno do Espectro Autista, associado a convulsão, devendo ser considerado especial conforme a legislação.

Necessita de acompanhamento com equipe multidisciplinar composta por:
- Psicóloga: 1x/semana
- Terapeuta Ocupacional: 2x/semana
- Fonoaudióloga: 2x/semana
- Cuidador(a) itinerante para inclusão educacional

CID-10: F84.0; G40
CID-11: 6A02

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # TEA com itinerante (ecolalia)
    "TEA_ITINERANTE": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de distúrbio de comportamento e atraso na fala (ecolalia), caracterizado por Transtorno do Espectro Autista, devendo ser considerado especial conforme a legislação.

Necessita de acompanhamento com equipe multidisciplinar composta por:
- Psicóloga: 1x/semana
- Terapeuta Ocupacional: 2x/semana
- Fonoaudióloga: 2x/semana
- Cuidador(a) para inclusão educacional

CID-10: F84.0
CID-11: 6A02

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # TEA com curatela
    "TEA_CURATELA": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de distúrbio de comportamento e atraso na fala (ecolalia), caracterizado por Transtorno do Espectro Autista com incapacidade cognitiva severa e sem previsão de alta, devendo ser considerado especial conforme a legislação.

A genitora deverá ter curatela para fins judiciais.

Necessita de acompanhamento com equipe multidisciplinar composta por:
- Psicóloga: 1x/semana
- Terapeuta Ocupacional: 2x/semana
- Fonoaudióloga: 2x/semana
- Cuidador(a) para inclusão educacional

CID-10: F84.0
CID-11: 6A02

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # TDAH simples
    "TDAH": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de Transtorno de Déficit de Atenção e Hiperatividade (TDAH), com funções cognitivas preservadas, porém desatenção e impulsividade.

Deverá ser incluído(a) em escola regular conforme lei de inclusão.

Direitos:
- Permanecer na primeira fila
- Mais tempo para provas
- Trabalhos complementares

CID-10: F90
CID-11: 6A05.0

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # TDAH com traços autísticos
    "TDAH_AUTISTICOS": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de Transtorno de Déficit de Atenção e Hiperatividade (TDAH) com traços autísticos.

Deverá ser incluído(a) em escola regular conforme lei de inclusão.

Direitos:
- Permanecer na primeira fila
- Mais tempo para provas
- Trabalhos complementares

CID-10: F90
CID-11: 6A02

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # Paralisia cerebral
    "PARALISIA_CEREBRAL": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de microcefalia, paralisia cerebral e retardo mental, sem previsão de alta e com incapacidade laboral severa.

CID-10: G80

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # Atraso na socialização
    "ATRASO_SOCIALIZACAO": """
LAUDO MÉDICO

Paciente: {nome}

Paciente com atraso na socialização, fala e olhar mantidos, timidez e introversão; recomendado terapia com psicóloga.

CID-10: F98

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # Atraso mental
    "ATRASO_MENTAL": """
LAUDO MÉDICO

Paciente: {nome}

Paciente com comprometimento cognitivo, lentidão intelectual, repercussão funcional e traços do espectro autista, portador de convulsão; sem condições laborais.

CID-10: F70; G40; F84

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",

    # Agitação psicomotora
    "AGITACAO_PSICOMOTORA": """
LAUDO MÉDICO

Paciente: {nome}

Paciente portador(a) de agitação psicomotora com impulsividade; comunicação preservada.

Recomendado:
- Psicóloga
- Terapeuta Ocupacional
- Fonoaudióloga

CID-10: R45.1

Maracanaú, {data}

Dra. Gilma M. P. Holanda
CRM: 2374
""",
}
