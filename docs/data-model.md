# Modelo de Dados

## Entidades principais

### Condominium

Representa o condominio gerenciado.

Campos principais:

- `id`
- `name`
- `address`
- `created_at`

### Unit

Representa uma unidade, como apartamento, sala ou casa.

Campos principais:

- `id`
- `condominium_id`
- `number`
- `block`
- `status`

### Resident

Representa morador ou responsavel pela unidade.

Campos principais:

- `id`
- `unit_id`
- `name`
- `email`
- `role`

### Ticket

Representa chamado operacional.

Campos principais:

- `id`
- `condominium_id`
- `unit_id`
- `title`
- `description`
- `location`
- `status`
- `category`
- `priority`
- `ai_analysis`
- `created_at`

### Expense

Representa despesa do condominio.

Campos principais:

- `id`
- `condominium_id`
- `description`
- `category`
- `amount`
- `due_date`
- `paid_at`

### Revenue

Representa receita esperada ou recebida.

Campos principais:

- `id`
- `condominium_id`
- `unit_id`
- `description`
- `amount`
- `due_date`
- `paid_at`

### Delinquency

Representa debito em atraso de uma unidade.

Campos principais:

- `id`
- `unit_id`
- `amount_due`
- `days_late`
- `status`
- `risk`

### Agreement

Representa acordo de pagamento.

Campos principais:

- `id`
- `unit_id`
- `delinquency_id`
- `entry_amount`
- `installments`
- `monthly_installment`
- `status`
- `created_at`

### Document

Representa regimento, convencao, ata, contrato ou balancete.

Campos principais:

- `id`
- `condominium_id`
- `title`
- `document_type`
- `content`
- `summary`
- `created_at`

### Announcement

Representa comunicado para moradores.

Campos principais:

- `id`
- `condominium_id`
- `title`
- `body`
- `audience`
- `created_at`

## Relacoes

- Um condominio tem muitas unidades.
- Uma unidade tem moradores, receitas, inadimplencias, acordos e chamados.
- Um chamado pertence a um condominio e pode estar ligado a uma unidade.
- Uma inadimplencia pode gerar um acordo.
- Documentos e comunicados pertencem ao condominio.

## Observacoes para o MVP

- `ai_analysis` pode ser um campo JSON portavel.
- Valores monetarios devem usar decimal.
- No SQLite, migrations podem ser simples ou recriadas durante o hackathon.
- Em producao, Postgres deve ser usado para consistencia e concorrencia.

