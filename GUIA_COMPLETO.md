# 🎯 GUIA COMPLETO - DEPLOY SERVIÇO PDF NA RAILWAY

## ✅ CHECKLIST INICIAL
- [ ] Tenho conta no GitHub (github.com)
- [ ] Tenho conta na Railway (railway.app)
- [ ] Tenho os 2 PDFs (feminino e masculino)
- [ ] Baixei a pasta `servico-pdf-nutri` que o Claude criou

---

## 📂 PASSO 1: ORGANIZAR ARQUIVOS (5 minutos)

### 1.1 Baixe a pasta `servico-pdf-nutri`
Você receberá uma pasta com:
```
servico-pdf-nutri/
├── app.py ✅
├── requirements.txt ✅
├── Procfile ✅
├── README.md ✅
├── .gitignore ✅
└── templates/ (VAZIA - você vai preencher)
```

### 1.2 Adicione seus PDFs
Copie seus 2 arquivos PDF para dentro da pasta `templates/`:

**IMPORTANTE:** Os nomes DEVEM ser exatamente:
- ✅ `plano-lead-feminino-otim.pdf`
- ✅ `plano-lead-masculino-otim.pdf`

Se seus arquivos tiverem nomes diferentes, RENOMEIE para esses nomes exatos!

### 1.3 (Opcional) Adicione a fonte
Se você tiver o arquivo `Montserrat-Bold.ttf`:
- Coloque na RAIZ da pasta (não dentro de templates)

Estrutura final:
```
servico-pdf-nutri/
├── app.py
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
├── Montserrat-Bold.ttf (opcional)
└── templates/
    ├── plano-lead-feminino-otim.pdf ✅
    └── plano-lead-masculino-otim.pdf ✅
```

---

## 🐙 PASSO 2: CRIAR REPOSITÓRIO NO GITHUB (10 minutos)

### 2.1 Criar repositório
1. Acesse: https://github.com/new
2. Nome do repositório: `servico-pdf-nutri`
3. Descrição: "Serviço de geração de PDFs nutricionais"
4. Deixe como: **Público**
5. NÃO marque "Add README" (já temos um)
6. Click "Create repository"

### 2.2 Fazer upload dos arquivos

**OPÇÃO A - Via Interface Web (Mais Fácil):**
1. Na página do repositório criado, click em "uploading an existing file"
2. Arraste TODA a pasta `servico-pdf-nutri` para a área
3. Aguarde o upload completar
4. No campo "Commit message", escreva: `Deploy inicial`
5. Click "Commit changes"

**OPÇÃO B - Via Git (Se você conhece):**
```bash
# Abra o terminal do Windows (Win + R, digite "cmd")
# Navegue até a pasta:
cd Desktop\servico-pdf-nutri

# Execute os comandos:
git init
git add .
git commit -m "Deploy inicial"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/servico-pdf-nutri.git
git push -u origin main
```

✅ **Checkpoint:** Você deve ver todos os arquivos no GitHub agora!

---

## 🚂 PASSO 3: FAZER DEPLOY NA RAILWAY (5 minutos)

### 3.1 Conectar GitHub com Railway
1. Acesse: https://railway.app
2. Faça login (se ainda não fez)
3. Click em **"New Project"**
4. Escolha **"Deploy from GitHub repo"**
5. Se for a primeira vez:
   - Click "Configure GitHub App"
   - Autorize a Railway a acessar seus repositórios
6. Selecione o repositório: **servico-pdf-nutri**

### 3.2 Aguardar deploy
- A Railway vai automaticamente:
  - ✅ Detectar que é Python
  - ✅ Instalar as dependências (Flask, PyMuPDF)
  - ✅ Executar o comando do Procfile
  - ✅ Deixar o serviço online

**Tempo de deploy:** 2-4 minutos

Você verá logs assim:
```
Building...
Installing dependencies...
Starting web server...
✅ Deployed successfully
```

