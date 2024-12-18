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
        with open("./chave.json.enc", "rb") as enc_file:
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

# Função para listar os membros por célula
def listar_membros_por_celula(celula):
    try:
        # Obter a base de dados do Google Sheets
        df = obter_base()
        
        # Filtrar os membros da célula
        membros = df[df["celula"] == celula]["nome"].tolist()
        return membros
    except Exception as e:
        st.error(f"Erro ao listar membros: {e}")
        return []

# Função para listar os membros presentes de um registro de presença
def listar_membros_presentes(celula, data):
    try:
        presenca_ref = db.collection("celulas_presenca")
        registros = presenca_ref.where("celula", "==", celula).where("data", "==", data).stream()
        
        membros_presentes = []
        for registro in registros:
            membros_presentes.extend(registro.to_dict().get("membros_presentes", []))
        return list(set(membros_presentes))  # Remover duplicatas
    except Exception as e:
        st.error(f"Erro ao listar membros presentes: {e}")
        return []

# Função para editar presença
def editar_presenca(id_documento, novo_membros_presentes, novo_responsavel):
    try:
        presenca_ref = db.collection("celulas_presenca").document(id_documento)
        presenca_ref.update({
            "membros_presentes": novo_membros_presentes,
            "responsavel": novo_responsavel
        })
        st.success("Presença atualizada com sucesso!")
        
        # Atualizar a página após a edição
        st.rerun()
        
    except Exception as e:
        st.error(f"Erro ao editar presença: {e}")

# Função para listar os últimos 5 registros
def listar_ultimos_registros():
    try:
        presenca_ref = db.collection("celulas_presenca")
        registros = presenca_ref.order_by("horario_insercao", direction=firestore.Query.DESCENDING).limit(5).stream()
        return [registro for registro in registros]
    except Exception as e:
        st.error(f"Erro ao listar registros: {e}")
        return []

# Página de edição de presenças
def pagina_editar_presenca():
    st.title("Editar Presença")

    # Listar os 5 últimos registros
    registros = listar_ultimos_registros()

    if registros:
        st.subheader("Últimos 5 Registros de Presença")
        lista_opcoes = []
        for registro in registros:
            doc_id = registro.id
            data = registro.to_dict().get("data")
            membros = ", ".join(registro.to_dict().get("membros_presentes", []))
            responsavel = registro.to_dict().get("responsavel", "Não especificado")
            lista_opcoes.append(f"ID: {doc_id} | Data: {data} | Membros: {membros} | Responsável: {responsavel}")
        
        registro_selecionado = st.selectbox("Selecione um registro para editar", lista_opcoes)
        
        # Identificar o ID do registro selecionado
        id_selecionado = registro_selecionado.split(" | ")[0].split(": ")[1]
        
        # Carregar os dados do registro selecionado
        registro_dados = db.collection("celulas_presenca").document(id_selecionado).get()
        dados = registro_dados.to_dict()
        
        if registro_dados.exists:
            # Exibir os dados do registro para edição
            membros_atual = dados["membros_presentes"]
            responsavel_atual = dados["responsavel"]
            celula_atual = dados["celula"]
            
            st.subheader(f"Editar Registro - {id_selecionado}")
            
            # Carregar membros da célula selecionada
            membros_celula = listar_membros_por_celula(celula_atual)
            if not membros_celula:
                st.warning(f"Não há membros cadastrados para a célula {celula_atual}.")
            
            # Selecionar membros da célula
            # Mostrar os membros presentes e os membros restantes (não presentes)
            membros_restantes = [membro for membro in membros_celula if membro not in membros_atual]

            # Combinar membros presentes e não presentes
            membros_completos = membros_atual + membros_restantes

            # Membros presentes já serão selecionados
            novo_membros = st.multiselect(
                "Membros Presentes", 
                membros_completos, 
                default=membros_atual  # Membros já presentes devem estar selecionados
            )
            
            novo_responsavel = st.selectbox(
                "Responsável pela chamada", 
                ["Lucas", "Jhow", "Larissa", "Vitória"], 
                index=["Lucas", "Jhow", "Larissa", "Vitória"].index(responsavel_atual)
            )

            # Botão para salvar a edição
            if st.button("Salvar Edição"):
                editar_presenca(id_selecionado, novo_membros, novo_responsavel)
    else:
        st.warning("Não há registros para exibir.")
        
# Chamar a função de edição
pagina_editar_presenca()
