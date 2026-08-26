import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import re

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
 
        # --- sujeira proposital para a etapa de limpeza --- 
        if random.random() < 0.05:
            quantidade = None                    # valor nulo 
        if random.random() < 0.04:
            preco = None                         # valor nulo 
        if random.random() < 0.06: 
            produto = "  " + produto + " "       # espacos extras 
        if random.random() < 0.03: 
            data_txt = "DATA INVALIDA"           # data invalida 
        if random.random() < 0.10: 
            cliente = random.choice([            # ruido no nome 
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

# Gerar e salvar o CSV bruto 
df_bruto = gerar_dataset_vendas() 
df_bruto.to_csv("vendas.csv", index=False) 
print(f"Dataset gerado com {len(df_bruto)} registros.") 
print(df_bruto.head())

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

def limpar_dados(df):
    """Limpa o DataFrame de vendas e retorna os dados limpos e um relatório."""

    # Evita alterar o DataFrame bruto original
    df = df.copy()

    # 1. Quantidade de registros antes da limpeza
    registros_iniciais = len(df)

    # 2. Remover espaços extras das colunas de texto
    colunas_texto = ["cliente", "produto", "categoria", "regiao"]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].str.strip()

    # 3. Converter datas; as inválidas se tornam NaT
    df["data_venda"] = pd.to_datetime(
        df["data_venda"],
        errors="coerce"
    )

    removidos_data_invalida = df["data_venda"].isna().sum()

    # Remove as linhas cuja data não pôde ser convertida
    df = df.dropna(subset=["data_venda"]).copy()

    # 4. Contar e remover nulos nas colunas críticas
    antes_remover_nulos = len(df)

    df = df.dropna(subset=["quantidade", "preco_unitario"]).copy()

    removidos_nulos_criticos = antes_remover_nulos - len(df)

    # 5. Garantir os tipos de dados solicitados
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)

    # 6. Limpar e validar os nomes dos clientes com regex
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

    # 7. Montar e exibir o relatório
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
