"""adiciona morfologia/fermentador e popula taxonomia dos microrganismos

Revision ID: 0012_add_taxonomia_micro
Revises: 0011_add_sem_antibiograma
Create Date: 2026-08-07

Contexto: o catálogo de microrganismos já tinha os campos `gram`/`tipo`/
`familia`/`relevancia_clinica`, mas nenhum registro estava com esses dados
realmente preenchidos. Esta migration adiciona `morfologia` (novo enum) e
`fermentador` (só relevante pra bacilos Gram-negativos) e faz o
UPSERT (por `nome`, que já é `unique`) da taxonomia validada pelo
biomédico responsável pelo laboratório: os 10 microrganismos já
cadastrados recebem UPDATE só dos campos novos, e mais 21 espécies novas
são inseridas completas. Dado de conhecimento clínico - não alterar
valores sem validação do usuário do sistema.
"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
# OBS: mantenha o revision id com no máximo 32 caracteres - é o tamanho da
# coluna alembic_version.version_num criada pela migration inicial (ver
# 0001_create_pacientes.py), e um ID mais longo quebra o "alembic upgrade".
revision: str = "0012_add_taxonomia_micro"
down_revision: Union[str, None] = "0011_add_sem_antibiograma"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MORFOLOGIA_ENUM = sa.Enum(
    "COCO", "BACILO", "COCOBACILO", "LEVEDURA", "NAO_SE_APLICA",
    name="morfologia_enum",
)

# nome | gram | tipo | morfologia | fermentador | familia | relevancia_clinica
# Fonte: taxonomia/morfologia validada pelo biomédico responsável pelo
# laboratório para os microrganismos que aparecem na rotina de exames.
# Nenhuma regra de fenótipo de resistência (MRSA/ESBL/MDR/CRE/VRE) é
# aplicada aqui - só taxonomia/morfologia.
TAXONOMIA = [
    ("Staphylococcus aureus", "POSITIVO", "BACTERIA", "COCO", None,
     "Staphylococcaceae",
     "Coagulase-positiva. Alvo do rastreio de MRSA (resistência à "
     "oxacilina/cefoxitina)."),
    ("Staphylococcus haemolyticus", "POSITIVO", "BACTERIA", "COCO", None,
     "Staphylococcaceae",
     "Estafilococo coagulase-negativa (CoNS). Uma das CoNS mais relevantes "
     "em infecção de corrente sanguínea; perfil de resistência costuma ser "
     "mais elevado que as demais CoNS."),
    ("Staphylococcus epidermidis", "POSITIVO", "BACTERIA", "COCO", None,
     "Staphylococcaceae",
     "CoNS mais comum - maior contaminante de hemocultura, mas também "
     "principal causa de infecção relacionada a cateter/prótese. Avaliar "
     "contexto clínico."),
    ("Staphylococcus capitis", "POSITIVO", "BACTERIA", "COCO", None,
     "Staphylococcaceae",
     "CoNS associada a infecções de dispositivo em UTI neonatal. Existe "
     "clone descrito (NRCS-A) com heterorresistência à vancomicina."),
    ("Staphylococcus hominis", "POSITIVO", "BACTERIA", "COCO", None,
     "Staphylococcaceae",
     "CoNS de baixa virulência, flora normal de pele."),
    ("Staphylococcus saprophyticus", "POSITIVO", "BACTERIA", "COCO", None,
     "Staphylococcaceae",
     "CoNS, mas exceção do grupo: patógeno verdadeiro em urina (ITU em "
     "mulher jovem) - não tratar como contaminante nesse material."),
    ("Micrococcus luteus", "POSITIVO", "BACTERIA", "COCO", None,
     "Micrococcaceae",
     "Baixa virulência, geralmente flora de pele/contaminante; pode ser "
     "patógeno real em imunossuprimido."),
    ("Streptococcus agalactiae", "POSITIVO", "BACTERIA", "COCO", None,
     "Streptococcaceae",
     "Estreptococo do grupo B. Rastreio em gestante, sepse neonatal."),
    ("Streptococcus pyogenes", "POSITIVO", "BACTERIA", "COCO", None,
     "Streptococcaceae",
     "Estreptococo do grupo A. Faringite, infecções de pele/tecidos moles "
     "graves."),
    ("Streptococcus pneumoniae", "POSITIVO", "BACTERIA", "COCO", None,
     "Streptococcaceae", "Pneumonia, meningite, otite."),
    ("Streptococcus viridans (grupo)", "POSITIVO", "BACTERIA", "COCO", None,
     "Streptococcaceae",
     "Grupo heterogêneo, flora oral; relevante em endocardite."),
    ("Enterococcus faecalis", "POSITIVO", "BACTERIA", "COCO", None,
     "Enterococcaceae", "Espécie mais comum do gênero."),
    ("Enterococcus faecium", "POSITIVO", "BACTERIA", "COCO", None,
     "Enterococcaceae",
     "Mais associado a VRE (resistência à vancomicina) - prioridade de "
     "vigilância."),
    ("Dietzia timorensis", "POSITIVO", "BACTERIA", "BACILO", None,
     "Dietziaceae",
     "Rara, ambiental/oportunista. Pouca literatura clínica disponível."),
    ("Escherichia coli", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Enterobacteriaceae",
     "Enterobacterales mais comum - principal causa de ITU."),
    ("Klebsiella pneumoniae", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Enterobacteriaceae", "Alvo principal de vigilância de ESBL e CRE."),
    ("Klebsiella oxytoca", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Enterobacteriaceae",
     "Produz enzima cromossômica própria (K1) que pode gerar falso "
     "positivo no rastreio de ESBL."),
    ("Proteus mirabilis", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Morganellaceae",
     "Urease positiva (\"swarming\" em placa); comum em ITU."),
    ("Proteus vulgaris", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Morganellaceae",
     "Urease positiva, perfil de resistência intrínseca mais amplo que P. "
     "mirabilis (resistente a ampicilina/cefalosporinas de 1ª geração)."),
    ("Enterobacter hormaechei ssp hormaechei", "NEGATIVO", "BACTERIA",
     "BACILO", True, "Enterobacteriaceae",
     "Complexo E. cloacae - AmpC cromossômico induzível: cuidado mesmo com "
     "cefalosporina sensível in vitro."),
    ("Morganella morganii", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Morganellaceae",
     "AmpC cromossômico induzível, mesmo grupo de risco do "
     "Enterobacter/Serratia/Citrobacter."),
    ("Serratia marcescens", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Yersiniaceae",
     "AmpC cromossômico induzível; historicamente associada a surtos "
     "hospitalares."),
    ("Citrobacter freundii", "NEGATIVO", "BACTERIA", "BACILO", True,
     "Enterobacteriaceae", "AmpC cromossômico induzível."),
    ("Pseudomonas aeruginosa", "NEGATIVO", "BACTERIA", "BACILO", False,
     "Pseudomonadaceae",
     "Não-fermentador. Alta prioridade de vigilância MDR."),
    ("Pseudomonas stutzeri", "NEGATIVO", "BACTERIA", "BACILO", False,
     "Pseudomonadaceae",
     "Não-fermentador, bem menos virulenta que P. aeruginosa, geralmente "
     "ambiental."),
    ("Acinetobacter baumannii", "NEGATIVO", "BACTERIA", "COCOBACILO", False,
     "Moraxellaceae",
     "Não-fermentador. Um dos principais organismos MDR/XDR de UTI."),
    ("Stenotrophomonas maltophilia", "NEGATIVO", "BACTERIA", "BACILO",
     False, "Xanthomonadaceae",
     "Não-fermentador. Resistência intrínseca a carbapenêmico - "
     "resistência a meropenem é esperada, não deve ser tratada como alarme "
     "de MDR isolado."),
    ("Haemophilus influenzae", "NEGATIVO", "BACTERIA", "COCOBACILO", None,
     "Pasteurellaceae",
     "Cocobacilo Gram-negativo fastidioso - exige meio especial (ágar "
     "chocolate). Patógeno respiratório."),
    ("Candida albicans", "NAO_SE_APLICA", "FUNGO", "LEVEDURA", None,
     "Debaryomycetaceae", None),
    ("Candida duobushaemulonis", "NAO_SE_APLICA", "FUNGO", "LEVEDURA", None,
     "Debaryomycetaceae",
     "Complexo C. haemulonii (mesmo grupo do C. auris) - resistência "
     "reduzida a azólicos é comum; considerar teste de suscetibilidade a "
     "equinocandina."),
    ("Rhodotorula mucilaginosa", "NAO_SE_APLICA", "FUNGO", "LEVEDURA", None,
     "Sporidiobolaceae",
     "Resistência intrínseca a equinocandinas e sensibilidade reduzida a "
     "fluconazol - oportunista emergente, geralmente relacionado a "
     "cateter."),
]

UPSERT_SQL = sa.text(
    """
    INSERT INTO microrganismos
        (id, nome, gram, tipo, morfologia, fermentador, familia,
         relevancia_clinica, is_active, created_at, updated_at)
    VALUES
        (:id, :nome, :gram, :tipo, :morfologia, :fermentador, :familia,
         :relevancia_clinica, true, now(), now())
    ON CONFLICT (nome) DO UPDATE SET
        gram = EXCLUDED.gram,
        tipo = EXCLUDED.tipo,
        morfologia = EXCLUDED.morfologia,
        fermentador = EXCLUDED.fermentador,
        familia = EXCLUDED.familia,
        relevancia_clinica = EXCLUDED.relevancia_clinica,
        updated_at = now()
    """
)


def upgrade() -> None:
    MORFOLOGIA_ENUM.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "microrganismos",
        sa.Column(
            "morfologia",
            MORFOLOGIA_ENUM,
            nullable=False,
            server_default="NAO_SE_APLICA",
        ),
    )
    op.add_column(
        "microrganismos",
        sa.Column("fermentador", sa.Boolean(), nullable=True),
    )

    bind = op.get_bind()
    for nome, gram, tipo, morfologia, fermentador, familia, relevancia in TAXONOMIA:
        bind.execute(
            UPSERT_SQL,
            {
                "id": str(uuid.uuid4()),
                "nome": nome,
                "gram": gram,
                "tipo": tipo,
                "morfologia": morfologia,
                "fermentador": fermentador,
                "familia": familia,
                "relevancia_clinica": relevancia,
            },
        )


def downgrade() -> None:
    # A migration de dados (upsert de taxonomia) não é revertida no
    # downgrade - só a estrutura das colunas/enum novos, seguindo o padrão
    # já usado nas demais migrations deste projeto.
    op.drop_column("microrganismos", "fermentador")
    op.drop_column("microrganismos", "morfologia")
    MORFOLOGIA_ENUM.drop(op.get_bind(), checkfirst=True)