### 3.3 Obter a URL do serviço
1. No painel da Railway, click no seu projeto
2. Vá na aba **"Settings"**
3. Procure por **"Domains"** ou **"Public Networking"**
4. Click em **"Generate Domain"**
5. Copie a URL gerada (exemplo: `https://servico-pdf-nutri-production.up.railway.app`)

✅ **Checkpoint:** Acesse a URL no navegador. Deve aparecer:
```json
{
  "status": "online",
  "servico": "Gerador de PDF - Plano Nutricional",
  "endpoint": "/gerar-pdf",
  "metodo": "POST"
}
```

---

## 🧪 PASSO 4: TESTAR O SERVIÇO (10 minutos)

### 4.1 Teste simples via navegador
Acesse: `https://sua-url.railway.app/`

Deve mostrar status online.

### 4.2 Teste completo no n8n

**Crie um workflow simples:**

1. **Manual Trigger** (para testar)
2. **Set Node** (para criar dados de teste):
```json
{
  "NOME": "Maria Silva",
  "SEXO": "Feminino",
  "ID": "12345",
  "PRAZO": "15/12/2025",
  "PESO": "70",
  "META KG": "65",
  "GET": "2200",
  "ALTURA": "165",
  "IDADE": "30",
  "NAF": "Moderado"
}
```

3. **HTTP Request Node**:
   - Method: `POST`
   - URL: `https://sua-url.railway.app/gerar-pdf`
   - Body Content Type: `JSON`
   - Body: (mapeie os campos do Set anterior)
   - Response Format: **"File"** (IMPORTANTE!)

4. Execute o workflow!

**Resultado esperado:**
- ✅ Status 200
- ✅ Arquivo PDF no output
- ✅ Nome: `PLANO_12345_Maria_Silva.pdf`

### 4.3 Teste com ambos os sexos

Execute 2 vezes mudando apenas:
- Teste 1: `"SEXO": "Feminino"` → Deve usar template feminino
- Teste 2: `"SEXO": "Masculino"` → Deve usar template masculino

---

## 🔧 PASSO 5: INTEGRAR COM SEU WORKFLOW REAL

Agora que está funcionando, adicione ao seu workflow existente:

```
[Trigger WhatsApp] → [Processar dados] → [HTTP Request - Gerar PDF] → [Enviar WhatsApp]
```

**No HTTP Request:**
- Mapeie `SEXO` do seu Google Sheets ou input
- URL: sua URL da Railway
- Response Format: File

---

## 📊 MONITORAMENTO

### Como ver logs de erro:
1. Acesse Railway → Seu projeto
2. Aba **"Deployments"**
3. Click no deployment ativo
4. Veja os logs em tempo real

### Erros comuns:

**Erro: "Template não encontrado"**
→ Verifique se os PDFs estão em `templates/` com nomes corretos

**Erro: "Campo X não encontrado"**
→ Certifique-se de enviar todos os campos obrigatórios

**Erro: "Sexo inválido"**
→ Use exatamente: Masculino, M, Feminino ou F

---

## 🔄 COMO ATUALIZAR NO FUTURO

### Mudou algum campo no PDF?
1. Edite `app.py` no GitHub
2. Altere as coordenadas na lista `campos`
3. Commit → Railway redeploya automaticamente

### Quer adicionar novo campo?
1. Adicione em `campos_obrigatorios`
2. Adicione na lista `campos` com X, Y, texto
3. Commit e push

### Quer trocar os PDFs?
1. Substitua os arquivos em `templates/`
2. Commit e push
3. Railway atualiza automaticamente

---

## 🎉 PRONTO!

Seu serviço está no ar 24/7 gerando PDFs automaticamente!

**Custos:**
- GitHub: Grátis
- Railway: Grátis até 500 horas/mês (suficiente para começar)

**Performance:**
- Cada PDF gera em ~2-3 segundos
- Pode gerar centenas por dia sem problemas

---

## 🆘 PRECISA DE AJUDA?

Se algo der errado, me envie:
1. Print do erro no n8n
2. Print dos logs da Railway
3. Um exemplo do JSON que você está enviando

Vou te ajudar a debugar! 🚀
