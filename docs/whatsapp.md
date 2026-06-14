# WhatsApp

## Visao

O WhatsApp deve ser tratado como canal futuro de entrada rapida para moradores,
inquilinos e ocupantes. Ele nao substitui o portal nem o painel do sindico. O
papel dele e capturar mensagens soltas e transformar conversa em operacao
rastreavel dentro do Kondo.

No MVP atual, a integracao real com WhatsApp fica fora do escopo. A plataforma
web continua sendo a fonte oficial. O WhatsApp entra como roadmap para reduzir
friccao na abertura de reclamacoes, envio de fotos e acompanhamento simples de
status.

```txt
WhatsApp = entrada rapida e resposta curta
Portal = acompanhamento, transparencia e fonte oficial
Painel do sindico = operacao, priorizacao e decisao
```

## Tese

O morador nao deveria precisar aprender um sistema novo para relatar um problema
do dia a dia. Ele pode mandar uma mensagem pelo WhatsApp, e o Kondo transforma
essa mensagem em um chamado estruturado, classificado por IA, visivel no Kanban e
acompanhavel pelo portal.

O valor principal nao e ter um chatbot generico. O valor e converter conversa
desorganizada em processo operacional:

- mensagem vira chamado;
- foto vira anexo;
- urgencia vira prioridade;
- duvida vira pergunta estruturada;
- cobranca repetida vira acompanhamento de status;
- conversa privada vira historico rastreavel.

## Escopo recomendado

### Dentro do escopo

- abrir reclamacoes e solicitacoes;
- receber fotos e videos de problemas;
- pedir informacoes faltantes;
- classificar categoria, prioridade, risco e local;
- criar chamado;
- enviar protocolo;
- avisar mudanca de status;
- responder perguntas simples sobre o chamado;
- enviar link para acompanhar no portal;
- registrar todo o historico no Kondo.

### Fora do escopo inicial

- prestacao de contas completa;
- discussao de assembleia;
- votacoes formais;
- negociacao complexa de inadimplencia;
- envio de documentos sensiveis;
- decisoes financeiras ou juridicas automatizadas;
- atendimento aberto sobre qualquer tema.

## Fluxo principal

```txt
Morador envia mensagem no WhatsApp
  -> Kondo identifica condominio e morador
  -> IA entende intencao, local, categoria e urgencia
  -> IA pede dados faltantes se necessario
  -> Kondo cria chamado e anexos
  -> Chamado aparece no Kanban do sindico
  -> Morador recebe protocolo
  -> Mudancas de status voltam pelo WhatsApp
  -> Portal mantem historico oficial
```

## Conversa ideal

### Abertura de reclamacao com foto

```txt
Morador:
Tem um vazamento na garagem do bloco B desde ontem.
O chao esta escorregadio.

Kondo:
Entendi. Parece um problema hidraulico em area comum com risco de acidente.
Voce consegue enviar uma foto do local?

Morador:
[foto]

Kondo:
Obrigado. Criei o chamado #142.

Resumo: vazamento na garagem do bloco B com risco de escorregamento.
Prioridade: alta.
Status: recebido.

O sindico foi notificado. Voce pode acompanhar por aqui ou pelo portal.
```

### Pergunta faltante antes de criar chamado

```txt
Morador:
O portao esta com problema.

Kondo:
Para abrir o chamado corretamente, qual portao esta com problema?

1. Entrada de pedestres
2. Garagem
3. Servico
4. Outro

Morador:
Garagem.

Kondo:
Perfeito. O problema impede a entrada ou saida de veiculos?

Morador:
Sim, esta travando.

Kondo:
Chamado #143 criado como prioridade alta.
Local: portao da garagem.
Status: recebido.
```

### Atualizacao de status

```txt
Kondo:
Atualizacao do chamado #142:

Status: fornecedor acionado.
Previsao: visita tecnica hoje entre 14h e 16h.
```

