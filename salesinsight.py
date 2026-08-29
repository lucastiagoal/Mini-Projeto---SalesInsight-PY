import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json

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

print("\n=== RF07 ===")

def calcular_estatisticas_numpy(df):
    """Calcula estatísticas e demonstra operações vetorizadas com NumPy."""

    receitas = df["receita_total"].to_numpy()

    media = np.mean(receitas)
    mediana = np.median(receitas)
    desvio_padrao = np.std(receitas)
    receita_total = np.sum(receitas)
    menor_receita = np.min(receitas)
    maior_receita = np.max(receitas)

    receitas_escalonadas = (
        (receitas - receitas.min())
        / (receitas.max() - receitas.min())
    )

    receitas_acima_media = receitas[receitas > media]

    estatisticas = {
        "media_receita": float(media),
        "mediana_receita": float(mediana),
        "desvio_padrao_receita": float(desvio_padrao),
        "receita_total": float(receita_total),
        "menor_receita": float(menor_receita),
        "maior_receita": float(maior_receita),
        "vendas_acima_da_media": int(len(receitas_acima_media))
    }

    print(f"Média: R$ {media:.2f}")
    print(f"Mediana: R$ {mediana:.2f}")
    print(f"Desvio padrão: R$ {desvio_padrao:.2f}")
    print(f"Receita total: R$ {receita_total:.2f}")
    print(f"Vendas acima da média: {len(receitas_acima_media)}")
    print(f"Primeiras receitas escalonadas: {receitas_escalonadas[:5]}")

    return estatisticas

estatisticas = calcular_estatisticas_numpy(df_transformado)

print("\n=== RF08 ===")

def criar_visualizacoes(df, metricas):
    """Cria e exporta os gráficos do projeto."""

    os.makedirs("outputs/graficos", exist_ok=True)
    sns.set_theme(style="whitegrid", palette="muted")
    por_mes = metricas["por_mes"]
    top_produtos = metricas["top_produtos"]
    por_regiao = metricas["por_regiao"]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        por_mes["mes_nome"],
        por_mes["receita_total"],
        marker="o",
        linewidth=2,
        color="steelblue"
    )

    ax.set_title("Receita Total por Mês")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Receita Total (R$)")
    ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    fig.savefig("outputs/graficos/receita_por_mes.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=top_produtos,
        y="produto",
        x="receita_total",
        hue="produto",
        legend=False,
        palette="Blues_d",
        ax=ax
    )

    ax.set_title("Top 5 Produtos por Receita")
    ax.set_xlabel("Receita Total (R$)")
    ax.set_ylabel("Produto")

    plt.tight_layout()
    fig.savefig("outputs/graficos/top_produtos.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.scatterplot(
        data=df,
        x="quantidade",
        y="receita_total",
        hue="categoria",
        palette="Set2",
        ax=ax
    )

    ax.set_title("Quantidade Vendida x Receita por Venda")
    ax.set_xlabel("Quantidade")
    ax.set_ylabel("Receita Total (R$)")
    ax.legend(title="Categoria")

    plt.tight_layout()
    fig.savefig("outputs/graficos/quantidade_vs_receita.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    axes[0, 0].plot(
        por_mes["mes_nome"],
        por_mes["receita_total"],
        marker="o",
        color="steelblue"
    )
    axes[0, 0].set_title("Receita por Mês")
    axes[0, 0].set_xlabel("Mês")
    axes[0, 0].set_ylabel("Receita (R$)")
    axes[0, 0].tick_params(axis="x", rotation=45)

    sns.barplot(
        data=top_produtos,
        y="produto",
        x="receita_total",
        hue="produto",
        legend=False,
        palette="Blues_d",
        ax=axes[0, 1]
    )
    axes[0, 1].set_title("Top Produtos")
    axes[0, 1].set_xlabel("Receita (R$)")
    axes[0, 1].set_ylabel("Produto")

    sns.scatterplot(
        data=df,
        x="quantidade",
        y="receita_total",
        hue="categoria",
        palette="Set2",
        ax=axes[1, 0]
    )
    axes[1, 0].set_title("Quantidade x Receita")
    axes[1, 0].set_xlabel("Quantidade")
    axes[1, 0].set_ylabel("Receita (R$)")
    axes[1, 0].legend(title="Categoria")

    sns.barplot(
        data=por_regiao,
        x="regiao",
        y="receita_total",
        hue="regiao",
        legend=False,
        palette="Greens_d",
        ax=axes[1, 1]
    )
    axes[1, 1].set_title("Receita por Região")
    axes[1, 1].set_xlabel("Região")
    axes[1, 1].set_ylabel("Receita (R$)")
    axes[1, 1].tick_params(axis="x", rotation=30)

    fig.suptitle("SalesInsight PY - Painel Resumo", fontsize=16)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig("outputs/graficos/painel_resumo.png", dpi=150)
    plt.close(fig)

    print("Gráficos salvos em outputs/graficos/")

criar_visualizacoes(df_transformado, metricas)

print("\n=== RF09 ===")

def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """Aplica uma função de transformação a uma coluna do DataFrame."""

    df = df.copy()

    nome_saida = nome_saida or f"{coluna}_transformado"

    df[nome_saida] = df[coluna].apply(funcao_transformacao)

    return df

df_transformado = processar_coluna(
    df_transformado,
    "receita_total",
    lambda valor: round(valor / 1000, 2),
    nome_saida="receita_em_milhares"
)

df_transformado = processar_coluna(
    df_transformado,
    "quantidade",
    lambda quantidade: "Alto Volume" if quantidade > 5 else "Baixo Volume",
    nome_saida="perfil_volume"
)

