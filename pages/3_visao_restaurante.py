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
import numpy as np

st.set_page_config(page_title='Visão Restaurante', page_icon='🍕', layout = 'wide')



#=========================
#Funções
#=========================

def avg_std_time_time_traffic(df1):
                
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['Avg_time', 'Std_time']

    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values = 'Avg_time', color = 'Std_time', color_continuous_scale = 'RdBu', color_continuous_midpoint = np.average(df_aux['Std_time']))
    return fig




def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude' ]

        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
        dis_media = np.round(df1['distance'].mean(), 2)
        return dis_media
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude' ]

        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data = [ go.Pie(labels = avg_distance['City'], values = avg_distance['distance'], pull = [0, 0.1, 0] )])
        return fig
        
    


            
def avg_std_delivery(df1, festival, op):
    '''
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega
            Parâmetros:
                Input:
                    - df: Dataframe com os cálculos necessários para o cálculo
                    - op: Tipo  de Operação que precisa ser calculado
                    - 'Avg_time': Tempo médio a ser calculado
                    - 'std_time': Calcular o Desvio_padrão do tempo
        Output:
                - Dataframe com duas colunas e uma linha
            '''
    
    
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['Avg_time', 'std_time']

    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
                
    return df_aux


def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['City',  'Time_taken(min)']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['Avg_time', 'Std_time']

    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name = 'Control', x = df_aux['City'], y = df_aux['Avg_time'], error_y = dict(type = 'data', array=df_aux['Std_time'])))
    fig.update_layout(barmode='group')
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






#---------------------------------------
#Import dataset
#---------------------------------------

df = pd.read_csv('dataset/train.csv')

#Limpando os dados

df1 = clean_code(df)


#================================================
#Barra Lateral
#================================================

st.header('Marketplace - Visão Restaurante')

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
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', ' _', '_'] )

with tab1:
    with st.container():
        st.markdown('''---''')
        st.title('Overal metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            
            deliver_unico = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores ', deliver_unico)
        with col2:
        
            dis_media = distance(df1, fig=False)
            col2.metric('Distância média de entregas', dis_media)

        with col3:
            df_aux = avg_std_delivery(df1, 'Yes ', 'Avg_time')
            col3.metric('Tempo Médio c/ Festival', df_aux)
            
        with col4:
            df_aux = avg_std_delivery(df1, 'Yes ', 'std_time')
            col4.metric('STD Entrega', df_aux)
            
            
            
        with col5:
            df_aux = avg_std_delivery(df1, 'No ', 'Avg_time')
            col5.metric('Tempo Médio s/ Festival', df_aux)
            
            
        with col6:
            df_aux = avg_std_delivery(df1, 'No ', 'std_time')
            col6.metric('Desvio Médio de Entrega s/ Festival', df_aux)
            
    with st.container():
        st.markdown('''---''')
        
        
        st.markdown('### Tempo Médio de entrega por cidade')
        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig)
        
            

    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do Tempo')
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = distance(df1, fig = True)
            st.plotly_chart(fig)
        
            
            
            
            
            
        with col2:
            fig = avg_std_time_time_traffic(df1)
            st.plotly_chart(fig)


    with st.container():
        st.markdown('''---''')
        st.markdown('### Distribuição da Distância')
        df_aux = df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})

        df_aux.columns = ['Avg_time', 'Std_time']

        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)