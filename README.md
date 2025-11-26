# 🚀 SERVIÇO DE GERAÇÃO DE PDF - PLANOS NUTRICIONAIS

## 📋 INSTRUÇÕES DE INSTALAÇÃO

### PASSO 1: Organizar arquivos
Coloque nesta pasta:

1. ✅ Seus 2 PDFs templates:
   - `templates/plano-lead-feminino-otim.pdf`
   - `templates/plano-lead-masculino-otim.pdf`

2. ✅ (Opcional) Fonte Montserrat:
   - `Montserrat-Bold.ttf` (na raiz)

### PASSO 2: Fazer upload no GitHub

```bash
# Abra o terminal nesta pasta e execute:
git init
git add .
git commit -m "Deploy serviço PDF"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/servico-pdf-nutri.git
git push -u origin main
```

### PASSO 3: Deploy na Railway
1. Acesse: https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Selecione o repositório `servico-pdf-nutri`
4. Aguarde o deploy (2-3 minutos)
5. Copie a URL gerada (ex: https://seu-app.railway.app)

### PASSO 4: Testar no n8n

**Endpoint:** `POST /gerar-pdf`

**Campos obrigatórios no JSON:**
```json
{
  "NOME": "Pedro Dual",
  "SEXO": "Masculino",  ← NOVO! Aceita: Masculino/M/Feminino/F
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

**Lógica de escolha do PDF:**
- SEXO = "Feminino", "F", "Mulher" → usa `plano-lead-feminino-otim.pdf`
- SEXO = "Masculino", "M", "Homem" → usa `plano-lead-masculino-otim.pdf`

---

## 🔧 COMO FUNCIONA

```
n8n envia dados → API recebe → Verifica SEXO → 
Escolhe PDF correto → Preenche campos → Retorna PDF pronto
```

---

## ❓ DÚVIDAS COMUNS

**P: E se eu quiser adicionar mais campos no futuro?**
R: Edite o `app.py`, adicione na lista `campos` e faça novo deploy.

**P: Posso testar localmente antes?**
R: Sim!
```bash
pip install -r requirements.txt
python app.py
# Acesse: http://localhost:5000
```

**P: Como atualizar depois?**
R: Edite os arquivos, faça commit e push. Railway redeploya automaticamente.

---

## 📞 SUPORTE
Criado por: Claude + Eagle Minds
Data: Novembro 2025
