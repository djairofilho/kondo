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
