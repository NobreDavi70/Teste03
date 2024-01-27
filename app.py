import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar e preparar os dados
def carregar_dados():
    # Carregando os dados
    df_hapvida = pd.read_csv('RECLAMEAQUI_HAPVIDA.csv')
    df_ibyte = pd.read_csv('RECLAMEAQUI_IBYTE.csv')
    df_nagem = pd.read_csv('RECLAMEAQUI_NAGEM.csv')

    # Adicionando uma coluna 'Empresa'
    df_hapvida['Empresa'] = 'Hapvida'
    df_ibyte['Empresa'] = 'Ibyte'
    df_nagem['Empresa'] = 'Nagem'

    # Combinando DataFrames
    df_total = pd.concat([df_hapvida, df_ibyte, df_nagem])

    # Criando e convertendo a coluna 'Data'
    df_total['Data_String'] = df_total['ANO'].astype(str) + '-' + df_total['MES'].astype(str).apply(lambda x: x.zfill(2)) + '-' + df_total['DIA'].astype(str).apply(lambda x: x.zfill(2))
    df_total['Data'] = pd.to_datetime(df_total['Data_String'], format='%Y-%m-%d')

    return df_total

# Função para configurar os seletores
def configurar_seletores(df_total):
    # Seletores na sidebar
    empresa = st.sidebar.selectbox("Escolha a Empresa", ["Todos"] + list(df_total['Empresa'].unique()))
    local = st.sidebar.selectbox("Escolha o Local", ["Todos"] + list(df_total['LOCAL'].unique()))
    status = st.sidebar.selectbox("Selecione o Status", ["Todos"] + list(df_total['STATUS'].unique()))

    # Menu de navegação
    opcoes_menu = [
        "Série Temporal do Número de Reclamações",
        "Frequência de Reclamações por Estado",
        "Frequência de Cada Tipo de Status",
        "Distribuição do Tamanho do Texto"
    ]
    selecao_menu = st.sidebar.radio("Menu de Navegação", opcoes_menu)

    # Seletor para o tamanho do texto
    categorias_tamanho_texto = {
        'Curto (< 50 caracteres)': 50,
        'Médio (50-150 caracteres)': 150,
        'Longo (150-300 caracteres)': 300,
        'Muito Longo (> 300 caracteres)': df_total['DESCRICAO'].str.len().max()
    }
    categoria_selecionada = st.sidebar.radio(
        "Selecione a categoria do tamanho do texto da descrição",
        list(categorias_tamanho_texto.keys())
    )

    return empresa, local, status, selecao_menu, categorias_tamanho_texto, categoria_selecionada

# Função para filtrar os dados
def filtrar_dados(df_total, empresa, local, status, categoria_selecionada, categorias_tamanho_texto):
    df_filtrado = df_total.copy()

    # Filtrando por empresa, local e status
    if empresa != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Empresa'] == empresa]
    if local != "Todos":
        df_filtrado = df_filtrado[df_filtrado['LOCAL'] == local]
    if status != "Todos":
        df_filtrado = df_filtrado[df_filtrado['STATUS'] == status]

    # Filtrando por tamanho do texto
    limite_superior = categorias_tamanho_texto[categoria_selecionada]
    if 'Muito Longo' in categoria_selecionada:
        df_filtrado = df_filtrado[df_filtrado['DESCRICAO'].str.len() > 300]
    else:
        limite_inferior = 'Curto' in categoria_selecionada and 0 or categorias_tamanho_texto[list(categorias_tamanho_texto.keys())[list(categorias_tamanho_texto.values()).index(limite_superior)-1]]
        df_filtrado = df_filtrado[(df_filtrado['DESCRICAO'].str.len() > limite_inferior) & (df_filtrado['DESCRICAO'].str.len() <= limite_superior)]

    return df_filtrado

