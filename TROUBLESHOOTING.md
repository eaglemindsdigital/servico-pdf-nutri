# 🔧 TROUBLESHOOTING - RESOLUÇÃO DE PROBLEMAS

## ❌ ERROS COMUNS E SOLUÇÕES

---

### 1️⃣ ERRO: "ModuleNotFoundError: No module named 'fitz'"

**Causa:** A biblioteca PyMuPDF não foi instalada.

**Solução:**
1. Verifique se `requirements.txt` contém: `PyMuPDF==1.23.8`
2. Faça novo deploy na Railway (push no GitHub)
3. Aguarde a Railway reinstalar as dependências

**Como verificar:** Olhe os logs da Railway, deve aparecer:
```
Installing dependencies...
Collecting PyMuPDF==1.23.8
Successfully installed PyMuPDF-1.23.8
```

---

### 2️⃣ ERRO: "Template feminino não encontrado no servidor"

**Causa:** O arquivo PDF não foi enviado ou está com nome errado.

**Solução:**
1. Verifique no GitHub se existe: `templates/plano-lead-feminino-otim.pdf`
2. Confirme que o nome está EXATAMENTE assim (sem espaços, acentos, etc)
3. Se estiver errado, renomeie e faça novo commit

**Estrutura esperada no GitHub:**
```
servico-pdf-nutri/
└── templates/
    ├── plano-lead-feminino-otim.pdf ✅
    └── plano-lead-masculino-otim.pdf ✅
```

---

### 3️⃣ ERRO: "Campo 'SEXO' não encontrado"

**Causa:** Você não está enviando o campo SEXO do n8n.

**Solução no n8n:**
```json
// Certifique-se de incluir:
{
  "SEXO": "Masculino"  // ou "Feminino", "M", "F"
}
```

**Mapeamento do Google Sheets:**
- Se a coluna se chama "Gênero", mapeie: `"SEXO": "={{ $json.Gênero }}"`
- Se é "Sexo", mapeie: `"SEXO": "={{ $json.Sexo }}"`

---

### 4️⃣ ERRO: "Sexo inválido: 'masculino'. Use: 'Feminino', 'Masculino', 'F' ou 'M'"

**Causa:** O valor está em minúscula ou com acento.

**Solução no n8n - Code Node antes do HTTP Request:**
```javascript
// Normalizar o sexo
let sexo = $json.SEXO || $json.Sexo || $json.Genero;

// Padronizar
sexo = sexo.trim().toUpperCase();

if (sexo.includes('FEM') || sexo === 'F') {
  sexo = 'Feminino';
} else if (sexo.includes('MASC') || sexo === 'M') {
  sexo = 'Masculino';
}

return {
  json: {
    ...$json,
    SEXO: sexo
  }
};
```

---

### 5️⃣ ERRO: "Connection timeout" no n8n

**Causa:** A Railway demorou muito para responder (servidor frio).

**Solução:**
1. No HTTP Request do n8n:
   - Options → Request Options
   - Timeout: `30000` (30 segundos)
2. Configure retry:
   - Retry On Fail: `true`
   - Max Retries: `2`

**Explicação:** Na primeira requisição, a Railway pode levar 10-15s para "acordar" o servidor. Depois fica rápido.

---

### 6️⃣ ERRO: "PDF gerado mas textos não aparecem"

**Causa:** Coordenadas X e Y estão erradas para seu template.

**Solução - Ajustar coordenadas:**

1. Abra seu PDF no Adobe Reader
2. Habilite "Ferramentas → Comentários → Adicionar nota"
3. Clique onde quer o texto e veja as coordenadas (canto inferior)
4. Edite `app.py` na lista `campos`:

```python
# Exemplo: mover o nome mais para direita
{"x": 630,  "y": 1660, "texto": dados["NOME"], ...}
#     ↑ aumente para direita, diminua para esquerda
#            ↑ aumente para baixo, diminua para cima
```

5. Commit e push → Railway redeploya

**Dica:** Faça testes incrementais mudando 1 campo por vez.

---

### 7️⃣ ERRO: "Response is not JSON" no n8n

**Causa:** Você configurou para receber JSON mas o serviço retorna PDF (arquivo binário).

**Solução no n8n - HTTP Request:**
- Options → Response
- Response Format: **"File"** (NÃO use "JSON")

---

### 8️⃣ ERRO: Railway mostra "Application failed to respond"

**Causa:** O servidor não está rodando na porta correta.

**Verificação no app.py:**
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # ← Deve estar assim
    app.run(host='0.0.0.0', port=port)
```

**Verificação no Procfile:**
```
web: gunicorn app:app  # ← Deve estar EXATAMENTE assim
```

Se estiver diferente, corrija e faça novo deploy.

---

### 9️⃣ ERRO: "Font not found" ou textos com fonte errada

**Causa:** O arquivo `Montserrat-Bold.ttf` não foi encontrado.

**Comportamento esperado:**
- Se a fonte EXISTE → Usa Montserrat
- Se NÃO existe → Usa Helvetica-Bold (fonte padrão)

**Para usar Montserrat:**
1. Baixe de: https://fonts.google.com/specimen/Montserrat
2. Extraia `Montserrat-Bold.ttf`
3. Coloque na RAIZ do projeto (não em `templates/`)
4. Commit e push

**Verificação nos logs da Railway:**
```
✅ Fonte 'Montserrat-Bold.ttf' encontrada! Usando Montserrat.
```
ou
```
⚠️ Fonte 'Montserrat-Bold.ttf' NÃO encontrada na pasta.
   👉 Usando 'Helvetica-Bold' padrão.
