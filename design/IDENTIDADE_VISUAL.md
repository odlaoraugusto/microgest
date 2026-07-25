# Identidade Visual do MicroGest

Fonte oficial: `Guia_de_Identidade_Visual_MicroGest_Fase1.png` (Design System - Fase 1).
Este arquivo consolida as regras que o frontend (`frontend/src/styles/tokens.css`)
segue à risca. Sempre que o guia evoluir, atualizar os dois lugares juntos.

## Paleta de cores

| Uso | Cor | Hex |
|---|---|---|
| Primária | Azul | `#0F4C81` |
| Secundária | Verde | `#2E8B57` |
| Fundo | Branco-gelo | `#F8FAFC` |
| Texto | Grafite | `#1F2937` |
| Sucesso | Verde | `#22C55E` |
| Alerta | Laranja | `#F59E0B` |
| Erro | Vermelho | `#DC2626` |
| Informação | Azul | `#3B82F6` |
| Neutro | Roxo-azulado | `#6366F1` |
| Neutro Claro | Cinza | `#E5E7EB` |

## Tipografia

Família: **Poppins** (pesos Bold, SemiBold, Medium, Regular, Light).
Carregada via Google Fonts em `frontend/index.html` e aplicada globalmente
em `frontend/src/styles/global.css` através da variável `--mg-font-family`.

## Logomarca

**Fonte oficial:** vetores reais fornecidos pelo usuário (extraídos/traçados
do manual de identidade visual), em `design/icons/`:

- `simbolo.svg` — símbolo principal, colorido (navy + verde), fundo
  transparente. Fonte de verdade do favicon e do componente React
  `MicroGestIcon` (variante `colorido`, padrão). Usar sobre fundos claros.
- `simbolo-negativo.svg` — símbolo branco sobre fundo navy em quadrado
  arredondado (200×200, já com o próprio fundo embutido). Usado nos ícones
  de aplicação (Android/iOS/Windows) e no componente `MicroGestIcon`
  (variante `negativo`) para superfícies escuras, como a sidebar.
- `simbolo-mono.svg` — variação em contorno único (grafite `#1F2937`),
  para impressão P&B.
- `logo-horizontal.svg` — lockup completo: símbolo + wordmark "MicroGest"
  (traçado como vetor) + tagline "Gestão em Microbiologia." em Poppins.
  Disponível como referência/asset de marca; ainda não usado ao vivo na
  interface porque o `<img>` externo não tem acesso às fontes web
  carregadas pela página (a tag `<text>` cairia para a fonte fallback do
  sistema em vez de Poppins). Para usar com a fonte garantida, inlinar o
  SVG diretamente no JSX/DOM em vez de referenciar via `<img src>`.
- `variacoes.svg` — grade de referência com as variações lado a lado
  (mantido apenas como documentação visual).

As cores desses vetores foram ajustadas para baterem exatamente com os hex
oficiais da paleta (o traçado original trouxe `#00426F`/`#1B8A57`, muito
próximos mas não idênticos a `#0F4C81`/`#2E8B57` — provavelmente por
amostragem de pixels com anti-aliasing durante a vetorização).

Onde a marca aparece hoje no sistema:

- Favicon do navegador (`frontend/public/favicon.svg`, a partir de `simbolo.svg`)
- Ícones de instalação do app (`apple-touch-icon.png`,
  `android-chrome-*.png`, `mstile-256x256.png`, a partir de
  `simbolo-negativo.svg`, referenciados em `site.webmanifest`/`index.html`)
- Sidebar (`MicroGestIcon variante="negativo"`) e tela de Login
  (`MicroGestIcon variante="colorido"`)
- Cabeçalho do relatório PDF da CCIH (`backend/app/assets/logo.png`,
  gerado a partir de `simbolo.svg`)

- Redução mínima: 24px / 8mm - nunca usar o símbolo abaixo disso.
- Variações: colorida (padrão), negativa (fundo escuro), monocromática e
  monocromática negativa (usos institucionais/impressão P&B).

## Área de proteção e usos incorretos

- Respeitar a área de proteção ao redor do logo (não encostar texto/bordas).
- Não alterar as cores oficiais.
- Não distorcer as proporções.
- Não aplicar sombras.
- Não usar contornos adicionais.
- Não alterar a tipografia do nome da marca.
- Não aplicar a logo sobre fundos de baixo contraste ou imagens.

## Ícones de aplicação

- Ícone do app (Android): 192x192px
- Ícone do app (iOS): 180x180px
- Ícone de página (favicon): 32x32px
- Ícone de atalho (Windows): 256x256px

Esses tamanhos devem ser gerados a partir do símbolo isolado (ícone) em
`design/` quando o app for empacotado/distribuído.

## Missão, visão e valores (contexto de produto)

- **Missão:** transformar dados microbiológicos em informações confiáveis
  para promover qualidade e segurança na saúde.
- **Visão:** ser referência em gestão laboratorial inteligente na América
  Latina.
- **Valores:** precisão, integração, inovação, transparência, segurança e
  compromisso com a vida.

Esses princípios orientam decisões de produto (ex.: por que o módulo CCIH
e a "IA silenciosa" do dashboard são prioridade desde a v1.0).
