import streamlit as st
from datetime import datetime
from base import obter_base, conectar_firebase

# Inicializa a conexão com o Firebase
try:
    db = conectar_firebase()
except Exception as e:
    st.error(f"Erro ao conectar com o Firebase: {e}")
    st.stop()

# Obtendo a base de dados da planilha
df = obter_base()

def salvar_presenca(celula, data, membros_presentes, horario_insercao, responsavel):
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
            "horario_insercao": horario_insercao,  # Horário da inserção
            "responsavel": responsavel  # Nome do responsável pela chamada
        })
        
        print(f"Presença salva com sucesso! ID do documento: {documento_id}")

        # Exibir a mensagem de sucesso
        st.success(f"Chamada feita com sucesso! Documento ID: {documento_id}")

    except Exception as e:
        print(f"Erro ao salvar presença: {e}")
        st.error(f"Erro ao salvar presença: {e}")  # Exibir erro no caso de falha

# Interface com Streamlit
st.title("Controle de Presença - Células")

# Selecionar célula
celulas = df["celula"].unique()  # Lista de células disponíveis
celula_selecionada = st.selectbox("Selecione a célula", celulas)

# Selecionar data
data_selecionada = st.date_input("Selecione a data", datetime.now().date())

# Selecionar responsável pela chamada
responsaveis = ["Lucas", "Jhow", "Larissa", "Vitória"]  # Lista de opções de responsáveis
responsavel_selecionado = st.selectbox("Selecione o responsável pela chamada", responsaveis)

# Carregar membros da célula selecionada
if celula_selecionada:
    st.subheader(f"Membros da célula: {celula_selecionada}")
    membros = df[df["celula"] == celula_selecionada]["nome"].tolist()
    
    if membros:
        membros_presentes = st.multiselect("Selecione os membros presentes", membros)

        # Salvar presença no Firebase
        if st.button("Salvar Presença"):
            horario_insercao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Horário da inserção
            salvar_presenca(
                celula=celula_selecionada, 
                data=str(data_selecionada), 
                membros_presentes=membros_presentes, 
                horario_insercao=horario_insercao, 
                responsavel=responsavel_selecionado
            )
    else:
        st.warning("Nenhum membro encontrado para esta célula.")