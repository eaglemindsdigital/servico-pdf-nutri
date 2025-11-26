# 🎯 CONFIGURAÇÃO N8N - EXEMPLOS PRÁTICOS

## 📋 EXEMPLO 1: Workflow Simples de Teste

```
[Manual Trigger] → [Set] → [HTTP Request] → [Download PDF]
```

### Set Node - Dados de Teste
```json
{
  "NOME": "Pedro Dual",
  "SEXO": "M",
  "ID": "553284692159",
  "PRAZO": "11/10/2025",
  "PESO": "85",
  "META KG": "78",
  "GET": "2875.25",
  "ALTURA": "180",
  "IDADE": "25",
  "NAF": "Moderado"
}
```

### HTTP Request Node
```json
{
  "method": "POST",
  "url": "https://sua-url.railway.app/gerar-pdf",
  "authentication": "none",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ $json }}",
  "options": {
    "response": {
      "response": {
        "responseFormat": "file"
      }
    }
  }
}
```

---

## 📋 EXEMPLO 2: Workflow com Google Sheets

```
[Google Sheets Trigger] → [Code] → [HTTP Request] → [WhatsApp]
```

### Google Sheets Trigger
Detecta nova linha na planilha com colunas:
- Nome
- Sexo (Masculino/Feminino)
- Telefone
- Peso
- Altura
- Idade
- etc.

### Code Node (JavaScript) - Preparar Dados
```javascript
// Padronizar o formato dos dados
const dados = {
  NOME: $input.item.json.Nome,
  SEXO: $input.item.json.Sexo, // Aceita: M, F, Masculino, Feminino
  ID: $input.item.json.row_number || String(Date.now()),
  PRAZO: new Date().toLocaleDateString('pt-BR'),
  PESO: String($input.item.json.Peso),
  "META KG": String($input.item.json['Meta de Peso']),
  GET: String($input.item.json.GET || 2500),
  ALTURA: String($input.item.json.Altura),
  IDADE: String($input.item.json.Idade),
  NAF: $input.item.json['Nível de Atividade'] || 'Moderado'
};

return { json: dados };
```

### HTTP Request (mesmo do exemplo 1)

### WhatsApp Node - Enviar PDF
```json
{
  "operation": "sendFile",
  "chatId": "={{ $('Google Sheets Trigger').item.json.Telefone }}@c.us",
  "caption": "Olá {{ $('Google Sheets Trigger').item.json.Nome }}! Segue seu plano nutricional personalizado 💪",
  "file": "={{ $binary.data }}"
}
```

---

## 📋 EXEMPLO 3: Workflow com Webhook (API Externa)

```
[Webhook] → [Validação] → [HTTP Request] → [Resposta]
```

### Webhook Node
- Method: POST
- Path: `/gerar-plano`

### Code Node - Validação
```javascript
// Validar campos obrigatórios
const camposObrigatorios = ['NOME', 'SEXO', 'PESO', 'ALTURA', 'IDADE'];
const dados = $input.item.json;

for (const campo of camposObrigatorios) {
  if (!dados[campo]) {
    return {
      json: { 
        erro: true, 
        mensagem: `Campo ${campo} é obrigatório` 
      }
    };
  }
}

// Adicionar campos calculados/padrões
dados.ID = dados.ID || String(Date.now());
dados.PRAZO = dados.PRAZO || new Date().toLocaleDateString('pt-BR');
dados.NAF = dados.NAF || 'Moderado';
dados['META KG'] = dados['META KG'] || String(Number(dados.PESO) - 5);

return { json: dados };
```

### HTTP Request (mesmo do exemplo 1)

### Respond to Webhook Node
```json
{
  "respondWith": "allIncomingItems",
  "responseBody": "={{ $json.erro ? { erro: $json.mensagem } : { sucesso: true, pdf_gerado: true } }}"
}
```

---

## 📋 EXEMPLO 4: Workflow Completo com Validações

```
[Trigger] → [Buscar Dados] → [Calcular IMC e GET] → [HTTP Request] → [Salvar Google Drive] → [Enviar WhatsApp]
```

### Code Node - Calcular IMC e GET
```javascript
const peso = Number($input.item.json.PESO);
const altura = Number($input.item.json.ALTURA) / 100; // cm para metros
const idade = Number($input.item.json.IDADE);
const sexo = $input.item.json.SEXO.toUpperCase();

// Calcular IMC
const imc = peso / (altura * altura);

// Calcular TMB (Taxa Metabólica Basal) - Fórmula de Harris-Benedict
let tmb;
if (sexo === 'M' || sexo === 'MASCULINO') {
  tmb = 88.362 + (13.397 * peso) + (4.799 * (altura * 100)) - (5.677 * idade);
} else {
  tmb = 447.593 + (9.247 * peso) + (3.098 * (altura * 100)) - (4.330 * idade);
}

// Calcular GET (Gasto Energético Total)
const naf = $input.item.json.NAF || 'Moderado';
let fatorAtividade = 1.55; // Moderado (padrão)

if (naf.includes('Sedentário')) fatorAtividade = 1.2;
else if (naf.includes('Leve')) fatorAtividade = 1.375;
else if (naf.includes('Moderado')) fatorAtividade = 1.55;
else if (naf.includes('Intenso')) fatorAtividade = 1.725;
else if (naf.includes('Muito Intenso')) fatorAtividade = 1.9;

const get = tmb * fatorAtividade;

// Retornar dados completos
return {
  json: {
    ...$input.item.json,
    IMC: imc.toFixed(2),
    GET: get.toFixed(2)
  }
};
```

