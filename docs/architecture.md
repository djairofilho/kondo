# Arquitetura

## Visao geral

O Kondo agora usa dois repositorios locais: um para frontend e outro para
backend/documentacao.

```txt
kondo-front/  # painel web em React + TanStack + Vite
kondo/        # API FastAPI, banco, testes e documentacao
```

Detalhes da decisao ficam em [Separacao de Repositorios](repository-split.md).

## Fluxo de dados

```txt
Usuario
  -> frontend React em kondo-front
  -> backend FastAPI
  -> SQLAlchemy
  -> SQLite no desenvolvimento
  -> PostgreSQL em producao
```

Servicos de IA ficam atras de uma camada propria no backend. No MVP, essa camada
pode retornar respostas simuladas. Depois, ela pode chamar OpenAI API ou outro
provedor.

O produto deve atender tres experiencias conectadas:

- sindico: operacao, decisao e priorizacao;
- condominio/conselho: governanca, transparencia e auditoria;
- inquilino/morador: solicitacoes, status, regras e comunicados.

## Modulos principais

- Dashboard: consolida metricas, alertas e prioridades.
- Chamados: cria, lista, classifica e acompanha solicitacoes.
- Financeiro: receitas, despesas, inadimplencia e previsao de caixa.
- Acordos: simula condicoes de pagamento e impacto no caixa.
- Documentos: armazena textos ou arquivos e habilita resumo/perguntas.
- Comunicados: gera e registra avisos para moradores.
- IA: classifica, resume, recomenda e gera textos.
- Portal do morador: permite abrir chamados, acompanhar status e consultar
  informacoes permitidas.
- WhatsApp futuro: captura reclamacoes e fotos por conversa, normaliza mensagens
  e cria chamados estruturados sem substituir o portal.

## Backend

O backend deve expor APIs REST simples e manter a regra de negocio fora das
rotas sempre que possivel:

- `routers/`: entrada HTTP.
- `schemas/`: contratos Pydantic.
- `models/`: modelos SQLAlchemy.
- `services/`: logica de dominio e IA.
- `core/`: configuracao, banco e dependencias comuns.

## Frontend

O frontend vive no repositorio irmao `../kondo-front` e deve priorizar uma
experiencia de painel operacional, com visoes por perfil:

- sindico: dashboard completo e acoes administrativas;
- conselho: transparencia financeira, status de decisoes e auditoria;
- morador: autosservico simples para demandas e regras.

Diretrizes de interface:

- navegacao lateral ou superior simples;
- dashboard como primeira tela;
- tabelas e listas densas, faceis de escanear;
- cards apenas para metricas e itens repetidos;
- estados claros para carregamento, erro e vazio.

## Evolucao para credito

O Kondo deve preparar os dados para um futuro marketplace de credito condominial:

- historico de arrecadacao;
- inadimplencia por unidade;
- acordos cumpridos ou quebrados;
- previsao de caixa;
- despesas recorrentes;
- obras e manutencoes planejadas.

No MVP, o credito e roadmap. A concessao futura deve ser feita por parceiros
regulados ou estrutura adequada.

## Evolucao para WhatsApp

A integracao com WhatsApp deve entrar como camada de entrada e notificacao, nao
como fonte oficial de dados. O fluxo recomendado e receber mensagem, normalizar
conteudo, classificar com IA, criar ou atualizar chamado e devolver respostas
curtas ao morador.

Detalhamento de conversa, escopo e arquitetura futura:
[WhatsApp](whatsapp.md).
