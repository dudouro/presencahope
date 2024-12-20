import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from cryptography.fernet import Fernet
import json


def obter_base():
    """
    Função para obter, processar e retornar a base de dados como um DataFrame.
    """
    # URL da planilha
    planilha = "https://docs.google.com/spreadsheets/d/1p-ibzJH1PfXGNNgCkK3E0aRn5sfERsDN6IEJ_gWyyTw/export?format=xlsx"

    # Convertendo para DataFrame
    df = pd.read_excel(planilha)

    # Renomeia as colunas para nomes mais práticos
    df.rename(
        columns={
            "Carimbo de data/hora": "timestamp",
            "Nome": "nome",
            "Data de Nascimento": "data_nascimento",
            "Telefone": "telefone",
            "Bairro de residência:": "bairro",
            "Você possui acompanhamento via discipulado?": "tem_discipulado",
            "  Você é membro da igreja?  ": "membro_igreja",
            "Você participa de algum pequeno grupo/célula?": "participa_celula"
        },
        inplace=True
    )

    # Remove a coluna 'timestamp', se não for mais necessária
    df.drop(columns=['timestamp'], inplace=True)

    # Calcula a idade e define a célula
    df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce')  # Converte para datetime
    df['idade'] = (datetime.now() - df['data_nascimento']).dt.days // 365

    # Define a célula com base na idade
    df['celula'] = df['idade'].apply(lambda x: 'Celula 18' if x >= 18 else 'Celula 14-17')

    # Adiciona colunas de latitude e longitude baseadas no bairro
    df['latitude'] = df['bairro'].map(lambda b: bairros_coordenadas.get(b, (None, None))[0])
    df['longitude'] = df['bairro'].map(lambda b: bairros_coordenadas.get(b, (None, None))[1])

    # Remove linhas onde não foi possível encontrar coordenadas
    df.dropna(subset=['latitude', 'longitude'], inplace=True)

    return df

# Função para converter o mês para português
def mes_em_portugues(mes):
    meses_pt = {
        "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", 
        "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto", 
        "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"
    }
    return meses_pt.get(mes, mes)  # Retorna o mês em português, ou o original se não encontrado

# Chave de descriptografia (INSERIR SUA CHAVE AQUI)
DECRYPT_KEY = "h3yOaT8eQDyJZ2Cz12eanXL3HbZYPPemN-Jseb7ITbI="

def obter_chave_firebase():
    """
    Descriptografa o arquivo de credenciais do Firebase e retorna os dados JSON.
    """
    try:
        f = Fernet(DECRYPT_KEY.encode())
        with open("chave.json.enc", "rb") as enc_file:
            encrypted_data = enc_file.read()
        decrypted_data = f.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"Erro ao obter chave Firebase: {e}")

def conectar_firebase():
    """
    Inicializa a conexão com o Firebase e retorna o cliente Firestore.
    """
    try:
        chave_descriptografada = obter_chave_firebase()
        if not firebase_admin._apps:
            cred = credentials.Certificate(chave_descriptografada)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        raise RuntimeError(f"Erro ao inicializar Firebase: {e}")

