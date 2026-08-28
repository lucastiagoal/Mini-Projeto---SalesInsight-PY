import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import re

print("\n=== RF01 ===")

def gerar_dataset_vendas(n_registros=200, seed=42): 
    """Gera um dataset sintetico de vendas com dados sujos.""" 
    random.seed(seed)
    np.random.seed(seed)
 
    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor", 
                "Teclado", "Mouse", "Headset"] 
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares", 
                  "Tablet": "Celulares", "Monitor": "Computadores", 
                  "Teclado": "Perifericos", "Mouse": "Perifericos", 
                  "Headset": "Perifericos"} 
    precos = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800, 
              "Monitor": 1200, "Teclado": 250, "Mouse": 120, 
              "Headset": 350} 
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    data_inicio = datetime(2025, 1, 1)
    dados = []
 
    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]
        quantidade = random.randint(1, 10)
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))
        data_txt = data.strftime("%Y-%m-%d")
        cliente = f"Cliente_{random.randint(1, 50):03d}"
 
        if random.random() < 0.05:
            quantidade = None                    
        if random.random() < 0.04:
            preco = None                         
        if random.random() < 0.06: 
            produto = "  " + produto + " "       
        if random.random() < 0.03: 
            data_txt = "DATA INVALIDA"           
        if random.random() < 0.10: 
            cliente = random.choice([            
                cliente.upper().replace("_", "-"), 
                cliente + "!!", 
                "  " + cliente, 
                cliente.replace("Cliente_", "cliente#"), 
            ]) 
 
        dados.append({ 
            "id_venda": i + 1, 
            "data_venda": data_txt, 
            "cliente": cliente, 
            "produto": produto, 
            "categoria": categoria, 
            "regiao": random.choice(regioes), 
            "quantidade": quantidade, 
            "preco_unitario": preco, 
        }) 
    return pd.DataFrame(dados) 

df_bruto = gerar_dataset_vendas() 
df_bruto.to_csv("vendas.csv", index=False) 
print(f"Dataset gerado com {len(df_bruto)} registros.") 
print(df_bruto.head())

print("\n=== RF02 ===")

def inspecionar_dados(df):
    """Exibe as informações estruturais do DataFrame."""
    print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados: \n{df.dtypes}")
    print(f"\nValores nulos por coluna: \n{df.isnull().sum()}")
    print(f"\nPrimeiros registros: \n{df.head()}")
    return df
df_bruto = inspecionar_dados(df_bruto)

print("\n=== RF03 ===")

def limpar_dados(df):
    """Limpa o DataFrame de vendas e retorna os dados limpos e um relatório."""

    df = df.copy()

    registros_iniciais = len(df)

    colunas_texto = ["cliente", "produto", "categoria", "regiao"]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].str.strip()

    df["data_venda"] = pd.to_datetime(
        df["data_venda"],
        errors="coerce"
    )

    removidos_data_invalida = df["data_venda"].isna().sum()

    df = df.dropna(subset=["data_venda"]).copy()

    antes_remover_nulos = len(df)

    df = df.dropna(subset=["quantidade", "preco_unitario"]).copy()

    df = df.reset_index(drop=True)

    removidos_nulos_criticos = antes_remover_nulos - len(df)

    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)

    padrao_cliente = re.compile(r"^cliente(\d{3})$", flags=re.IGNORECASE)

    def padronizar_cliente(valor):
        texto_limpo = re.sub(r"[^A-Za-z0-9]", "", str(valor).strip())

        resultado = padrao_cliente.fullmatch(texto_limpo)

        if resultado:
            numero_cliente = resultado.group(1)
            return f"Cliente_{numero_cliente}", True

        return texto_limpo, False

    resultado_clientes = df["cliente"].apply(padronizar_cliente)

    df["cliente"] = resultado_clientes.apply(lambda item: item[0])
    df["cliente_valido"] = resultado_clientes.apply(lambda item: item[1])

    clientes_fora_padrao = (~df["cliente_valido"]).sum()

    relatorio = {
        "registros_iniciais": registros_iniciais,
        "removidos_data_invalida": int(removidos_data_invalida),
        "removidos_nulos_criticos": int(removidos_nulos_criticos),
        "clientes_fora_padrao": int(clientes_fora_padrao),
        "registros_finais": len(df)
    }

    print("\n=== RELATÓRIO DE LIMPEZA ===")
    for item, quantidade in relatorio.items():
        print(f"{item}: {quantidade}")

    return df, relatorio