---

## 🔍 TESTES DE VALIDAÇÃO

### Teste 1: Sexo Feminino
```json
{
  "NOME": "Ana Costa",
  "SEXO": "Feminino",
  "PESO": "65",
  "ALTURA": "160",
  "IDADE": "28"
}
```
**Esperado:** PDF com template feminino

### Teste 2: Sexo Masculino
```json
{
  "NOME": "João Silva",
  "SEXO": "M",
  "PESO": "80",
  "ALTURA": "175",
  "IDADE": "35"
}
```
**Esperado:** PDF com template masculino

### Teste 3: Variações de Sexo (todas devem funcionar)
- "Feminino", "F", "FEMININO", "f", "Mulher", "MULHER"
- "Masculino", "M", "MASCULINO", "m", "Homem", "HOMEM"

---

## 🚨 TRATAMENTO DE ERROS

### Error Trigger Node
Adicione após o HTTP Request para capturar erros:

```javascript
// Code Node - Processar Erro
const erro = $input.item.json;

// Log detalhado
console.log('ERRO AO GERAR PDF:', erro);

// Enviar notificação
return {
  json: {
    tipo_erro: 'Falha na geração de PDF',
    cliente: $('Google Sheets Trigger').item.json.Nome || 'Desconhecido',
    mensagem: erro.error || 'Erro desconhecido',
    timestamp: new Date().toISOString()
  }
};
```

### Slack/Telegram Notification
Envie alerta para você quando houver erro:
```
"⚠️ ERRO NO SERVIÇO PDF
Cliente: {{ $json.cliente }}
Erro: {{ $json.mensagem }}
Horário: {{ $json.timestamp }}"
```

---

## 💡 DICAS DE PERFORMANCE

### 1. Cache de Resultados
Se o mesmo cliente pedir várias vezes, reutilize o PDF:
```javascript
// Gerar ID único baseado nos dados
const dadosHash = JSON.stringify($json);
const pdfId = require('crypto').createHash('md5').update(dadosHash).digest('hex');

// Verificar se já foi gerado
// ... lógica de cache ...
```

### 2. Processamento em Lote
Para gerar múltiplos PDFs:
```
[Google Sheets] → [Split In Batches] → [HTTP Request] → [Merge]
```
Gera 10 PDFs por vez, evitando sobrecarregar a API.

### 3. Retry Automático
Configure no HTTP Request:
- Options → Request Options → Retry On Fail: `true`
- Max Retries: `3`
- Wait Between Retries: `1000ms`

---

## 📊 MONITORAMENTO DE USO

### Code Node - Log de Métricas
```javascript
// Após gerar PDF com sucesso
const metricas = {
  timestamp: new Date().toISOString(),
  cliente: $input.item.json.NOME,
  sexo: $input.item.json.SEXO,
  template_usado: $input.item.json.SEXO.includes('F') ? 'feminino' : 'masculino',
  tempo_geracao: Date.now() - $execution.startedAt
};

// Salvar em Google Sheets de métricas
return { json: metricas };
```

---

## ✅ CHECKLIST FINAL

Antes de colocar em produção:

- [ ] Testei com sexo Feminino
- [ ] Testei com sexo Masculino
- [ ] Testei com dados incompletos (deve dar erro claro)
- [ ] Configurei tratamento de erros
- [ ] Configurei notificações de falha
- [ ] Testei o envio por WhatsApp
- [ ] Documentei o workflow

---

## 🎓 RECURSOS ADICIONAIS

### Variáveis de Ambiente na Railway
Para deixar mais seguro, você pode usar variáveis de ambiente:

1. Na Railway, vá em Settings → Variables
2. Adicione: `SECRET_TOKEN=seu-token-secreto`
3. No n8n, adicione header: `Authorization: Bearer seu-token-secreto`

### Webhook Signature
Para validar que requisições vêm do n8n:
```python
# No app.py, adicione validação de token
token = request.headers.get('Authorization')
if token != os.environ.get('SECRET_TOKEN'):
    return jsonify({"erro": "Não autorizado"}), 401
```

---

Pronto! Com esses exemplos você consegue implementar qualquer fluxo! 🚀
