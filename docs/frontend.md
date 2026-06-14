# Frontend

## Objetivo

O frontend deve ser uma plataforma web operacional para sindico,
condominio/conselho e inquilino/morador. A experiencia do sindico deve comecar
no dashboard de prioridades. A experiencia do morador deve comecar em
autosservico: chamados, status, regras e comunicados.

## Stack

- React.
- Vite.
- Tailwind.
- Lucide React para icones.

## Navegacao

Telas principais:

- Dashboard.
- Chamados.
- Financeiro.
- Inadimplencia e acordos.
- Documentos.
- Comunicados.
- Portal do morador.

## Perfis de usuario para demo

O frontend mockado deve permitir alternar entre tres perfis principais sem login
real. O seletor de perfil deve deixar claro qual visao esta ativa.

### Sindico / Manager

Usuario operacional do condominio. Pode ver e acionar:

- dashboard geral;
- chamados e Kanban;
- financeiro, inadimplencia e acordos;
- documentos e comunicados;
- fornecedores, anexos e acoes administrativas;
- alertas e recomendacoes de IA.

Dados sugeridos para mock:

- nome: Marina Souza;
- papel: Sindica;
- condominio: Condominio Jardim Aurora;
- unidade opcional: Nao se aplica.

### Conselho / Board member

Usuario de governanca e transparencia. Deve ter foco em leitura, auditoria e
acompanhamento, sem parecer operador do dia a dia.

Pode ver:

- resumo financeiro;
- status de manutencoes;
- eventos de auditoria;
- documentos publicados;
- decisoes recentes;
- indicadores de inadimplencia.

Dados sugeridos para mock:

- nome: Carlos Andrade;
- papel: Conselheiro;
- condominio: Condominio Jardim Aurora;
- unidade opcional: 1202.

### Morador / Resident

Usuario de autosservico. Deve ver apenas sua unidade e informacoes publicadas
para moradores.

Pode ver e acionar:

- portal do morador;
- dados da propria unidade;
- abertura de chamado;
- acompanhamento dos proprios chamados;
- comunicados;
- regras e documentos permitidos;
- pergunta para IA sobre regras do condominio.

Dados sugeridos para mock:

- nome: Joao Lima;
- papel: Morador;
- condominio: Condominio Jardim Aurora;
- unidade: 304, Bloco A;
- tipo: Inquilino.

### Admin da plataforma

Nao precisa aparecer como perfil principal da demo. Caso seja exibido, deve ficar
em uma area separada de bastidor para gestao interna da plataforma, nao como
fluxo principal do MVP para condominio.

## Dashboard

Deve exibir:

- saldo atual;
- caixa projetado;
- inadimplencia;
- chamados abertos;
- chamados criticos;
- prioridades da IA.

Essa tela e o centro da demo.

## Portal do morador

Funcionalidades:

- abrir chamado da unidade;
- acompanhar status;
- consultar comunicados;
- perguntar sobre regras do condominio;
- acessar documentos permitidos;
- visualizar manutencoes e avisos relevantes.

Estados:

- sem chamados abertos;
- chamado aguardando analise;
- chamado em execucao;
- chamado resolvido.

## Chamados

Funcionalidades:

- criar chamado;
- listar chamados;
- ver status;
- acionar classificacao por IA;
- exibir categoria, prioridade e proxima acao.

Estados:

- vazio: nenhum chamado cadastrado;
- carregando;
- erro de API;
- chamado classificado.

## Financeiro

Funcionalidades:

- resumo de receitas e despesas;
- deficit ou sobra projetada;
- insights financeiros;
- destaque para gastos fora do padrao.

## Inadimplencia e acordos

Funcionalidades:

- listar unidades em atraso;
- exibir valor e dias de atraso;
- simular acordo;
- mostrar impacto no caixa.

## Documentos

Funcionalidades:

- listar documentos;
- exibir resumo;
- enviar pergunta sobre o documento.

## Comunicados

Funcionalidades:

- escrever rascunho;
- gerar versao com IA;
- salvar comunicado.

## Direcao visual

Kondo deve parecer uma ferramenta de operacao e autosservico, nao uma landing
page. Priorizar:

- layout limpo;
- informacao escaneavel;
- tabelas e listas organizadas;
- cores sobrias com alertas claros;
- botoes com icones quando fizer sentido;
- responsividade para notebook e mobile.
