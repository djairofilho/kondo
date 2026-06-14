# IA

## Papel da IA

A IA no Kondo deve reduzir trabalho manual e transformar dados soltos em acoes.
Ela nao deve tomar decisoes sensiveis sozinha, como perdoar divida, aprovar
gasto relevante ou iniciar cobranca juridica.

## MVP

No MVP, a IA pode ser implementada como servico abstrato com respostas simuladas
e deterministicas. Isso permite demonstrar valor mesmo sem depender de chave de
API ou internet.

Exemplo de servico:

```txt
services/ai_service.py
```

Responsabilidades:

- classificar chamados;
- transformar mensagens de WhatsApp em chamados estruturados no futuro;
- gerar comunicados;
- resumir documentos;
- responder perguntas sobre documentos;
- sugerir acordos;
- gerar insights financeiros.

## Casos de uso

### Classificacao de chamados

Entrada:

- titulo;
- descricao;
- local;
- anexos no futuro.

Saida:

- categoria;
- prioridade;
- risco;
- responsavel sugerido;
- proxima acao.

### Entrada assistida por WhatsApp

Entrada futura:

- texto livre enviado pelo morador;
- foto ou video;
- numero do remetente;
- condominio identificado;
- contexto curto da conversa.

Saida:

- intencao;
- resumo do problema;
- dados faltantes;
- categoria;
- prioridade;
- risco;
- local;
- resposta sugerida ao morador;
- dados para criar ou atualizar chamado.

Essa IA deve ser restrita a abertura e acompanhamento de chamados. Ela nao deve
aprovar gastos, assumir prazos sem confirmacao ou expor informacoes sensiveis.

### Resumo financeiro

Entrada:

- receitas previstas;
- receitas recebidas;
- despesas;
- inadimplencia.

Saida:

- resumo simples;
- alerta de caixa;
- gastos fora do padrao;
- recomendacoes operacionais.

### Simulacao de acordos

Entrada:

- valor devido;
- dias de atraso;
- historico da unidade;
- caixa projetado;
- entrada e parcelas desejadas.

Saida:

- recomendacao de entrada;
- quantidade maxima de parcelas;
- impacto no caixa;
- risco de quebra do acordo.

### Geracao de comunicados

Entrada:

- rascunho do sindico;
- tom desejado;
- publico-alvo.

Saida:

- titulo;
- corpo do comunicado;
- versao clara e objetiva.

### Leitura de documentos

Entrada:

- conteudo de regimento, convencao, ata ou contrato;
- texto extraido automaticamente de PDFs enviados em `/documents/upload`;
- pergunta do usuario.

Saida:

- resposta em linguagem simples;
- trechos recuperados do documento quando disponiveis;
- aviso de que a resposta nao substitui orientacao juridica.

No modo local, a leitura usa RAG lexical sobre o campo `Document.content`: o PDF
e extraido, dividido em trechos e ranqueado pelos termos da pergunta. Se nenhum
trecho relevante for encontrado, a API informa que nao encontrou base suficiente
no documento em vez de inventar resposta.

## Evolucao

Quando houver chave de IA configurada, o backend pode usar OpenAI API. Sem chave,
deve cair para simulacao. Essa decisao permite demo confiavel e evita quebrar o
fluxo do hackathon.
