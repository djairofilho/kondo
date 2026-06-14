# Roteiro de Vídeo — Kondo (2 minutos)

> **Objetivo:** mostrar o problema, apresentar a plataforma e terminar no Kondo AI executando ações reais.
> **Perfil de entrada:** síndico (`sindico@kondo.com` / `kondo123`).
> **Tempo total:** ~2 min — cada cena tem tempo estimado.

---

## Antes de gravar

- Backend rodando (`uv run uvicorn app.main:app --reload`)
- Frontend rodando (`bun run dev`)
- Banco com seed (`uv run python -m app.seed`)
- `ANTHROPIC_API_KEY` configurada no `.env` — **obrigatório para as tools funcionarem**
- Navegador em tela cheia, zoom 90%, sidebar aberta
- Abrir `/login` e já estar logado como **síndico** antes de apertar REC

---

## Cena 1 — Problema (0:00 – 0:12)

**Tela:** qualquer — pode ser um slide rápido ou a landing em `/landing`

**Fala:**
> "Condomínios ainda funcionam assim: chamados perdidos no WhatsApp, balancetes em PDF, inadimplência em planilha. O síndico reage. O conselho não enxerga. O morador não sabe o status de nada."

**O que mostrar:** se tiver a landing page, scrollar brevemente. Se não, corte direto para o dashboard.

---

## Cena 2 — Dashboard do síndico (0:12 – 0:28)

**Tela:** `/sindico`

**Ação:** entrar na tela, deixar carregar os cards.

**Fala:**
> "O Kondo centraliza tudo. O síndico abre o painel e já sabe o que precisa resolver hoje — chamados críticos, risco de caixa, prioridades geradas pela IA."

**O que mostrar:**
- Cards de ação rápida no topo (Criar comunicado, Revisar pagamento, Abrir chamado)
- Cards de status da central de decisão (chamados abertos, alerta de despesas)
- Painel "Copiloto IA do dia" com os próximos passos
- StatCards: Receitas previstas, Despesas do mês, Saldo previsto

> **Não clicar em nada ainda — só mostrar a tela carregada.**

---

## Cena 3 — Chamados e Kanban (0:28 – 0:42)

**Tela:** `/chamados`

**Ação:** navegar para Chamados pela sidebar.

**Fala:**
> "Cada chamado tem categoria, prioridade e próxima ação classificados pela IA automaticamente. O síndico arrasta o card entre as colunas do Kanban conforme o andamento."

**O que mostrar:**
- Kanban com as 6 colunas: Recebido → Em análise → Fornecedor → Aprovação → Execução → Resolvido
- Clicar em um chamado crítico para abrir o drawer lateral
- Mostrar o badge de prioridade, status e o texto de IA (`iaStatus`)
- **Opcional:** arrastar um card de coluna para demonstrar o drag-and-drop

> **Não precisa criar chamado aqui — isso vai acontecer via Kondo AI.**

---

## Cena 4 — Financeiro e inadimplência (0:42 – 0:58)

**Tela:** `/financeiro`

**Ação:** navegar para Financeiro.

**Fala:**
> "O financeiro mostra receitas, despesas e inadimplência em tempo real — com gráficos e simulador de acordo. A IA analisa as despesas e gera resumo pronto para o conselho."

**O que mostrar:**
- 4 StatCards: Receitas, Despesas, Saldo previsto, Inadimplência
- Gráfico de barras (visualização mensal)
- Clicar em **"Analisar"** no Radar IA de despesas — aguardar o texto gerado aparecer
- Rolar até a aba **Moradores** e mostrar a lista de inadimplentes com o simulador de acordo

> Dica: o Radar IA usa mock se não houver chave — mas fica claro o que ele faz.

---

## Cena 5 — Kondo AI (0:58 – 1:55) ← O CLÍMAX

**Tela:** `/kondo-ia`

**Ação:** clicar em **"Kondo AI"** na sidebar (ícone Sparkles).

**Fala de entrada:**
> "E aqui está o clímax do sistema: o Kondo AI. Em vez de navegar por telas, você conversa. E ele não só responde — ele age."

---

### Sequência de comandos — digitar um a um, aguardar resposta antes do próximo

---

#### Comando 1 — Contexto do dia (1:00 – 1:12)

**Digitar:**
```
Organiza meu dia. O que precisa de atenção agora?
```

**O que acontece:** o modelo lê o contexto real do condomínio (chamados críticos, caixa, inadimplência) e responde com prioridades.

**Fala durante a resposta:**
> "Ele lê os dados reais do condomínio e me diz onde focar."

---

#### Comando 2 — Abrir chamado (tool `abrir_chamado`) (1:12 – 1:28)

**Digitar:**
```
Abre um chamado de vazamento no corredor do bloco B, unidade 12. Descrição: água escorrendo pelo teto perto do quadro elétrico. Local: corredor térreo bloco B.
```

**O que acontece:**
1. O modelo chama a tool `abrir_chamado`
2. Na interface, aparece o chip da tool com ícone de chave (`🔧 abrir_chamado`)
3. A resposta confirma: `Chamado aberto (id=X): 'Vazamento no corredor do bloco B'...`
4. O chamado aparece no Kanban em tempo real

