# SalesInsight PY

Projeto avaliativo do curso **Desenvolvimento de IA para Análise Preditiva** da Turma 03.

## Sobre o projeto

O SalesInsight PY realiza a análise exploratória de um conjunto de vendas. O programa gera e carrega um dataset em CSV, trata dados inconsistentes, cria novas colunas, calcula métricas e produz visualizações para apoiar a tomada de decisão.
O foco do projeto é praticar Python, Pandas, NumPy e visualizaço de dados.

## Perguntas respondidas pela análise

- Como a receita se comporta por mês e trimestre?
- Quais produtos e categorias geram mais receita?
- Quais regiões apresentam melhor desempenho?
- Quais clientes pertencem aos segmentos Bronze, Prata e Ouro?
- Qual é a relação entre quantidade vendida e receita por venda?

## Funcionalidades

- Geração automática do arquivo `vendas.csv` com dados de vendas propositalmente inconsistentes;
- Inspeção da estrutura e dos valores nulos do dataset;
- Limpeza de espaços, datas inválidas, valores nulos e nomes de clientes com expressões regulares;
- Criação de colunas derivadas, como receita total, mês, trimestre, ano e faixa de receita;
- Calculo de métricas por mês, produto, categoria e região;
- Segmentação de clientes por nível de gasto;
- Operações vetorizadas com NumPy;
- Gráficos de linha, barras, dispersão e painel-resumo;
- Exportação de resultados em CSV, JSON e PNG.

## Tecnologias e conceitos praticados

- Python 3
- Pandas e DataFrames
- NumPy: arrays, operações vetorizadas e broadcasting
- `datetime` e expressões regulares (`re`)
- Funções, `lambda` e função de ordem superior
- Classes e métodos de instância
- Matplotlib e Seaborn
- Leitura e escrita de CSV e JSON
- Git e GitHub

## Como executar

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd salesinsight-py
```

### 2. Crie e ative um ambiente virtual (opcional, recomendado)

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\\Scripts\\activate
```

### 3. Instale as dependências

```bash
pip install pandas numpy matplotlib seaborn
```

### 4. Execute o projeto

```bash
python salesinsight.py
```

Na primeira execução, o programa deverá gerar automaticamente o arquivo `vendas.csv`, caso ele ainda não exista. Em seguida, os arquivos de resultado serão criados na pasta `outputs/`.

## Estrutura do projeto

```text
salesinsight-py/
|-- salesinsight.py              # Codigo principal e ponto de entrada
|-- vendas.csv                   # Dataset gerado automaticamente
|-- README.md                    # Documentacao do projeto
|-- outputs/
    |-- metricas_por_mes.csv
    |-- segmentacao_clientes.csv
    |-- estatisticas_gerais.json
    |-- graficos/
        |-- receita_por_mes.png
        |-- top_produtos.png
        |-- quantidade_vs_receita.png
        |-- painel_resumo.png
```

## Decisoes técnicas

Os registros com data inválida ou valores ausentes nas colunas críticas são removidos, pois não permitem calcular a receita de forma confiável. Essa escolha preserva a consistência das métricas e dos gráficos.
Para classificar a receita por venda, será usado `np.select`, pois ele permite aplicar condições de forma vetorizada, evitando um laco manual sobre cada registro.

## Status do desenvolvimento
