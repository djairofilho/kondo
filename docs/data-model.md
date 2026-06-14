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

Observacao: o papel de acesso ao sistema fica em `Membership.role`. Em
`Resident`, o tipo de morador fica em `resident_type`, como `owner`, `tenant` ou
`occupant`.

### Membership

Conecta uma pessoa a um condominio e define o papel dela naquele contexto.

Campos principais:

- `id`
- `user_id`
- `condominium_id`
- `unit_id`
- `role`
- `status`

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

Ao criar um chamado, a API tambem cria um `WorkItem` para o Kanban operacional.

### WorkItem

Representa um card operacional no Kanban.

Campos principais:

- `id`
- `condominium_id`
- `ticket_id`
- `type`
- `title`
- `description`
- `status`
- `priority`
- `due_date`
- `source_type`
- `source_id`

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

### Attachment

Representa metadados de arquivos como fotos, boletos, comprovantes, notas e
documentos.

Campos principais:

- `id`
- `condominium_id`
- `entity_type`
- `entity_id`
- `uploaded_by_user_id`
- `original_file_name`
- `stored_file_name`
- `content_type`
- `file_size`
- `storage_key`
- `storage_provider`
- `visibility`

### Vendor

Representa fornecedor do condominio.

Campos principais:

- `id`
- `condominium_id`
- `name`
- `category`
- `email`
- `phone`
- `status`

### Quote

Representa orcamento de fornecedor.

Campos principais:

- `id`
- `condominium_id`
- `vendor_id`
- `work_item_id`
- `title`
- `amount`
- `scope`
- `warranty_days`
- `status`

### AuditEvent

Representa evento rastreavel do sistema.

Campos principais:

- `id`
- `condominium_id`
- `actor_user_id`
- `action`
- `entity_type`
- `entity_id`
- `event_metadata`

## Relacoes

- Um condominio tem muitas unidades.
- Uma unidade tem moradores, receitas, inadimplencias, acordos e chamados.
- Um chamado pertence a um condominio e pode estar ligado a uma unidade.
- Uma inadimplencia pode gerar um acordo.
- Documentos e comunicados pertencem ao condominio.
- Uma pessoa pode ter varios memberships em condominios diferentes.
- Um chamado pode gerar um ou mais itens no Kanban.
- Anexos podem pertencer a diferentes entidades via `entity_type` e `entity_id`.

## Observacoes para o MVP

- `ai_analysis` pode ser um campo JSON portavel.
- Valores monetarios devem usar decimal.
- No SQLite, migrations podem ser simples ou recriadas durante o hackathon.
- Em producao, Postgres deve ser usado para consistencia e concorrencia.