**Fala:**
> "Chamado criado direto no sistema — com WorkItem no Kanban. Sem abrir outra tela, sem formulário."

> ⚠️ **Atenção:** precisa de `unit_id` válido. Use `unit_id: 1` se não souber o ID correto nos dados demo. A mensagem acima já inclui `unidade 12` — o modelo vai pedir ou inferir.

---

#### Comando 3 — Registrar despesa (tool `adicionar_despesa`) (1:28 – 1:42)

**Digitar:**
```
Registra uma despesa de manutenção do portão eletrônico. Categoria manutenção, valor R$ 850, vencimento 2026-07-15.
```

**O que acontece:**
1. Valor está abaixo de R$ 5.000 → **não pede confirmação**
2. Tool `adicionar_despesa` é chamada
3. Aparece chip da tool na mensagem
4. Resposta confirma: `Despesa registrada (id=X): 'Manutenção do portão eletrônico', categoria 'manutencao', R$ 850,00, vencimento 15/07/2026.`

**Fala:**
> "Despesa lançada no financeiro. Auditada, rastreada, sem precisar abrir outra aba."

---

#### Comando 4 — Criar e publicar comunicado (tool `criar_comunicado`) (1:42 – 1:55)

**Digitar:**
```
Cria um comunicado para os moradores informando que a garagem B estará interditada amanhã das 8h às 18h por manutenção hidráulica. Publica agora.
```

**O que acontece:**
1. Publicação imediata **requer confirmação explícita** — o modelo vai responder pedindo confirmação
2. Digitar em seguida:
```
Confirmo, pode publicar.
```
3. Tool `criar_comunicado` é chamada com `publicar: true`
4. Chip da tool aparece: `🔧 criar_comunicado`
5. Resposta confirma: `Comunicado publicado (id=X): 'Garagem B - Manutenção Hidráulica', audiência 'residents'.`

**Fala durante a confirmação:**
> "Para publicar imediatamente, ele pede confirmação. Nada sensível é executado sem o síndico confirmar."

**Fala após publicação:**
> "Comunicado publicado. Moradores já visualizam no portal deles."

---

## Cena 6 — Fechamento (1:55 – 2:00)

**Tela:** permanecer no `/kondo-ia` com as mensagens na tela

**Fala:**
> "Kondo começa resolvendo o dia a dia do síndico. Com os dados de operação e caixa que acumula, evolui para infraestrutura de crédito para condomínios."

---

## Resumo visual das cenas

| # | Tela | Tempo | O que mostrar |
|---|---|---|---|
| 1 | Landing ou narração | 0:00–0:12 | Problema |
| 2 | `/sindico` | 0:12–0:28 | Dashboard, prioridades IA, métricas |
| 3 | `/chamados` | 0:28–0:42 | Kanban, chamado crítico, drag-and-drop |
| 4 | `/financeiro` | 0:42–0:58 | Métricas, gráfico, Radar IA, inadimplência |
| 5 | `/kondo-ia` | 0:58–1:55 | **4 comandos com tools reais** |
| 6 | `/kondo-ia` | 1:55–2:00 | Fechamento |

---

## Comandos do Kondo AI em ordem (copiar e colar durante gravação)

```
1. Organiza meu dia. O que precisa de atenção agora?
```

```
2. Abre um chamado de vazamento no corredor do bloco B, unidade 12. Descrição: água escorrendo pelo teto perto do quadro elétrico. Local: corredor térreo bloco B.
```

```
3. Registra uma despesa de manutenção do portão eletrônico. Categoria manutenção, valor R$ 850, vencimento 2026-07-15.
```

```
4. Cria um comunicado para os moradores informando que a garagem B estará interditada amanhã das 8h às 18h por manutenção hidráulica. Publica agora.
```

```
5. (confirmação) Confirmo, pode publicar.
```

---

## O que mostrar em cada tool

| Tool chamada | Onde aparece na UI | O que falar |
|---|---|---|
| `abrir_chamado` | Chip `🔧 abrir_chamado` + texto de confirmação | "Chamado criado direto no Kanban" |
| `adicionar_despesa` | Chip `🔧 adicionar_despesa` + confirmação com id | "Lançamento financeiro sem abrir outra tela" |
| `criar_comunicado` | Pedido de confirmação + chip após confirmar | "Guardrail: ele pediu confirmação antes de publicar" |

---

## Fallbacks se algo der errado

| Problema | Solução rápida |
|---|---|
| Tool não aparece (sem chave) | Mostrar o fallback e explicar que sem chave a resposta é simulada — o fluxo é o mesmo |
| `unit_id` inválido no chamado | Resposta da tool vai dizer "Unidade não encontrada" — digitar novamente com `unit_id: 1` |
| Timeout do modelo | Refrescar e tentar o comando mais curto: `"Abre chamado de vazamento, bloco B, local corredor térreo."` |
| Confirmação não reconhecida | Digitar exatamente: `Confirmo, pode executar.` |
