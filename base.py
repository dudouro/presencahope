import pandas as pd
import hashlib
from datetime import datetime


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

    # Função para criar um hash único baseado no timestamp
    def gerar_id_unico(timestamp):
        # Converte o valor para string antes de aplicar o hash
        return hashlib.md5(str(timestamp).encode()).hexdigest()

    # Aplica a função à coluna 'timestamp' para gerar o ID
    df['id'] = df['timestamp'].apply(gerar_id_unico)

    # Remove a coluna 'timestamp', se não for mais necessária
    df.drop(columns=['timestamp'], inplace=True)

    # Calcula a idade e define a célula
    df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce')  # Converte para datetime
    df['idade'] = (datetime.now() - df['data_nascimento']).dt.days // 365

    # Define a célula com base na idade
    df['celula'] = df['idade'].apply(lambda x: 'Celula 18' if x >= 18 else 'Celula 14-17')

    return df

# Função para converter o mês para português
def mes_em_portugues(mes):
    meses_pt = {
        "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", 
        "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto", 
        "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"
    }
    return meses_pt.get(mes, mes)  # Retorna o mês em português, ou o original se não encontrado

