import pandas as pd
import re
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium

#a biblioteca necessária
import pandas as pd 
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadoress', page_icon='🏍', layout = 'wide')



#=========================
#Funções
#=========================

def top_delivers(df1, top_asc):
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending = top_asc).reset_index()
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian ', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban ', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban ', :].head(10)
    df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop = True)
    return df3



def clean_code( df1 ): 
    ''' Esta função tem a responsabelidade de limpar o dataframe:
        
        Tipos de limpeza:
        1. Renovação dos dados NAN
        2. Mudança do tipo de coluna de dados
        3. Remoção dos dados das variáveis de preço 
        4. Formatação da coluna de dados
        5. Limpeza da coluna de tempo
        
        Input: Dataframe 
        Output: DataFrame
    '''
    
    
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]


    linhas_vazias = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # Comando para remover o texto de números
    #df1 = df1.reset_index( drop=True )
    #for i in range( len( df1 ) ):
        #df1.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df1.loc[i, 'Time_taken(min)'] )

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    return df1



#Import dataset

df = pd.read_csv('dataset/train.csv')

#Cleaning dataset
df1 = clean_code(df)




#================================================
#Barra Lateral
#================================================

st.header('Marketplace - Visão Entregadores')

image_path = 'logo.jpg'
image = Image.open(image_path)
st.sidebar.image(image)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite ')

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime( 2022, 4, 3),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low ', 'Medium ', 'High ', 'Jam '],
    default = ['Low ', 'Medium ', 'High ', 'Jam '] )

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider 
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#====================================================
#Layout do streamlit 
#====================================================

tab1, tab2, tab3=st.tabs( ['Visão Gerencial', ' _', '_'] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        with col1:
            #Maior idade dos entregadores
            st.subheader('Maior de idade')
            maior = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade ', maior)
        
        with col2:
            #Menor idade dos entregadores
            st.subheader('Menor de idade')
            menor = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor)
        with col3:
            #melhor condiçao de veiculo
            st.subheader('Melhor condição de veiculos')
            melhor = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor)
            
            
        with col4:
            #pior condiçao de veiculo
            st.subheader('Pior condição de veículos')
            pior = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condicao', pior)
    
    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        
        
        with col1:
            st.markdown('##### Avaliação Média por Entregador')
            rating_per_deliver = df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby(['Delivery_person_ID']).mean().reset_index()

            st.dataframe(rating_per_deliver)
        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
            rating_by_trafic = df1.loc[:, ['Road_traffic_density','Delivery_person_Ratings']].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings': ['mean', 'std']})
            rating_by_trafic.columns = ['Delivery_mean', 'Delivery_std']
            rating_by_trafic = rating_by_trafic.reset_index()
            st.dataframe(rating_by_trafic)

            st.markdown(' ##### Avaliação Média por Clima ' )
            rating_by_wheather = df1.loc[:, ['Weatherconditions','Delivery_person_Ratings']].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings': ['mean', 'std']})

            #Padrão visual
            rating_by_wheather.columns = ['Delivery_mean', 'Delivery_std']
            rating_by_wheather = rating_by_wheather.reset_index()
            st.dataframe(rating_by_wheather)
            
    with st.container():
            st.markdown('''---''')
            st.title('Velocidade de Entrega')

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('##### Top Entregadores mais Rápido')
                df3 = top_delivers(df1, top_asc=True)
                st.dataframe(df3)
            with col2:
                st.markdown('##### Top Entregadores mais Lentos' )
                df3 = top_delivers(df1, top_asc=False)
                st.dataframe(df3)
                
                
                
            