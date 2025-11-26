from flask import Flask, request, send_file, jsonify
import fitz  # PyMuPDF
import os
import requests
from io import BytesIO

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
TEMPLATE_FEMININO = "templates/plano-lead-feminino-otim.pdf"
TEMPLATE_MASCULINO = "templates/plano-lead-masculino-otim.pdf"
ARQUIVO_FONTE = "Montserrat-Bold.ttf"

# IDs dos arquivos no Google Drive
DRIVE_ID_FEMININO = "1F86FSyC-hFD9GMRoTLbyBSBek0XbtGRV"
DRIVE_ID_MASCULINO = "1j02pSYdmN1TaAOiF9TdWwDsyVAZArIX0"

# Verifica se a fonte existe
TEM_FONTE_CUSTOMIZADA = os.path.exists(ARQUIVO_FONTE)
NOME_FONTE = "Montserrat-Bold" if TEM_FONTE_CUSTOMIZADA else "Helvetica-Bold"
FONTE_PATH = ARQUIVO_FONTE if TEM_FONTE_CUSTOMIZADA else None

def baixar_pdf_do_drive(file_id, caminho_destino):
    """Baixa um arquivo PDF do Google Drive"""
    print(f"📥 Baixando PDF do Google Drive (ID: {file_id})...")
    
    # URL de download direto do Google Drive
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        # Fazer download do arquivo
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Salvar o arquivo
        with open(caminho_destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ PDF baixado com sucesso: {caminho_destino}")
        return True
    except Exception as e:
        print(f"❌ Erro ao baixar PDF: {e}")
        return False

def inicializar_templates():
    """Baixa os PDFs do Google Drive se não existirem localmente"""
    print("=" * 50)
    print("🚀 INICIALIZANDO TEMPLATES...")
    print("=" * 50)
    
    # Criar pasta templates se não existir
    os.makedirs("templates", exist_ok=True)
    print("✅ Pasta 'templates/' criada/verificada")
    
    # Baixar PDF feminino se não existir
    if not os.path.exists(TEMPLATE_FEMININO):
        print(f"⚠️ PDF feminino não encontrado localmente. Baixando do Drive...")
        baixar_pdf_do_drive(DRIVE_ID_FEMININO, TEMPLATE_FEMININO)
    else:
        print(f"✅ PDF feminino já existe: {TEMPLATE_FEMININO}")
    
    # Baixar PDF masculino se não existir
    if not os.path.exists(TEMPLATE_MASCULINO):
        print(f"⚠️ PDF masculino não encontrado localmente. Baixando do Drive...")
        baixar_pdf_do_drive(DRIVE_ID_MASCULINO, TEMPLATE_MASCULINO)
    else:
        print(f"✅ PDF masculino já existe: {TEMPLATE_MASCULINO}")
    
    # Verificar se ambos existem agora
    if os.path.exists(TEMPLATE_FEMININO) and os.path.exists(TEMPLATE_MASCULINO):
        print("=" * 50)
        print("✅ TEMPLATES PRONTOS!")
        print(f"   - Feminino: {os.path.getsize(TEMPLATE_FEMININO) / 1024 / 1024:.2f} MB")
        print(f"   - Masculino: {os.path.getsize(TEMPLATE_MASCULINO) / 1024 / 1024:.2f} MB")
        print("=" * 50)
        return True
    else:
        print("=" * 50)
        print("❌ ERRO: Não foi possível baixar os templates!")
        print("=" * 50)
        return False

def hex_to_rgb(hex_color):
    """Converte Hex para RGB do PyMuPDF"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def escrever_centralizado_forca_bruta(page, texto, x1, x2, y_base, tamanho_maximo, cor, centro_vertical=False):
    largura_disponivel = x2 - x1
    centro_da_area = x1 + (largura_disponivel / 2)
    tamanho_atual = tamanho_maximo
    
    while True:
        if TEM_FONTE_CUSTOMIZADA:
            largura_texto = fitz.get_text_length(texto, fontname=NOME_FONTE, fontfile=FONTE_PATH, fontsize=tamanho_atual)
        else:
            largura_texto = fitz.get_text_length(texto, fontname=NOME_FONTE, fontsize=tamanho_atual)

        if largura_texto <= (largura_disponivel - 10) or tamanho_atual <= 10:
            break
        tamanho_atual -= 2

    posicao_x = centro_da_area - (largura_texto / 2)
    posicao_y = y_base + (tamanho_atual * 0.35) if centro_vertical else y_base

    if TEM_FONTE_CUSTOMIZADA:
        page.insert_text(point=(posicao_x, posicao_y), text=texto, fontsize=tamanho_atual, 
                        fontname=NOME_FONTE, fontfile=FONTE_PATH, color=cor)
    else:
        page.insert_text(point=(posicao_x, posicao_y), text=texto, fontsize=tamanho_atual, 
                        fontname=NOME_FONTE, color=cor)

def inserir_campo_fixo(page, item):
    """Função auxiliar para tratar inserção com ou sem fonte customizada"""
    args = {
        "point": (item["x"], item["y"]),
        "text": item["texto"],
        "fontsize": item["size"],
        "color": item["cor"],
        "fontname": NOME_FONTE
    }
    if TEM_FONTE_CUSTOMIZADA:
        args["fontfile"] = FONTE_PATH
        
    page.insert_text(**args)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "servico": "Gerador de PDF - Plano Nutricional",
        "endpoint": "/gerar-pdf",
        "metodo": "POST",
        "templates": {
            "feminino": os.path.exists(TEMPLATE_FEMININO),
            "masculino": os.path.exists(TEMPLATE_MASCULINO)
        }
    })

@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf():
    try:
        # Receber dados do n8n
        dados = request.json
        
        if not dados:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        # Validar campos obrigatórios
        campos_obrigatorios = ["NOME", "ID", "PRAZO", "PESO", "META KG", "GET", 
                              "ALTURA", "IDADE", "NAF", "SEXO"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo '{campo}' não encontrado"}), 400

        # ===== ESCOLHER TEMPLATE BASEADO NO SEXO =====
        sexo = dados["SEXO"].strip().upper()
        
        if sexo in ["FEMININO", "F", "MULHER", "FEMALE"]:
            arquivo_template = TEMPLATE_FEMININO
            tipo_template = "feminino"
        elif sexo in ["MASCULINO", "M", "HOMEM", "MALE"]:
            arquivo_template = TEMPLATE_MASCULINO
            tipo_template = "masculino"
        else:
            return jsonify({
                "erro": f"Sexo inválido: '{dados['SEXO']}'. Use: 'Feminino', 'Masculino', 'F' ou 'M'"
            }), 400

        # Verificar se template existe
        if not os.path.exists(arquivo_template):
            return jsonify({
                "erro": f"Template {tipo_template} não encontrado",
                "caminho": arquivo_template
            }), 500

        # Abrir o PDF template escolhido
        print(f"📄 Abrindo template {tipo_template}...")
        doc = fitz.open(arquivo_template)
        page = doc[0]

        # --- CORES ---
        COR_AZUL_ESCURO = hex_to_rgb("#002D3A")
        COR_BRANCO = (1, 1, 1)
        COR_PRETO_SUAVE = hex_to_rgb("#1E1E1E")
        COR_BEGE_CLARO = hex_to_rgb("#FFF1DA")
        TAMANHO_PADRAO = 64

        # Calcular IMC
        try:
            peso = float(dados["PESO"])
            altura = float(dados["ALTURA"]) / 100  # cm para metros
            imc = peso / (altura ** 2)
            imc_formatado = f"{imc:.2f}"
        except:
            imc_formatado = "N/A"

        # --- 1. CABEÇALHO ---
        escrever_centralizado_forca_bruta(
            page=page,
            texto=dados["NOME"],
            x1=600, x2=1950, y_base=550, 
            tamanho_maximo=100, cor=COR_BRANCO
        )

        # --- 2. CAMPOS FIXOS ---
        campos = [
            # Dados Pessoais
            {"x": 630,  "y": 1660, "texto": dados["NOME"],      "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE}, 
            {"x": 1530, "y": 1780, "texto": dados["ID"],        "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE}, 
            {"x": 1950, "y": 1780, "texto": dados["PRAZO"],     "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE}, 

            # Métricas
            {"x": 1050, "y": 2180, "texto": dados["PESO"],      "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE}, 
            {"x": 1000, "y": 2280, "texto": dados["META KG"],   "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE}, 
            {"x": 1750, "y": 2280, "texto": dados["GET"],       "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE},
            {"x": 680,  "y": 2400, "texto": dados["ALTURA"],    "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE},
            {"x": 700,  "y": 2505, "texto": dados["IDADE"],     "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE},
            {"x": 1550, "y": 2505, "texto": imc_formatado,      "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE},
            {"x": 1070, "y": 2620, "texto": dados["NAF"],       "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE},

            # Meta
            {"x": 900,  "y": 6080, "texto": dados["META KG"],   "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE}, 
            {"x": 1150, "y": 6080, "texto": "4",                "size": TAMANHO_PADRAO, "cor": COR_PRETO_SUAVE}, 

            # Rodapé Peso
            {"x": 550,  "y": 13550, "texto": f"{dados['PESO']}kg", "size": 100, "cor": COR_AZUL_ESCURO},
            {"x": 1850, "y": 13550, "texto": f"{dados['META KG']}kg", "size": 100, "cor": COR_BRANCO},
        ]

        for item in campos:
            inserir_campo_fixo(page, item)

        # --- 3. ASSINATURA ---
        escrever_centralizado_forca_bruta(
            page=page,
            texto=dados["NOME"],
            x1=600, x2=1950, y_base=32150,
            tamanho_maximo=100, cor=COR_BEGE_CLARO,
            centro_vertical=False
        )

        # Salvar em memória (BytesIO)
        pdf_bytes = BytesIO()
        doc.save(pdf_bytes)
        doc.close()
        pdf_bytes.seek(0)

        # Retornar o PDF
        nome_arquivo = f"PLANO_{dados['ID']}_{dados['NOME'].replace(' ', '_')}.pdf"
        
        print(f"✅ PDF gerado com sucesso: {nome_arquivo}")
        
        return send_file(
            pdf_bytes,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nome_arquivo
        )

    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    # Inicializar templates antes de iniciar o servidor
    if not inicializar_templates():
        print("⚠️ AVISO: Serviço iniciando sem templates!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

## 📝 AGORA VOCÊ PRECISA:

1. **Ir para o GitHub**: https://github.com/eaglemindsdigital/servico-pdf-nutri
2. **Deletar a pasta `templates/`** (já que os PDFs vão vir do Drive agora):
   - Não consegue deletar pasta inteira, então delete os arquivos dentro dela
3. **Editar o `app.py`**:
   - Click em `app.py` → lápis ✏️
   - Delete todo o conteúdo
   - Cole o código acima
   - Commit: `Atualizar para usar Google Drive`

---

## ⏱️ DEPOIS DO COMMIT:

1. Railway vai fazer redeploy (3-4 minutos)
2. Nos logs você vai ver:
```
📥 Baixando PDF do Google Drive...
✅ PDF baixado com sucesso
✅ TEMPLATES PRONTOS!
