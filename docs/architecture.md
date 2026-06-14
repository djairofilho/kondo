# Arquitetura

## Visao geral

O Kondo usa um monorepo simples com separacao direta entre frontend, backend e
documentacao.

```txt
frontend/     # painel web em React + Vite + Tailwind
backend/      # API em FastAPI + SQLAlchemy + Pydantic
docs/         # produto, arquitetura, API, demo e pitch
```

## Fluxo de dados

```txt
Usuario
  -> frontend React
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

## Backend

O backend deve expor APIs REST simples e manter a regra de negocio fora das
rotas sempre que possivel:

- `routers/`: entrada HTTP.
- `schemas/`: contratos Pydantic.
- `models/`: modelos SQLAlchemy.
- `services/`: logica de dominio e IA.
- `core/`: configuracao, banco e dependencias comuns.

## Frontend

O frontend deve priorizar uma experiencia de painel operacional, com visoes por
perfil:

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
