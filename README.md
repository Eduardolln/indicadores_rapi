# Dashboard RAPI - Florianópolis 🌳

Dashboard interativo para visualização e análise dos **Indicadores RAPI** (Relatório Anual de Progresso dos Indicadores) de Florianópolis, Santa Catarina.

## 📋 Visão Geral

Este dashboard apresenta os indicadores de progresso municipal organizados em três dimensões principais:
- 🌳 **Ambiental** - Sustentabilidade e meio ambiente
- 🏙️ **Urbana** - Desenvolvimento urbano e infraestrutura  
- 💰 **Fiscal** - Gestão fiscal e orçamentária

## ✨ Funcionalidades

### 📊 Dashboard Executivo
- KPIs globais (total de indicadores, % verde, órgãos monitorados)
- Gráfico de rosca com distribuição de status
- Resumo por dimensão

### 🔍 Páginas de Dimensões
- Filtros interativos (Pilar, Tema, Órgão)
- Tabela hierárquica com status e tendências
- Cartões resumidos por status

### 🏛️ Órgãos Responsáveis
- Visão geral de todos os órgãos
- Detalhamento por órgão selecionado
- Ranking de órgãos

### 📈 Análise de Indicadores
- Busca textual avançada
- Visualização de séries temporais (2014-2024)
- Exibição de metas (faixas verde/amarela/vermelha)
- Informações completas do indicador

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.10 ou superior
- pip

### Instalação

1. **Clone ou navegue até o diretório do projeto:**
```bash
cd /home/eduwin/indicadores_rapi
```

2. **Crie um ambiente virtual (opcional, mas recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

### Executar o Dashboard

```bash
streamlit run app.py
```

O dashboard será aberto automaticamente no navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
indicadores_rapi/
├── app.py                              # Aplicação principal
├── bd_RAPI.csv                         # Dados (fonte)
├── requirements.txt                    # Dependências Python
├── README.md                           # Este arquivo
├── .streamlit/
│   └── config.toml                     # Configuração do tema
├── utils/
│   ├── __init__.py
│   ├── data_loader.py                  # ETL e processamento de dados
│   ├── styling.py                      # CSS customizado
│   └── components.py                   # Componentes reutilizáveis
└── pages/
    ├── 1_🏠_Inicio.py                   # Dashboard executivo
    ├── 2_🌳_Dimensao_Ambiental.py
    ├── 3_🏙️_Dimensao_Urbana.py
    ├── 4_💰_Dimensao_Fiscal.py
    ├── 5_🏛️_Orgaos_Responsaveis.py
    └── 6_📊_Analise_Indicadores.py
```

## 📊 Sobre os Dados

### Fonte de Dados
- **Arquivo:** `bd_RAPI.csv`
- **Formato:** Long format (ano, valor)
- **Período:** 2014-2024
- **Total:** ~1.400 registros

### Colunas Principais
- `dimensoes`: AMBIENTAL, URBANA, FISCAL
- `pilar`, `tema`, `subtema`: Hierarquia temática
- `id`: Identificador único do indicador
- `indicador`: Nome descritivo completo
- `orgao_responsavel`: Órgão gestor
- `faixa_1`, `faixa_2`, `faixa_3`: Metas (verde, amarela, vermelha)
- `ano`: Ano de referência
- `valor`: Valor medido

### Classificação de Status
- 🟢 **Verde**: Indicador atingiu a meta (faixa_1)
- 🟡 **Amarelo**: Atenção necessária (faixa_2)
- 🔴 **Vermelho**: Abaixo da meta (faixa_3)
- ⚫ **Cinza**: Sem dados disponíveis

### Cálculo de Tendência
- ⬆️ Valor 2024 > Valor 2023
- ⬇️ Valor 2024 < Valor 2023
- ➡️ Valores iguais ou dados insuficientes

## 🎨 Design e Tema

O dashboard utiliza uma paleta de cores verde, refletindo a identidade visual sustentável de Florianópolis ("Ver a Cidade"):
- **Verde primário:** #2E8B57 (SeaGreen)
- **Verde secundário:** #3CB371 (MediumSeaGreen)
- **Verde claro:** #90EE90 (LightGreen)

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Streamlit** - Framework de UI
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas

## 📝 Notas Técnicas

### Performance
- Cache habilitado com `@st.cache_data` para carregamento rápido
- Processamento otimizado para ~1.400 registros

### Limitações Conhecidas
- Colunas `analise_qualitativa` e `meta_ods` não estão disponíveis no dataset atual (placeholders exibidos)
- Parsing de faixas assume formatos específicos (">90-100", "<75", etc.)

## 🔄 Atualização de Dados

Para atualizar os dados:
1. Substitua o arquivo `bd_RAPI.csv` com a nova versão
2. Mantenha o mesmo formato de colunas
3. Reinicie o servidor Streamlit

## 📄 Licença

Dashboard desenvolvido para a Prefeitura de Florianópolis - SC.

## 🤝 Suporte

Em caso de dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme que o arquivo `bd_RAPI.csv` está no diretório raiz
3. Verifique a versão do Python (3.10+)

---

Desenvolvido com ❤️ usando Streamlit