# Função principal
def main():
    # Título do Dashboard
    st.title("Dashboard de Reclamações - RECLAME AQUI")

    # Carregando e preparando dados
    df_total = carregar_dados()

    # Configurando os seletores
    empresa, local, status, selecao_menu, categorias_tamanho_texto, categoria_selecionada = configurar_seletores(df_total)

    # Filtrando os dados
    df_filtrado = filtrar_dados(df_total, empresa, local, status, categoria_selecionada, categorias_tamanho_texto)

    # Lógica de exibição dos gráficos
    if selecao_menu == "Série Temporal do Número de Reclamações":        
        # Agrupando os dados filtrados por mês e contando o número de reclamações
        df_agrupado = df_filtrado.groupby([pd.Grouper(key='Data', freq='M'), 'Empresa']).size().reset_index(name='Contagem')

        # Criando o gráfico de área com Plotly
        fig = px.area(
            df_agrupado,
            x='Data',
            y='Contagem',
            color='Empresa',
            title='Série Temporal do Número de Reclamações',
            labels={'Contagem': 'Número de Reclamações', 'Data': 'Data'},
            color_discrete_map={'Hapvida': '#ff7f0e', 'Ibyte': '#2ca02c', 'Nagem': '#1f77b4'}
        )

        # Ajustes visuais do gráfico
        fig.update_layout(
            xaxis_title='Data',
            yaxis_title='Número de Reclamações',
            legend_title='Empresa',
            font=dict(family="Arial, sans-serif", size=12, color="RebeccaPurple"),
        )

        # Exibindo o gráfico 
        st.plotly_chart(fig)

    elif selecao_menu == "Frequência de Reclamações por Estado":        
        # Gráfico de barras com a frequência de reclamações por estado
        reclamacoes_por_estado = df_filtrado.groupby('LOCAL').size().reset_index(name='Contagem')
        reclamacoes_por_estado = reclamacoes_por_estado.sort_values(by='Contagem', ascending=False)

        # Criando o gráfico de área com Plotly
        fig = px.bar(
            reclamacoes_por_estado,
            x='LOCAL',
            y='Contagem',
            title='Frequência de Reclamações por Estado'
        )

        # Ajustes visuais do gráfico
        fig.update_layout(
            xaxis_title='Estado',
            yaxis_title='Número de Reclamações',
            font=dict(family="Arial, sans-serif", size=12, color="RebeccaPurple"),
        )

        # Exibindo o gráfico 
        st.plotly_chart(fig)

    elif selecao_menu == "Frequência de Cada Tipo de Status":        
        # Gráfico de barras com a frequência de cada tipo de status
        frequencia_status = df_filtrado.groupby('STATUS').size().reset_index(name='Contagem')
        frequencia_status = frequencia_status.sort_values(by='Contagem', ascending=False)

        # Criando o gráfico de área com Plotly
        fig = px.bar(
            frequencia_status,
            x='STATUS',
            y='Contagem',
            title='Frequência de Cada Tipo de Status',
            color='STATUS',
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        # Ajustes visuais do gráfico
        fig.update_layout(
            xaxis_title='Status',
            yaxis_title='Número de Reclamações',
            font=dict(family="Arial, sans-serif", size=12, color="RebeccaPurple"),
        )

        # Exibindo o gráfico
        st.plotly_chart(fig)

    elif selecao_menu == "Distribuição do Tamanho do Texto":

        # Histograma com a distribuição do tamanho do texto
        df_filtrado['Tamanho_Texto'] = df_filtrado['DESCRICAO'].str.len()

        # Criando o gráfico de área com Plotly
        fig = px.histogram(
            df_filtrado,
            x='Tamanho_Texto',
            nbins=50,
            title='Distribuição do Tamanho do Texto'
        )

        # Ajustes visuais do gráfico
        fig.update_layout(
            xaxis_title='Tamanho do Texto (número de caracteres)',
            yaxis_title='Quantidade de Reclamações',
            font=dict(family="Arial, sans-serif", size=12, color="RebeccaPurple"),
        )

        # Exibindo o gráfico
        st.plotly_chart(fig)

# Executando a aplicação
if __name__ == "__main__":
    main()
