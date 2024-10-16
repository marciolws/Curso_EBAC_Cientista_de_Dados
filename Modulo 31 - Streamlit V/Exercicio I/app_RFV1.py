# Imports
import pandas as pd
import streamlit as st
from io import BytesIO

# Função para converter DataFrame para CSV
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter DataFrame para Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# Classificação de Recência
def recencia_class(x, quartis):
    if x <= quartis[0.25]:
        return 'A'
    elif x <= quartis[0.50]:
        return 'B'
    elif x <= quartis[0.75]:
        return 'C'
    return 'D'

# Classificação de Frequência e Valor
def freq_val_class(x, quartis):
    if x <= quartis[0.25]:
        return 'D'
    elif x <= quartis[0.50]:
        return 'C'
    elif x <= quartis[0.75]:
        return 'B'
    return 'A'

# Função principal da aplicação
def main():
    # Configuração inicial da página
    st.set_page_config(
        page_title="RFV - Análise de Clientes",
        page_icon='https://raw.githubusercontent.com/marciolws/Curso_EBAC_Cientista_de_Dados/refs/heads/main/EBAC-media-utils/icon/favicon.ico',
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # TÍTULO
    st.markdown("""
    <div style="text-align:center">
        <a href="https://raw.githubusercontent.com/marciolws/Curso_EBAC_Cientista_de_Dados/refs/heads/main/EBAC-media-utils/logo/ebac_logo-data_science.png">
            <img src="https://raw.githubusercontent.com/marciolws/Curso_EBAC_Cientista_de_Dados/refs/heads/main/EBAC-media-utils/logo/ebac_logo-data_science.png" alt="ebac_logo-data_science" width="100%">
        </a>
    </div>
                
    ---
                
    ### **Módulo 31** | Streamlit V | Exercício I
                
    **Aluno:** [Marcio da Silva](https://www.linkedin.com/in/marcio-d-silva/)<br>
    **Data:** 15 de outubro de 2024.
                
    ---
    """, unsafe_allow_html=True)

    st.write("""# RFV
    RFV significa Recência, Frequência e Valor, utilizado para segmentação de clientes com base no comportamento de compras.
    Isso permite ações de marketing e CRM mais direcionadas, ajudando na personalização do conteúdo e retenção de clientes.
    - **Recência (R)**: Dias desde a última compra.
    - **Frequência (F)**: Total de compras no período.
    - **Valor (V)**: Total gasto nas compras do período.
    """)
    
    st.markdown("---")

    # Imagem na barra lateral
    st.sidebar.image('https://raw.githubusercontent.com/marciolws/Curso_EBAC_Cientista_de_Dados/refs/heads/main/EBAC-media-utils/logo/newebac_logo_black_half.png')

    # Carregar arquivo na aplicação
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    # Usar arquivo demonstrativo se não houver arquivo carregado
    if data_file_1 is None and st.sidebar.button('Carregar Arquivo Demonstrativo'):
        data_file_1 = 'dados_input 1.csv'  
    # Verifica se há conteúdo carregado na aplicação
    if data_file_1 is not None:
        try:
            # Tenta ler o arquivo com diferentes codificações
            df_compras = pd.read_csv(data_file_1, encoding='ISO-8859-1', infer_datetime_format=True, parse_dates=['DiaCompra'])
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo: {e}")
            return

        # Recência
        dia_atual = df_compras['DiaCompra'].max()
        st.write('## Recência (R)')
        st.write('Dia máximo na base de dados: ', dia_atual)
        df_recencia = df_compras.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
        df_recencia['Recencia'] = (dia_atual - df_recencia['DiaCompra']).dt.days
        df_recencia.drop('DiaCompra', axis=1, inplace=True)
        st.write(df_recencia.head())

        # Frequência
        st.write('## Frequência (F)')
        df_frequencia = df_compras.groupby('ID_cliente').size().reset_index(name='Frequencia')
        st.write(df_frequencia.head())

        # Valor
        st.write('## Valor (V)')
        df_valor = df_compras.groupby('ID_cliente')['ValorTotal'].sum().reset_index()
        df_valor.columns = ['ID_cliente', 'Valor']
        st.write(df_valor.head())

        # Tabela RFV
        st.write('## Tabela RFV final')
        df_RF = df_recencia.merge(df_frequencia, on='ID_cliente').merge(df_valor, on='ID_cliente')
        df_RF.set_index('ID_cliente', inplace=True)
        st.write(df_RF.head())

        # Segmentação utilizando o RFV
        quartis = df_RF[['Recencia', 'Frequencia', 'Valor']].quantile(q=[0.25, 0.5, 0.75])
        df_RF['R_quartil'] = df_RF['Recencia'].apply(recencia_class, args=(quartis['Recencia'],))
        df_RF['F_quartil'] = df_RF['Frequencia'].apply(freq_val_class, args=(quartis['Frequencia'],))
        df_RF['V_quartil'] = df_RF['Valor'].apply(freq_val_class, args=(quartis['Valor'],))
        df_RF['RFV_Score'] = df_RF['R_quartil'] + df_RF['F_quartil'] + df_RF['V_quartil']

        st.write('## Resultado da Segmentação')
        st.write(df_RF.head())
        st.write('Quantidade de clientes por grupo:')
        st.write(df_RF['RFV_Score'].value_counts())

        st.write('#### Top 10 clientes com menor recência, maior frequência e maior valor gasto:')
        st.write(df_RF[df_RF['RFV_Score'] == 'AAA'].sort_values('Valor', ascending=False).head(10))

        # Ações de marketing/CRM
        st.write('### Ações de marketing/CRM')
        dict_acoes = {
            'AAA': 'Enviar cupons de desconto e amostras grátis.',
            'DDD': 'Churn! Fazer nada.',
            'DAA': 'Enviar cupons de desconto para tentar recuperar.',
            'CAA': 'Enviar cupons de desconto para tentar recuperar.'
        }
        df_RF['acoes de marketing/crm'] = df_RF['RFV_Score'].map(dict_acoes)
        st.write(df_RF[['acoes de marketing/crm']].head())

        # Download do arquivo Excel
        df_xlsx = to_excel(df_RF)
        st.download_button(label='📥 Download do RFV', data=df_xlsx, file_name='RFV_.xlsx')

        st.write('Quantidade de clientes por tipo de ação:')
        st.write(df_RF['acoes de marketing/crm'].value_counts(dropna=False))

if __name__ == '__main__':
    main()
