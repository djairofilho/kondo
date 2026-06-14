# Checklist de Revisão do Kondo (Backend + Docs)

Este checklist organiza a revisão enquanto aguardamos o frontend.

Status: `pendente` até fechamento de cada item.

## 1) Escopo do Produto (coerencia com a tese)

### O que esta pronto

- Painel, chamados e Kanban implementados.
- Estrutura financeira básica (resumo, receitas, despesas, pagamentos, inadimplência, acordos).
- Documentos, comunicados e anexos implementados.
- Entrega de IA simulada (classificação, resumo, recomendação e comparação).

### Pontos de revisão

- Confirmar no frontend o fluxo de "múltiplas pessoas por condomínio" em todas as telas.
- Confirmar UX para "chamado + anexos (foto)" no portal do morador.
- Confirmar que WhatsApp entra como roadmap apenas e não como bloqueante de MVP.

Responsável: Produto

Prioridade: P1

### Regra de aceitação

- Cada caso de uso prioritario em [use-cases](use-cases.md) precisa ter pelo menos uma tela planejada no frontend e um endpoint funcional no backend.

## 2) Papéis e permissões

### Achados críticos

1. Apenas endpoints da rota `/admin` exigem `platform_admin`.
   - Arquivos: [app/core/deps.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\core\deps.py), [app/routers/admin.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\routers\admin.py)
   - Risco: operações de condomínio, financeiro, chamados e anexos estão abertas para qualquer token válido.
   - Prioridade: P0
   - Mitigação:
     - aplicar `require_roles("platform_admin")`, `require_roles("manager")`, `require_roles("board_member")` e `require_roles("resident")` por domínio;
     - incluir checagem de associação ao condomínio no serviço;
     - registrar erros de autorização em `audit_events`.

2. `get_current_user` pode retornar token válido mesmo fora do escopo do condomínio.
   - Arquivo: [app/routers/auth.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\routers\auth.py)
   - Risco: ausência de “escopo de condomínio” por endpoint.
   - Prioridade: P1
   - Mitigação:
     - criar helper de contexto de acesso no condomínio;
     - exigir `condominium_id` no token de sessão do usuário ativo ou na rota principal.

3. Endpoints de `residents/portal` aceitam dados de unidade via query (`unit_id`) não derivada do login.
   - Arquivo: [app/routers/experiences.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\routers\experiences.py)
   - Risco: usuário visualizar/acionar dados de outra unidade ao manipular o parâmetro.
   - Prioridade: P1
   - Mitigação:
     - resolver unidade via `current_user` + `memberships`;
     - manter parâmetro de unidade apenas administrativo (manager/board).

4. Criação de comentários em chamado permite `author_user_id` livre no payload.
   - Arquivo: [app/schemas/tickets.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\schemas\tickets.py), [app/routers/tickets.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\routers\tickets.py)
   - Risco: spoofing de autor.
   - Prioridade: P1
   - Mitigação:
     - derivar autor do token e ignorar campo no payload.

## 3) Contrato API x Implementacao

### Achados

1. `POST /documents/{id}/summarize` e `POST /documents/{id}/ask` esperam apenas `document_id`, mas internamente não recebem `document_id` como parâmetro obrigatório do contrato de request body em serviços simulados.
   - Arquivos: [app/routers/documents.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\routers\documents.py), [app/routers/ai.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\routers\ai.py)
   - Risco: integração front-end pode conflitar no payload e no contrato de validação.
   - Prioridade: P2
   - Mitigação:
     - padronizar contratos com pydantic e garantir retorno de estrutura única de erro.

2. `/board/overview` e `/board/dashboard` estão retornando a mesma estrutura.
   - Arquivo: [app/routers/experiences.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\routers\experiences.py)
   - Risco: telas com expectativa diferente podem ficar redundantes.
   - Prioridade: P2
   - Mitigação:
     - separar finalidade dos dois endpoints ou documentar que são equivalentes temporariamente.

3. Muitos endpoints de escrita não têm paginação, filtros nem versionamento.
   - Arquivos: `app/routers/*`
   - Risco: performance e evolução quebram cedo.
   - Prioridade: P2
   - Mitigação:
     - definir padrão `limit/offset`, `page`, `sort` para listagens críticas.

