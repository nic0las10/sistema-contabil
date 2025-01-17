import pandas as pd
import random
from faker import Faker

# Inicializa o gerador de dados fictícios
fake = Faker()

# Função para gerar transações bancárias
def gerar_transacoes_bancarias(qtd):
    transacoes = []
    for _ in range(qtd):
        transacoes.append({
            "data": fake.date_between(start_date="-1y", end_date="today"),
            "descricao": fake.catch_phrase(),
            "valor": round(random.uniform(100, 5000), 2),
            "tipo": random.choice(["Receita", "Despesa"])
        })
    return pd.DataFrame(transacoes)

# Gera 100 transações bancárias fictícias
transacoes_df = gerar_transacoes_bancarias(100)

# Salva em CSV
transacoes_df.to_csv("transacoes_bancarias.csv", index=False)
print("Transações bancárias geradas e salvas em 'transacoes_bancarias.csv'")

# Salva em Excel
transacoes_df.to_excel("transacoes_bancarias.xlsx", index=False, sheet_name="Transações Bancárias")
print("Transações bancárias geradas e salvas em 'transacoes_bancarias.xlsx'")

# Função para gerar registros contábeis com base nas transações bancárias
def gerar_registros_contabeis(transacoes_df):
    registros = []
    for _, transacao in transacoes_df.iterrows():
        # Criamos discrepâncias em algumas transações
        valor_ajustado = transacao["valor"]
        if random.random() < 0.2:  # 20% de chance de discrepância
            valor_ajustado += round(random.uniform(-50, 50), 2)  # Pequeno ajuste no valor
        
        registros.append({
            "data": transacao["data"],
            "descricao": transacao["descricao"],
            "valor": valor_ajustado,
            "tipo": transacao["tipo"]
        })

    return pd.DataFrame(registros)

# Gerar registros contábeis com base nas transações bancárias
registros_contabeis_df = gerar_registros_contabeis(transacoes_df)

# Salvar em CSV
registros_contabeis_df.to_csv("registros_contabeis.csv", index=False)
print("Registros contábeis gerados e salvos em 'registros_contabeis.csv'")

# Salvar em Excel
registros_contabeis_df.to_excel("registros_contabeis.xlsx", index=False, sheet_name="Registros Contábeis")
print("Registros contábeis gerados e salvos em 'registros_contabeis.xlsx'")

# Função para reconciliar transações bancárias com registros contábeis
def reconciliar_dados(transacoes_df, registros_df):
    # Faz a mesclagem (merge) dos dados com base na data e descrição
    reconciliacao = pd.merge(
        transacoes_df, registros_df,
        on=["data", "descricao", "tipo"],  # Colunas usadas como chave para combinar
        suffixes=('_bancario', '_contabil'),
        how='outer',  # Inclui tudo para detectar discrepâncias
        indicator=True  # Adiciona coluna para mostrar de onde veio cada linha
    )
    
    # Adiciona coluna para diferenças nos valores
    reconciliacao["diferenca_valor"] = reconciliacao["valor_bancario"].fillna(0) - reconciliacao["valor_contabil"].fillna(0)

    # Substituir valores na coluna _merge para algo mais amigável
    if reconciliacao["_merge"].dtype.name == "category":
        reconciliacao["_merge"] = reconciliacao["_merge"].cat.rename_categories({
            "both": "Conciliado",
            "left_only": "Apenas Bancário",
            "right_only": "Apenas Contábil"
        })
    else:
        reconciliacao["_merge"] = reconciliacao["_merge"].replace({
            "both": "Conciliado",
            "left_only": "Apenas Bancário",
            "right_only": "Apenas Contábil"
        })

    # Renomear colunas para cabeçalhos claros
    reconciliacao.rename(columns={
        "data": "Data",
        "descricao": "Descrição",
        "valor_bancario": "Valor Bancário",
        "valor_contabil": "Valor Contábil",
        "diferenca_valor": "Diferença de Valor",
        "_merge": "Status da Conciliacao"
    }, inplace=True)

    # Formatar os valores
    reconciliacao["Data"] = pd.to_datetime(reconciliacao["Data"]).dt.strftime('%d/%m/%Y')
    reconciliacao["Valor Bancário"] = reconciliacao["Valor Bancário"].round(2)
    reconciliacao["Valor Contábil"] = reconciliacao["Valor Contábil"].round(2)
    reconciliacao["Diferença de Valor"] = reconciliacao["Diferença de Valor"].round(2)
    
    return reconciliacao

# Executa a função de reconciliação
reconciliacao_df = reconciliar_dados(transacoes_df, registros_contabeis_df)

# Salva o resultado em Excel
reconciliacao_df.to_excel("reconciliacao_contabil.xlsx", index=False, sheet_name="Reconciliação")
print("Reconciliação realizada e salva como 'reconciliacao_contabil.xlsx'")
