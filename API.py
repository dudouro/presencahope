import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from base import obter_base  # Importa a função obter_base de outro arquivo
from cryptography.fernet import Fernet
import json  # Importação necessária para trabalhar com JSON

# Chave de descriptografia (INSERIR SUA CHAVE AQUI)
DECRYPT_KEY = "h3yOaT8eQDyJZ2Cz12eanXL3HbZYPPemN-Jseb7ITbI="  # Substitua por sua chave gerada

# Função para descriptografar a chave
def obter_chave_firebase():
    try:
        # Inicializar o objeto Fernet com a chave fixa
        f = Fernet(DECRYPT_KEY.encode())

        # Ler o arquivo criptografado
        with open("chave.json.enc", "rb") as enc_file:
            encrypted_data = enc_file.read()

        # Descriptografar a chave
        decrypted_data = f.decrypt(encrypted_data)

        # Converter o JSON para um dicionário
        return json.loads(decrypted_data.decode("utf-8"))
    except Exception as e:
        st.error(f"Erro ao obter chave Firebase: {e}")
        raise e

# Inicializar o Firebase
try:
    # Obter a chave descriptografada como dicionário
    chave_descriptografada = obter_chave_firebase()

    # Inicializar Firebase usando a chave descriptografada
    if not firebase_admin._apps:
        cred = credentials.Certificate(chave_descriptografada)
        firebase_admin.initialize_app(cred)

    # Obter referência ao Firestore
    db = firestore.client()
except Exception as e:
    st.error(f"Erro ao inicializar Firebase: {e}")
    raise e

def salvar_presenca(celula, data, membros_presentes, horario_insercao):
    try:
        presenca_ref = db.collection("celulas_presenca")

        # Obter número de membros na célula e formatar com 3 dígitos
        numero_membros = len(membros_presentes)
        numero_membros_formatado = f"{numero_membros:03}"  # Formato de 3 dígitos (ex: 001, 015)

        # Definir prefixo baseado na célula
        if celula == "Celula 14-17":
            prefixo = "17"
        elif celula == "Celula 18":
            prefixo = "18"
        else:
            prefixo = "00"  # Prefixo padrão para células não especificadas

        # Criar um ID organizado: CEL + data atual no formato DDMMYYYY + prefixo + número de membros
        data_atual = datetime.now()
        documento_id = f"CEL{data_atual.strftime('%d%m%Y')}{prefixo}{numero_membros_formatado}"

        # Salvar presença no Firestore com ID personalizado
        presenca_ref.document(documento_id).set({
            "celula": celula,
            "data": data,  # Data da célula
            "membros_presentes": membros_presentes,  # Membros presentes
            "horario_insercao": horario_insercao  # Horário da inserção
        })
        
        print(f"Presença salva com sucesso! ID do documento: {documento_id}")

        # Exibir a mensagem de sucesso
        st.success(f"Chamada feita com sucesso! Documento ID: {documento_id}")

    except Exception as e:
        print(f"Erro ao salvar presença: {e}")
        st.error(f"Erro ao salvar presença: {e}")  # Exibir erro no caso de falha


# Interface com Streamlit
st.title("Controle de Presença - Células")

# Obter base de dados do Google Sheets
df = obter_base()

# Selecionar célula
celulas = df["celula"].unique()  # Lista de células disponíveis
celula_selecionada = st.selectbox("Selecione a célula", celulas)

# Selecionar data
data_selecionada = st.date_input("Selecione a data", datetime.now().date())

# Carregar membros da célula selecionada
if celula_selecionada:
    st.subheader(f"Membros da célula: {celula_selecionada}")
    membros = df[df["celula"] == celula_selecionada]["nome"].tolist()
    
    if membros:
        membros_presentes = st.multiselect("Selecione os membros presentes", membros)

        # Salvar presença no Firebase
        if st.button("Salvar Presença"):
            horario_insercao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Horário da inserção
            salvar_presenca(celula_selecionada, str(data_selecionada), membros_presentes, horario_insercao)
    else:
        st.warning("Nenhum membro encontrado para esta célula.")