# Dicionário com bairros e suas coordenadas
bairros_coordenadas = {
    "Centro": [-18.917404, -48.276574],
    "Fundinho": [-18.924006, -48.283089],
    "Nossa Senhora Aparecida": [-18.905758, -48.267006],
    "Martins": [-18.909697, -48.282028],
    "Osvaldo Rezende": [-18.913097, -48.293288],
    "Bom Jesus": [-18.904120, -48.275747],
    "Brasil": [-18.893931, -48.262301],
    "Cazeca": [-18.914996, -48.265675],
    "Lídice": [-18.923595, -48.273731],
    "Daniel Fonseca": [-18.918147, -48.300211],
    "Tabajaras": [-18.927867, -48.287415],
    "Presidente Roosevelt": [-18.896854, -48.284960],
    "Jardim Brasília": [-18.897910, -48.303882],
    "São José": [-18.900799, -48.310918],
    "Marta Helena": [-18.879155, -48.267092],
    "Pacaembu": [-18.884854, -48.291606],
    "Santa Rosa": [-18.890273, -48.278343],
    "Residencial Gramado": [-18.873316, -48.290870],
    "Nossa Senhora das Graças": [-18.870330, -48.278422],
    "Minas Gerais": [-18.863756, -48.265750],
    "Distrito Industrial": [-18.870594, -48.300557],
    "Maravilha": [-18.887309, -48.301044],
    "Jaraguá": [-18.925024, -48.304100],
    "Planalto": [-18.934837, -48.313344],
    "Chácaras Tubalina": [-18.926063, -48.321387],
    "Chácaras Panorama": [-18.955764, -48.345369],
    "Luizote de Freitas": [-18.918974, -48.332674],
    "Jardim das Palmeiras": [-18.945681, -48.312090],
    "Jardim Patrícia": [-18.911045, -48.324883],
    "Jardim Holanda": [-18.958617, -48.315094],
    "Jardim Europa": [-18.939682, -48.339945],
    "Jardim Canaã": [-18.964314, -48.330534],
    "Mansour": [-18.930752, -48.336331],
    "Dona Zulmira": [-18.910210, -48.315472],
    "Taiaman": [-18.900737, -48.319787],
    "Guarani": [-18.890631, -48.329695],
    "Tocantins": [-18.899807, -48.334991],
    "Morada do Sol": [-18.893852, -48.349609],
    "Monte Hebron": [-18.972054, -48.349707],
    "Residencial Pequis": [-18.973381, -48.382989],
    "Morada Nova": [-18.992719, -48.371876],
    "Tubalina": [-18.935284, -48.299324],
    "Cidade Jardim": [-18.946216, -48.296460],
    "Nova Uberlândia": [-18.958781, -48.299418],
    "Patrimônio": [-18.935310, -48.286997],
    "Morada da Colina": [-18.942910, -48.279456],
    "Vigilato Pereira": [-18.930355, -48.269641],
    "Saraiva": [-18.921523, -48.265105],
    "Lagoinha": [-18.929759, -48.258900],
    "Carajás": [-18.930797, -48.249550],
    "Pampulha": [-18.935296, -48.242634],
    "Jardim Karaíba": [-18.946672, -48.266046],
    "Jardim Inconfidência": [-18.939472, -48.256373],
    "Santa Luzia": [-18.942034, -48.229829],
    "Granada": [-18.947963, -48.244162],
    "São Jorge": [-18.959289, -48.222557],
    "Laranjeiras": [-18.962840, -48.240489],
    "Shopping Park": [-18.980156, -48.274047],
    "Jardim Sul": [-18.961626, -48.262607],
    "Gávea": [-18.957389, -48.283430],
    "Santa Mônica": [-18.920334, -48.247070],
    "Tibery": [-18.903545, -48.245409],
    "Segismundo Pereira": [-18.927463, -48.226456],
    "Umuarama": [-18.883720, -48.258354],
    "Alto Umuarama": [-18.887543, -48.241053],
    "Custódio Pereira": [-18.896975, -48.240237],
    "Aclimação": [-18.875345, -48.231472],
    "Mansões Aeroporto": [-18.892239, -48.213632],
    "Alvorada": [-18.921460, -48.198759],
    "Novo Mundo": [-18.924960, -48.211172],
    "Morumbi": [-18.914442, -48.186779],
    "Residencial Integração": [-18.912522, -48.205694],
    "Morada dos Pássaros": [-18.862454, -48.215539],
    "Jardim Ipanema": [-18.885357, -48.224324],
    "Portal do Vale": [-18.902297, -48.201135],
    "Granja Marileusa": [-18.870826, -48.247069],
    "Grand Ville": [-18.902545, -48.217743]
}
