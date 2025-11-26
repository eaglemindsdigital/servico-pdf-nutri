FROM python:3.9-slim

# Instalar dependências do sistema necessárias para PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache de build)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar TODA a aplicação (incluindo templates/)
COPY . .

# Verificar se os arquivos foram copiados (DEBUG)
RUN echo "=== Verificando arquivos copiados ===" && \
    ls -la && \
    echo "=== Conteúdo de templates/ ===" && \
    ls -la templates/ && \
    echo "=== Testando abertura dos PDFs ===" && \
    python3 -c "import fitz; print('PDF Feminino OK' if fitz.open('templates/plano-lead-feminino-otim.pdf') else 'ERRO'); print('PDF Masculino OK' if fitz.open('templates/plano-lead-masculino-otim.pdf') else 'ERRO')"

# Expor porta
EXPOSE 5000

# Comando para iniciar o servidor
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

5. Embaixo, escreva: `Corrigir Dockerfile para copiar templates corretamente`
6. Click em **"Commit changes"**

---

## ⏱️ AGUARDE O NOVO DEPLOY

Depois do commit:

1. A Railway vai fazer um novo build (3-5 minutos)
2. Durante o build, você vai ver nos **Build Logs** a saída do comando de verificação
3. Se tudo estiver OK, vai aparecer:
```
   === Verificando arquivos copiados ===
   === Conteúdo de templates/ ===
   plano-lead-feminino-otim.pdf
   plano-lead-masculino-otim.pdf
   === Testando abertura dos PDFs ===
   PDF Feminino OK
   PDF Masculino OK
