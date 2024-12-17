import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from base import obter_base  # Importa a função obter_base de outro arquivo

# Inicializar o Firebase
cred = credentials.Certificate("firebase-key.json")  # Caminho do seu arquivo de credenciais do Firebase
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Obter referência ao banco de dados Firestore
db = firestore.client()

def salvar_presenca(celula, data, membros_presentes, horario_insercao):
    try:
        presenca_ref = db.collection("celulas_presenca")
        
        # Salvar presença no Firestore
        presenca_ref.add({
            "celula": celula,
            "data": data,  # Data da célula
            "membros_presentes": membros_presentes,  # Membros presentes
            "horario_insercao": horario_insercao  # Horário da inserção
        })
        
        print("Presença salva com sucesso")

        # Exibir a mensagem de sucesso
        st.success("Chamada feita com sucesso!")

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
