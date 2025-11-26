FROM python:3.9-slim

# Instalar dependências do sistema necessárias para PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Expor porta
EXPOSE 5000

# Comando para iniciar o servidor
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