df_limpo, relatorio_limpeza = limpar_dados(df_bruto)
inspecionar_dados(df_limpo)

print("\n=== RF04 ===")

def criar_colunas_derivadas(df):
    """Cria colunas derivadas no DataFrame."""
    df = df.copy()

    df["receita_total"] = df["quantidade"] * df["preco_unitario"]

    df["mes"] = df["data_venda"].dt.month

    mes_nome = ({1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
                7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"})
    
    df["mes_nome"] = df["mes"].map(mes_nome)

    df["trimestre"] = "Q" + df["data_venda"].dt.quarter.astype(str)

    df["ano"] = df["data_venda"].dt.year

    condicoes = [
    df["receita_total"] < 500,
    (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
    df["receita_total"] >= 5000,
    ]
    faixas = ["Baixo Valor", "Medio Valor", "Alto Valor"]
    df["faixa_receita_item"] = np.select(condicoes, faixas, default="Nao Classificado")
    return df
df_transformado = criar_colunas_derivadas(df_limpo)
print(df_transformado.head())

print("\n=== RF05 ===")

def calcular_metricas(df):
    """Calcula as metricas agregadas do dataset."""
    df = df.copy()

    por_mes = (
        df.groupby(["mes", "mes_nome"], as_index=False)
        .agg(
            receita_total=("receita_total", "sum"),
            quantidade=("quantidade", "sum"),
            n_vendas=("id_venda", "count")
        )
        .sort_values("mes")
        .reset_index(drop=True)
    )

    top_produtos = (
        df.groupby("produto", as_index=False)
        .agg(receita_total=("receita_total", "sum"))
        .sort_values("receita_total", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    por_categoria = (
        df.groupby("categoria", as_index=False)
        .agg(receita_total=("receita_total", "sum"))
        .sort_values("receita_total", ascending=False)
        .reset_index(drop=True)
    )

    por_regiao = (
        df.groupby("regiao", as_index=False)
        .agg(
            receita_total=("receita_total", "sum"),
            ticket_medio=("receita_total", "mean")
        )
        .sort_values("receita_total", ascending=False)
        .reset_index(drop=True)
    )

    metricas = {
        "por_mes": por_mes,
        "top_produtos": top_produtos,
        "por_categoria": por_categoria,
        "por_regiao": por_regiao
    }
    return metricas
metricas = calcular_metricas(df_transformado)

print("\n=== POR MÊS ===")
print(metricas["por_mes"])
print("\n=== TOP PRODUTOS ===")
print(metricas["top_produtos"])
print("\n=== POR CATEGORIA ===")
print(metricas["por_categoria"])
print("\n=== POR REGIÃO ===")
print(metricas["por_regiao"])

print("\n=== RF06 ===")

def segmentar_clientes(df):
    """Agrupa clientes por total gasto e os classifica em segmentos."""

    clientes = (
        df.groupby("cliente", as_index=False)
        .agg(total_gasto=("receita_total", "sum"))
        .sort_values("total_gasto", ascending=False)
        .reset_index(drop=True)
    )

    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda gasto:
            "Bronze" if gasto < 5000
            else "Prata" if gasto <= 15000
            else "Ouro"
    )

    print("\n=== TOP 10 CLIENTES ===")
    print(clientes.head(10).to_string(index=False))

    print("\n=== DISTRIBUIÇÃO POR SEGMENTO ===")
    print(clientes["segmento"].value_counts())

    return clientes

clientes = segmentar_clientes(df_transformado)