```

---

### 🔟 ERRO: "Railway exceeded free tier limits"

**Causa:** Você ultrapassou 500 horas/mês ou $5 de crédito.

**Soluções:**
1. **Plano Hobby:** $5/mês para uso ilimitado
2. **Otimizar uso:** Configure sleep em horários inativos
3. **Alternativas gratuitas:**
   - Render.com (750 horas/mês)
   - Fly.io (até 3 apps grátis)

---

## 🔍 COMO DEBUGAR

### Passo 1: Verificar se a API está online
Acesse no navegador: `https://sua-url.railway.app/`

**Esperado:**
```json
{
  "status": "online",
  "servico": "Gerador de PDF - Plano Nutricional",
  "endpoint": "/gerar-pdf",
  "metodo": "POST"
}
```

Se não aparecer isso, o servidor está offline.

---

### Passo 2: Ver logs da Railway
1. Acesse Railway → Seu projeto
2. Aba "Deployments"
3. Click no deployment ativo
4. Veja erros em tempo real

**Erros comuns nos logs:**
- `ModuleNotFoundError` → Falta biblioteca no `requirements.txt`
- `FileNotFoundError` → PDF template não encontrado
- `SyntaxError` → Erro no código Python

---

### Passo 3: Testar com cURL (fora do n8n)

No terminal do Windows (cmd):
```bash
curl -X POST https://sua-url.railway.app/gerar-pdf ^
  -H "Content-Type: application/json" ^
  -d "{\"NOME\":\"Teste\",\"SEXO\":\"M\",\"ID\":\"123\",\"PRAZO\":\"11/10/2025\",\"PESO\":\"80\",\"META KG\":\"75\",\"GET\":\"2500\",\"ALTURA\":\"175\",\"IDADE\":\"30\",\"NAF\":\"Moderado\"}" ^
  --output teste.pdf
```

Se funcionar, o problema está no n8n, não na API.

---

### Passo 4: Testar no n8n com dados fixos

Crie um workflow simples:
```
[Manual Trigger] → [Set com dados fixos] → [HTTP Request]
```

Se funcionar com dados fixos mas não com dados reais:
→ O problema está na etapa anterior (Google Sheets, webhook, etc)

---

### Passo 5: Adicionar logs extras no código

Edite `app.py` e adicione prints:

```python
@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf():
    try:
        dados = request.json
        print("=== DADOS RECEBIDOS ===")
        print(json.dumps(dados, indent=2, ensure_ascii=False))
        
        # ... resto do código ...
```

Depois veja os logs na Railway para ver exatamente o que está chegando.

---

## 📊 VERIFICAÇÃO DE INTEGRIDADE

### Checklist antes de reportar erro:

- [ ] A API responde em `https://sua-url.railway.app/` ?
- [ ] Os 2 PDFs estão na pasta `templates/` no GitHub?
- [ ] O `requirements.txt` tem as 3 bibliotecas?
- [ ] O `Procfile` está correto?
- [ ] Você está enviando TODOS os campos obrigatórios?
- [ ] O campo SEXO está em formato válido?
- [ ] O n8n está configurado para receber "File" e não "JSON"?

---

## 🆘 ÚLTIMOS RECURSOS

### Se nada funcionou:

1. **Delete tudo e recomece:**
   - Delete o repositório no GitHub
   - Delete o projeto na Railway
   - Siga o GUIA_COMPLETO.md novamente do zero

2. **Teste localmente primeiro:**
   ```bash
   pip install -r requirements.txt
   python app.py
   # Teste em http://localhost:5000
   ```
   Se funciona local mas não na Railway → Problema de deploy
   Se não funciona nem local → Problema no código/arquivos

3. **Peça ajuda com contexto:**
   Envie:
   - Screenshot do erro no n8n
   - Screenshot dos logs da Railway
   - Print da estrutura de pastas no GitHub
   - Exemplo do JSON que você está enviando

---

## 💡 DICAS DE PREVENÇÃO

### 1. Sempre teste mudanças localmente
Antes de fazer deploy, rode `python app.py` no seu PC.

### 2. Use Git branches para testes
```bash
git checkout -b teste-nova-feature
# Faça mudanças
# Teste
git checkout main  # Volta para versão estável se der errado
```

### 3. Mantenha backup dos PDFs
Sempre tenha cópia local dos templates originais.

### 4. Documente customizações
Se mudar coordenadas ou adicionar campos, anote no README.md.

### 5. Monitore uso da Railway
Configure alertas quando atingir 80% do limite gratuito.

---

## 🎯 RESUMO DOS ARQUIVOS CRÍTICOS

**Esses 3 arquivos NÃO podem ter erro:**

1. **requirements.txt** - Lista as bibliotecas
2. **Procfile** - Comando de inicialização
3. **app.py** - Código principal

Se algum deles estiver errado, NADA funciona.

**Validação rápida:**

```bash
# requirements.txt deve ter EXATAMENTE:
Flask==3.0.0
PyMuPDF==1.23.8
gunicorn==21.2.0

# Procfile deve ter EXATAMENTE:
web: gunicorn app:app

# app.py deve ter a função:
@app.route('/gerar-pdf', methods=['POST'])
```

---

Pronto! Com este guia você consegue resolver 99% dos problemas! 🚀

Se encontrar um erro novo que não está aqui, me avise para eu adicionar! 😊
