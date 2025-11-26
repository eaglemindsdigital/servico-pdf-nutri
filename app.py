from flask import Flask, request, send_file, jsonify
import fitz
import os
import requests
from io import BytesIO

app = Flask(__name__)

TEMPLATE_FEMININO = "templates/plano-lead-feminino-otim.pdf"
TEMPLATE_MASCULINO = "templates/plano-lead-masculino-otim.pdf"
DRIVE_ID_FEMININO = "1F86FSyC-hFD9GMRoTLbyBSBek0XbtGRV"
DRIVE_ID_MASCULINO = "1j02pSYdmN1TaAOiF9TdWwDsyVAZArIX0"

def baixar_pdf_do_drive(file_id, caminho_destino):
    print(f"Baixando PDF do Google Drive (ID: {file_id})...")
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(caminho_destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"PDF baixado: {caminho_destino}")
        return True
    except Exception as e:
        print(f"Erro ao baixar PDF: {e}")
        return False

def inicializar_templates():
    print("=== INICIALIZANDO TEMPLATES ===")
    os.makedirs("templates", exist_ok=True)
    
    if not os.path.exists(TEMPLATE_FEMININO):
        print(f"PDF feminino nao encontrado, baixando...")
        baixar_pdf_do_drive(DRIVE_ID_FEMININO, TEMPLATE_FEMININO)
    else:
        print(f"PDF feminino ja existe: {TEMPLATE_FEMININO}")
    
    if not os.path.exists(TEMPLATE_MASCULINO):
        print(f"PDF masculino nao encontrado, baixando...")
        baixar_pdf_do_drive(DRIVE_ID_MASCULINO, TEMPLATE_MASCULINO)
    else:
        print(f"PDF masculino ja existe: {TEMPLATE_MASCULINO}")
    
    if os.path.exists(TEMPLATE_FEMININO) and os.path.exists(TEMPLATE_MASCULINO):
        print("=== TEMPLATES PRONTOS ===")
        return True
    else:
        print("=== ERRO: Templates nao encontrados ===")
        return False

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

# Inicializar templates quando o módulo for importado
print("Iniciando aplicacao Flask...")
inicializar_templates()

@app.route('/')
def home():
    templates_ok = os.path.exists(TEMPLATE_FEMININO) and os.path.exists(TEMPLATE_MASCULINO)
    return jsonify({
        "status": "online",
        "servico": "Gerador de PDF - Plano Nutricional",
        "endpoint": "/gerar-pdf",
        "metodo": "POST",
        "templates_disponiveis": templates_ok
    })

@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf():
    try:
        dados = request.json
        if not dados:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        campos_obrigatorios = ["NOME", "ID", "PRAZO", "PESO", "META KG", "GET", "ALTURA", "IDADE", "NAF", "SEXO"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo '{campo}' nao encontrado"}), 400

        sexo = dados["SEXO"].strip().upper()
        if sexo in ["FEMININO", "F", "MULHER", "FEMALE"]:
            arquivo_template = TEMPLATE_FEMININO
        elif sexo in ["MASCULINO", "M", "HOMEM", "MALE"]:
            arquivo_template = TEMPLATE_MASCULINO
        else:
            return jsonify({"erro": f"Sexo invalido: '{dados['SEXO']}'"}), 400

        print(f"Verificando template: {arquivo_template}")
        print(f"Arquivo existe: {os.path.exists(arquivo_template)}")
        
        if not os.path.exists(arquivo_template):
            print(f"ERRO: Template nao encontrado em {arquivo_template}")
            print(f"Arquivos em templates/: {os.listdir('templates') if os.path.exists('templates') else 'pasta nao existe'}")
            return jsonify({"erro": "Template nao encontrado", "caminho": arquivo_template}), 500

        doc = fitz.open(arquivo_template)
        page = doc[0]

        COR_BRANCO = (1, 1, 1)
        COR_PRETO = hex_to_rgb("#1E1E1E")
        COR_AZUL = hex_to_rgb("#002D3A")
        COR_BEGE = hex_to_rgb("#FFF1DA")

        try:
            peso = float(dados["PESO"])
            altura = float(dados["ALTURA"]) / 100
            imc = peso / (altura ** 2)
            imc_formatado = f"{imc:.2f}"
        except:
            imc_formatado = "N/A"

        page.insert_text((1275, 550), dados["NOME"], fontsize=80, fontname="Helvetica-Bold", color=COR_BRANCO)
        page.insert_text((630, 1660), dados["NOME"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1530, 1780), dados["ID"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1950, 1780), dados["PRAZO"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1050, 2180), dados["PESO"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1000, 2280), dados["META KG"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1750, 2280), dados["GET"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((680, 2400), dados["ALTURA"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((700, 2505), dados["IDADE"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1550, 2505), imc_formatado, fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1070, 2620), dados["NAF"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((900, 6080), dados["META KG"], fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((1150, 6080), "4", fontsize=64, fontname="Helvetica-Bold", color=COR_PRETO)
        page.insert_text((550, 13550), f"{dados['PESO']}kg", fontsize=100, fontname="Helvetica-Bold", color=COR_AZUL)
        page.insert_text((1850, 13550), f"{dados['META KG']}kg", fontsize=100, fontname="Helvetica-Bold", color=COR_BRANCO)
        page.insert_text((1275, 32150), dados["NOME"], fontsize=80, fontname="Helvetica-Bold", color=COR_BEGE)

        pdf_bytes = BytesIO()
        doc.save(pdf_bytes)
        doc.close()
        pdf_bytes.seek(0)

        nome_arquivo = f"PLANO_{dados['ID']}_{dados['NOME'].replace(' ', '_')}.pdf"
        print(f"PDF gerado com sucesso: {nome_arquivo}")
        
        return send_file(pdf_bytes, mimetype='application/pdf', as_attachment=True, download_name=nome_arquivo)

    except Exception as e:
        print(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
