# Roteiro de Teste — Kondo AI

## Pré-requisitos

Certifique-se que backend e frontend estão rodando:

**Terminal 1 — backend:**

```bash
cd kondo
uv run uvicorn app.main:app --reload
# → http://localhost:8000
```

**Terminal 2 — frontend:**

```bash
cd kondo-front
bun run dev
# → http://localhost:5173
```

---

## Usuários demo

Senha universal: `kondo123`

| Perfil | E-mail | Acesso |
|---|---|---|
| Síndico | `sindico@kondo.com` | Dashboard completo, chamados, financeiro, IA |
| Conselho | `conselho@kondo.com` | Financeiro, documentos, governança |
| Morador | `morador@kondo.com` | Portal da unidade, chamados, boletos |

---

## Cenário 1 — Síndico: Dashboard e prioridades da IA

**Login:** `sindico@kondo.com` / `kondo123`

1. Acesse `http://localhost:5173/login` e entre com as credenciais acima.
2. Você deve cair no dashboard do síndico automaticamente.
3. Verificar:
   - Saldo atual do mês visível.
   - Alerta de caixa projetado negativo (impacto da inadimplência).
   - Contador de chamados críticos — esperado: 2.
   - Contador de inadimplentes — esperado: 6 unidades.
   - Painel de IA com sugestões de prioridades do dia.

**Mensagem esperada da IA:**
> "Com a inadimplência atual, o caixa pode ficar negativo no próximo mês."

---

## Cenário 2 — Síndico: Simulação de acordo de inadimplência

Ainda logado como síndico:

1. Navegue até **Financeiro → Inadimplência**.
2. Localize a **Unidade 304** — R$ 1.548 em aberto, 63 dias de atraso.
3. Clique em **Simular Acordo**.
4. Preencha:
   - Entrada: `R$ 400`
   - Parcelas: `4`
5. Verificar:
   - IA calcula o valor das parcelas automaticamente.
   - Sistema mostra impacto no caixa projetado.
   - Sugestão da IA aparece como "condição segura para o condomínio".

---

## Cenário 3 — Morador: Abertura de chamado crítico

**Logout → Login:** `morador@kondo.com` / `kondo123`

1. Acesse o **Portal do Morador** (Unidade 804).
2. Clique em **Novo Chamado**.
3. Preencha:
   - **Título:** `Vazamento na garagem`
   - **Descrição:** `Vazamento forte na garagem B2 perto do quadro elétrico.`
   - **Local:** `Garagem B2`
4. Submeta o chamado.
5. Verificar resposta da IA:
   - Categoria classificada: **Hidráulica**
   - Prioridade: **Alta**
   - Risco detectado: **Elétrico**
   - Ação sugerida: isolar área e chamar fornecedor.

---

## Cenário 4 — Síndico: Acompanhamento do chamado no Kanban

**Logout → Login:** `sindico@kondo.com` / `kondo123`

1. Navegue até **Chamados** (ou Kanban).
2. Localize o chamado "Vazamento na garagem" recém-criado.
3. Verificar:
   - Chamado aparece na coluna `received` ou `in_review`.
   - Classificação da IA visível — categoria, prioridade, risco.
4. Avance o status para **`vendor_contacted`**.
5. Confirmar que o status muda corretamente no board.

---

## Cenário 5 — Síndico: Geração de comunicado via IA

Ainda logado como síndico:

1. Navegue até **Comunicados → Novo Comunicado**.
2. No campo de rascunho, escreva:
   > `Garagem B2 em manutenção emergencial, área perto do quadro elétrico isolada.`
3. Escolha o tom: **Urgente**.
4. Clique em **Gerar com IA**.
5. Verificar:
   - IA expande o rascunho em comunicado formal e estruturado.
   - Texto menciona isolamento da área e previsão de retorno.
6. Clique em **Publicar**.

---

## Cenário 6 — Morador: Acompanhamento e consulta ao regimento

**Logout → Login:** `morador@kondo.com` / `kondo123`

1. Vá em **Meus Chamados**.
2. Verificar que o chamado de vazamento aparece com status atualizado.
3. Acesse **Kondo IA** (chat).
4. Pergunte: `Posso fazer obra no sábado?`
5. Verificar:
   - IA responde com base no regimento cadastrado.
   - Para dúvida sensível ou jurídica, orienta consultar o síndico.

---

## Cenário 7 — Conselho: Transparência financeira

**Logout → Login:** `conselho@kondo.com` / `kondo123`

1. Acesse o **Painel do Conselho**.
2. Verificar:
   - Receitas, despesas e inadimplência do mês visíveis.
   - Caixa projetado com variações explicadas pela IA em linguagem simples.
   - Acesso a documentos — atas, regimento.
   - Opções de gestão operacional **não aparecem** (exclusivas do síndico).

---

## Pontos de atenção

- **Fallback de IA:** sem `OPENAI_API_KEY` no `.env`, a IA usa respostas simuladas — comportamento esperado.
- **Indicador de mock:** o frontend exibe um badge visual quando os dados são mock (backend desconectado).
- **Kanban:** ao criar qualquer chamado, um `WorkItem` deve ser criado automaticamente no board.
- **Financeiro:** todos os valores monetários devem aparecer com 2 casas decimais, sem arredondamento de float.
