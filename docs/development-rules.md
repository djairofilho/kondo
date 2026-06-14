# Regras de Desenvolvimento

## Regra principal

Toda funcionalidade criada no Kondo deve ser documentada no mesmo PR.

Isso vale para:

- endpoints;
- modelos de dados;
- variaveis de ambiente;
- comandos de execucao;
- scripts;
- fluxos de produto;
- decisoes tecnicas;
- limitacoes conhecidas;
- estrategias temporarias, como SQLite e storage local.

## Checklist por PR

Antes de abrir um PR, validar:

- O `README.md` foi atualizado se mudou setup, execucao ou env.
- `docs/api.md` foi atualizado se endpoints mudaram.
- `docs/data-model.md` foi atualizado se modelos ou relacoes mudaram.
- `docs/backend.md` foi atualizado se arquitetura, comandos, banco, auth ou
  storage mudaram.
- `docs/use-cases.md` foi atualizado se o fluxo de usuario mudou.
- Testes foram adicionados ou atualizados quando houver comportamento novo.
- Se modelos SQLAlchemy mudaram, migration Alembic foi criada ou atualizada.

## Padrao de PR

Usar nomes convencionais:

```txt
feat(backend): add database models
feat(backend): add auth and memberships
feat(backend): add operational workflows
docs: update backend implementation guide
chore: add environment examples
```

## Decisoes temporarias

SQLite e storage local sao atalhos para desenvolvimento rapido. O dominio deve
continuar maleavel para trocar:

- SQLite por PostgreSQL via `DATABASE_URL`;
- storage local por S3, R2 ou Supabase Storage via `storage_service`.

Nenhuma regra de negocio deve depender diretamente de SQLite ou do filesystem
local.