print(
    df_transformado[
        ["receita_total", "receita_em_milhares", "quantidade", "perfil_volume"]
    ].head()
)

class AnalisadorDeVendas:
    """Encapsula o fluxo de análise dos dados de vendas."""

    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.df_bruto = None
        self.df_limpo = None
        self.df_transformado = None
        self.metricas = {}
        self.clientes = None
        self.estatisticas = {}
        self.relatorio_limpeza = {}

    def carregar(self):
        """Lê o CSV e guarda o DataFrame bruto."""
        self.df_bruto = pd.read_csv(self.caminho_arquivo)
        print(f"[Analisador] {len(self.df_bruto)} registros lidos.")
        return self.df_bruto

    def limpar(self):
        """Limpa os dados usando a função limpar_dados."""
        self.df_limpo, self.relatorio_limpeza = limpar_dados(
            self.df_bruto
        )
        return self.df_limpo

    def transformar(self):
        """Cria colunas derivadas e aplica transformações reutilizáveis."""
        self.df_transformado = criar_colunas_derivadas(self.df_limpo)

        self.df_transformado = processar_coluna(
            self.df_transformado,
            "receita_total",
            lambda valor: round(valor / 1000, 2),
            nome_saida="receita_em_milhares"
        )

        self.df_transformado = processar_coluna(
            self.df_transformado,
            "quantidade",
            lambda quantidade: (
                "Alto Volume" if quantidade > 5 else "Baixo Volume"
            ),
            nome_saida="perfil_volume"
        )

        return self.df_transformado

    def analisar(self):
        """Calcula métricas, segmentação e estatísticas NumPy."""
        self.metricas = calcular_metricas(self.df_transformado)
        self.clientes = segmentar_clientes(self.df_transformado)
        self.estatisticas = calcular_estatisticas_numpy(
            self.df_transformado
        )

    def visualizar(self):
        """Gera e exporta os gráficos."""
        criar_visualizacoes(self.df_transformado, self.metricas)

    def exportar(self):
        """Exporta os resultados da análise."""
        return exportar_resultados(
            self.metricas,
            self.clientes,
            self.estatisticas
        )
    
    def resumo(self):
        """Exibe um resumo final da análise."""
        print("\n=== RESUMO EXECUTIVO ===")
        print(f"Registros analisados: {len(self.df_transformado)}")
        print(
            f"Receita total: "
            f"R$ {self.estatisticas['receita_total']:.2f}"
        )
        print(
            f"Clientes segmentados: "
            f"{len(self.clientes)}"
        )

print("\n=== RF10 ===")

def exportar_resultados(metricas, clientes, estatisticas):
    """Exporta as métricas, a segmentação e as estatísticas do projeto."""

    os.makedirs("outputs", exist_ok=True)

    metricas["por_mes"].to_csv(
        "outputs/metricas_por_mes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    clientes.to_csv(
        "outputs/segmentacao_clientes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    estatisticas_serializaveis = {
        chave: round(float(valor), 2)
        for chave, valor in estatisticas.items()
    }

    caminho_json = "outputs/estatisticas_gerais.json"

    with open(caminho_json, "w", encoding="utf-8") as arquivo:
        json.dump(
            estatisticas_serializaveis,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    with open(caminho_json, "r", encoding="utf-8") as arquivo:
        conferencia = json.load(arquivo)

    print("CSV de métricas salvo em outputs/metricas_por_mes.csv")
    print("CSV de segmentação salvo em outputs/segmentacao_clientes.csv")
    print(f"JSON gravado e lido: {conferencia}")

    return conferencia
exportar_resultados(metricas, clientes, estatisticas)

print("\n=== RF11 ===")

def main():
    """Executa o fluxo completo do SalesInsight PY."""

    print("=" * 60)
    print("SALESINSIGHT PY - Análise de Dados de Vendas")
    print("=" * 60)

    print("\n=== RF01 ===")

    if not os.path.exists("vendas.csv"):
        df_gerado = gerar_dataset_vendas()
        df_gerado.to_csv("vendas.csv", index=False)
        print(f"Dataset gerado com {len(df_gerado)} registros.")
    else:
        print("Dataset vendas.csv já existe e será utilizado.")

    analisador = AnalisadorDeVendas("vendas.csv")

    print("\n=== RF02 ===")
    analisador.carregar()
    inspecionar_dados(analisador.df_bruto)

    print("\n=== RF03 ===")
    analisador.limpar()
    inspecionar_dados(analisador.df_limpo)

    print("\n=== RF04 e RF09 ===")
    analisador.transformar()

    print(
        analisador.df_transformado[
            [
                "receita_total",
                "receita_em_milhares",
                "quantidade",
                "perfil_volume"
            ]
        ].head()
    )

    print("\n=== RF05, RF06 e RF07 ===")
    analisador.analisar()

    print("\n=== MÉTRICAS POR MÊS ===")
    print(analisador.metricas["por_mes"].to_string(index=False))

    print("\n=== TOP PRODUTOS ===")
    print(analisador.metricas["top_produtos"].to_string(index=False))

    print("\n=== POR CATEGORIA ===")
    print(analisador.metricas["por_categoria"].to_string(index=False))

    print("\n=== POR REGIÃO ===")
    print(analisador.metricas["por_regiao"].to_string(index=False))

    print("\n=== RF08 ===")
    analisador.visualizar()

    print("\n=== RF10 ===")
    analisador.exportar()

    analisador.resumo()

    print("\n[CONCLUÍDO] Fluxo finalizado com sucesso.")


if __name__ == "__main__":
    main()