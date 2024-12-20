import streamlit as st
from datetime import datetime
from base import conectar_firebase

# Inicializa a conexão com o Firebase
try:
    db = conectar_firebase()
except Exception as e:
    st.error(f"Erro ao conectar com o Firebase: {e}")
    st.stop()

def salvar_discipulado(discipulador, discipulo, data, horario_insercao, observacoes):
    try:
        # Salvar na coleção `discipulados_presenca`
        registro_ref = db.collection("discipulados_presenca")  # Corrigido para a coleção correta

        # Criar um ID único para o registro
        data_atual = datetime.now()
        documento_id = f"DISC{data_atual.strftime('%d%m%Y%H%M%S')}".replace(" ", "_")

        # Dados para salvar
        registro_ref.document(documento_id).set({
            "discipulador": discipulador,
            "discipulo": discipulo,
            "data": data,
            "horario_insercao": horario_insercao,
            "observacoes": observacoes
        })

        st.success(f"Discipulado registrado com sucesso na coleção `discipulados_presenca`! Documento ID: {documento_id}")

    except Exception as e:
        st.error(f"Erro ao salvar o registro na coleção `discipulados_presenca`: {e}")

# Interface com Streamlit
st.title("Registro de Discipulado")

# Obter lista de discipuladores únicos da coleção `discipulados`
try:
    discipulados_docs = db.collection("discipulados").stream()
    discipuladores = list(set(doc.to_dict()["discipulador"] for doc in discipulados_docs))
    discipuladores.sort()  # Ordenar alfabeticamente
except Exception as e:
    st.error(f"Erro ao carregar discipuladores: {e}")
    discipuladores = []

# Selecionar discipulador
discipulador_selecionado = st.selectbox("Selecione o discipulador", discipuladores)

# Carregar discípulos associados ao discipulador
if discipulador_selecionado:
    try:
        discipulos_docs = db.collection("discipulados").where("discipulador", "==", discipulador_selecionado).stream()
        lista_discipulos = [doc.to_dict()["nome"] for doc in discipulos_docs]
        lista_discipulos.sort()  # Ordenar alfabeticamente
    except Exception as e:
        st.error(f"Erro ao carregar discípulos: {e}")
        lista_discipulos = []

    # Selecionar discípulo
    discipulo_selecionado = st.selectbox("Selecione o discípulo", lista_discipulos)

    # Selecionar data
    data_selecionada = st.date_input("Selecione a data", datetime.now().date())

    # Campo de observações
    observacoes = st.text_area("Observações (opcional)")

    # Botão para salvar registro
    if st.button("Registrar Discipulado"):
        horario_insercao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Horário da inserção
        salvar_discipulado(
            discipulador=discipulador_selecionado,
            discipulo=discipulo_selecionado,
            data=str(data_selecionada),
            horario_insercao=horario_insercao,
            observacoes=observacoes
        )
else:
    st.warning("Selecione um discipulador para continuar.")