4. Falta de códigos de erro padronizados para conflitos (422,409) e duplicidade.
   - Arquivos: serviços de domínio.
   - Prioridade: P3

## 4) Dados e domínio

### Achados

1. `finance_summary` calcula caixa projetado como `received_revenue - expenses`, sem considerar:
   - parcelamentos por acordo,
   - pagamentos futuros em aberto,
   - status de receita/pagamento em revisão.
   - Arquivo: [app/services/finance_service.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\services\finance_service.py)
   - Prioridade: P2

2. `get_finance_summary` suporta `db=None` com valores fixos (fallback de demo).
   - Arquivo: mesmo
   - Risco: comportamento divergente entre ambiente teste e produção se chamado sem injeção correta do banco.
   - Prioridade: P3

3. `get_unit_history` retorna apenas contadores e não o histórico detalhado.
   - Arquivo: [app/services/condominium_service.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\services\condominium_service.py)
   - Mitigação:
     - para dashboard de unidade retornar histórico agregável por mês e vencimentos.

## 5) Observabilidade e auditoria

1. Rotas críticas (financeiro, status de chamado, exclusão) não registram evento no audit log.
   - Arquivos: routers de finanças, tickets e attachments
   - Prioridade: P2

2. `audit_events` existe, mas está com endpoint público e sem filtro de papel.
   - Arquivo: [app/routers/audit.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app/routers\audit.py)
   - Prioridade: P1

## 6) Roadmap técnico (alto valor para próxima etapa)

1. `auth` e tokens: manter token local, mas planejar claims de condomínio/role para escopo sem retrabalho.
   - Arquivos: [app/core/security.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\core\security.py), [app/core/deps.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app\core/deps.py)

2. Storage local já está pronto, manter abstração de provider sem quebrar schema.
   - Arquivos: [app/services/storage_service.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app/services/storage_service.py)

3. `board` e `resident` ainda têm alguns endpoints de retorno estático, ideal para evoluir em próximas etapas.
   - Arquivo: [app/routers/experiences.py](C:\Users\Usuario\Documents\hackhatons\lastroHackhaton\backend\app/routers/experiences.py)

## 7) Checklist pronto para usar no PR do frontend

- [ ] Confirmar quais endpoints já aceitam `meu perfil de acesso` (sem parâmetros de `unit_id` manuais).
- [ ] Confirmar autenticação em todos os mutáveis.
- [ ] Definir regras de visibilidade de anexos antes do design final.
- [ ] Padronizar contrato de erro e sucesso para chamadas IA.
- [ ] Revisar paginação e filtros nas telas de lista.
- [ ] Mapear quais rotas retornam dados sensíveis para `board`.
- [ ] Conferir textos e estados de erro em português nas respostas (UX copy).

## 8) Ações recomendadas (ordem sugerida)

- Semana 1: bloquear exposição cruzada (P0/P1) e validar quem pode ver o que.
- Semana 1/2: endurecer contratos de request/response mais críticos para chamadas de UI.
- Semana 2: fechar auditoria e rastreabilidade de mutações críticas.

## 9) Follow-up pós-hardening de permissões

Status: pendente para o próximo PR antes de piloto com múltiplos condomínios reais.

- Escopo por condomínio ainda precisa ser aplicado de ponta a ponta nas rotas de gestão.
  - Exemplos: tickets, finanças, documentos, comunicados, fornecedores, kanban, anexos e listagem de condomínios.
  - Regra esperada: `manager` e `board_member` só podem listar, ler ou escrever dados de condomínios onde tenham `Membership` ativa.
- `GET /audit/events` deve filtrar eventos pelo condomínio acessível ao `board_member`.
- Downloads/listagens de anexos devem validar `attachment.condominium_id` contra a membership do usuário.
- Payloads com `condominium_id` devem ser validados contra a membership ou derivados do contexto autenticado.

Observação: o hardening atual fecha exposição pública, separa escrita de manager e leitura de board, deriva autoria de comentários/anexos do token e bloqueia override de unidade no portal do morador. O isolamento multi-condomínio amplo fica documentado como próximo passo.
