# Libraries
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


st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout = 'wide')


#=========================
#Funções
#=========================


def country_map(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup = location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width = 1024, height = 600)
    

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'week_of_year']
    df_aux = df1.loc[:, cols].groupby(['week_of_year']).count().reset_index()

    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig

def order_share_by_week(df1):
    
    df_aux1 = df1.loc[:, ['week_of_year', 'ID']].groupby('week_of_year').count().reset_index() 
    df_aux2 = df1.loc[:, ['week_of_year', 'Delivery_person_ID']].groupby('week_of_year').nunique().reset_index()
    
    
    df_aux = pd.merge(df_aux1, df_aux2, how = 'inner', on = 'week_of_year')
    df_aux['Order_by_deliver'] = df_aux['ID']/ df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x = 'week_of_year', y = 'Order_by_deliver')
    return fig


def order_metric(df1):
    cols = ['ID', 'Order_Date']

            #seleçao de linhas
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
    return fig
            #plotly

    
def traffic_order_share(df1):
    
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()

    df_aux['perc_pedido'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux, values = 'perc_pedido', names = 'Road_traffic_density')
    return fig

def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Type_of_vehicle']].groupby(['City', 'Type_of_vehicle']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN ', :] 

    fig = px.scatter(df_aux, x = 'City', y = 'Type_of_vehicle', size = 'ID', color = 'City')
    return fig

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

#------------------------Início da estrutura lógica do código---------------------
#---------------------------------------------------------------------------------
#Import dataset
#---------------------------------------------------------------------------------
df = pd.read_csv('dataset/train.csv')
#---------------------------------------------------------------------------------
#Limpeza dos dados 
#--------------------------------------------------------------------------------
df1 = clean_code(df)
    

#================================================
#Barra Lateral
#================================================

st.header('Marketplace - Visão Cliente')

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

tab1, tab2, tab3=st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
        #ordermetric
        #colunas 
    fig = order_metric(df1)
    
    with st.container():
        st.markdown('# Orders by day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            st.header('Order traffic Share')
            fig = traffic_order_share(df1)  
            st.plotly_chart(fig, use_container_width=True)
            
        with col2: 
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
        
        

        
        
with tab3:
    st.markdown('# Country maps')
    country_map(df1)
    
                       
                   
#print(df1.head())