### Encerramento

```txt
Kondo:
O chamado #142 foi marcado como resolvido.

O vazamento foi corrigido e a area foi liberada.
Se o problema continuar, responda "reabrir #142".
```

## Intencoes que a IA deve reconhecer

- abrir reclamacao;
- complementar chamado existente;
- enviar foto de problema;
- pedir status de chamado;
- reabrir chamado;
- cancelar chamado;
- perguntar regra simples;
- confirmar informacao;
- dizer que e urgente;
- mandar mensagem que exige atendimento humano.

## Classificacao esperada

Ao receber uma mensagem, a IA deve extrair:

- condominio;
- usuario;
- unidade, quando aplicavel;
- tipo de solicitacao;
- categoria;
- local;
- resumo;
- prioridade;
- risco;
- necessidade de anexo;
- dados faltantes;
- resposta sugerida;
- acao operacional sugerida.

Exemplo de saida interna:

```json
{
  "intent": "create_ticket",
  "category": "hydraulic",
  "priority": "high",
  "risk": "slip_hazard",
  "location": "garagem bloco B",
  "summary": "Vazamento com chao escorregadio na garagem do bloco B.",
  "missing_fields": [],
  "suggested_status": "received",
  "suggested_work_item_type": "ticket"
}
```

## Regras de seguranca e controle

- A IA nao deve prometer prazo sem confirmacao operacional.
- A IA nao deve aprovar gasto, contratar fornecedor ou assumir culpa.
- A IA nao deve expor dados financeiros ou documentos sensiveis pelo WhatsApp.
- Mensagens com conflito, ameaca, risco juridico ou acidente devem escalar para
  atendimento humano.
- O usuario deve saber quando esta falando com assistente automatico.
- Toda conversa relevante deve ficar registrada no Kondo.
- O portal continua sendo a fonte oficial de status, documentos e historico.

## Arquitetura futura

```txt
WhatsApp Provider
  -> WhatsApp Gateway
  -> Message Intake Service
  -> AI Classification Service
  -> Ticket Service
  -> Attachment Service
  -> Kanban
  -> Notification Service
  -> WhatsApp Provider
```

Componentes sugeridos:

- `whatsapp_gateway`: recebe webhooks do provedor.
- `message_intake_service`: normaliza mensagens, midias e remetentes.
- `conversation_service`: mantem contexto curto da conversa.
- `ai_classification_service`: interpreta intencao e dados estruturados.
- `ticket_service`: cria ou atualiza chamados.
- `notification_service`: envia respostas e atualizacoes.

## Dados a persistir no futuro

- numero do WhatsApp;
- consentimento do usuario;
- provedor usado;
- id externo da conversa;
- id externo da mensagem;
- direcao da mensagem;
- texto normalizado;
- anexos recebidos;
- entidade vinculada, como chamado ou unidade;
- status de entrega;
- historico de escalonamento humano.

## Possiveis endpoints futuros

```txt
POST /integrations/whatsapp/webhook
GET  /integrations/whatsapp/conversations
GET  /integrations/whatsapp/conversations/{conversation_id}
POST /integrations/whatsapp/conversations/{conversation_id}/reply
POST /integrations/whatsapp/conversations/{conversation_id}/create-ticket
POST /integrations/whatsapp/messages/{message_id}/classify-ai
```

Esses endpoints nao fazem parte do backend atual. Eles documentam a direcao de
produto e ajudam a evitar que a integracao futura seja improvisada.

## Demo sem integracao real

Para hackathon, o frontend pode simular uma tela chamada "Inbox WhatsApp":

- lista de mensagens recebidas;
- detalhe da conversa;
- card de classificacao sugerida pela IA;
- botao para criar chamado;
- resposta automatica sugerida;
- link para abrir o chamado no Kanban.

Essa demo comunica o valor do WhatsApp sem depender de aprovacao de templates,
provedor externo ou numero real.
