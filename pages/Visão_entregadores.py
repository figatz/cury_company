#Importando bibliotecas necessárias
import numpy as np
import pandas as pd
import plotly.express as px
import folium
from geopy.distance import geodesic
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Visão Entregadores",
    page_icon="🛵",
    layout="wide"
)

# Carregar o dataset
# Certifique-se de que o arquivo train.csv está no mesmo diretório do script
df = pd.read_csv('train.csv')

linhas_selecionadas = df['Delivery_person_Age'] != 'NaN '

df = df.loc[linhas_selecionadas, :].copy()
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
linhas_selecionadas = df['multiple_deliveries'] != 'NaN '
df = df.loc[linhas_selecionadas, :].copy()
df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
df = df.loc[df ['Road_traffic_density'] != "NaN", :]
df = df.loc[df ['City'] != "NaN ", :]
df = df.loc[df ['Festival'] != "NaN ", :]

df = df.reset_index(drop=True)
# Remover espaços em branco extras
df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
df.loc[:,'City'] = df.loc[:,'City'].str.strip()

#Fazer a conversão de 'Time_taken(min)' retirando o texto 'min' e convertendo para inteiro
df['Time_taken(min)'] = df['Time_taken(min)'].str.extract('(\d+)').astype(int)

min_age = df['Delivery_person_Age'].min()
max_age = df['Delivery_person_Age'].max()

min_vehicle_quality = df['Vehicle_condition'].min()
max_vehicle_quality = df['Vehicle_condition'].max()


#VISÃO ENTREGADORES
#=====================================================

#=====================================================
# Layout barra lateral no Streamlit
#=====================================================
st.header('Marketplace - Visão Entregadores')

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

start_date = df['Order_Date'].min().to_pydatetime()
end_date = df['Order_Date'].max().to_pydatetime() 

date_slider = st.sidebar.slider(
    'Até qual data?',
    value=end_date,
    min_value=start_date,
    max_value=end_date,
    format='DD/MM/YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by FilipeGatz')
# Carregar e exibir a imagem do logo
image_path = 'logo_fg.png' # Caminho para a imagem do logo
image = Image.open(image_path)
st.sidebar.image(image, width=220)
#Filtro de data
df = df.loc[df['Order_Date'] <= date_slider, :].copy()
# Filtro de trânsito
selected_lines = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[selected_lines, :].copy()

#=====================================================
# Layout no Streamlit
#=====================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '', ''])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            
            col1.metric('Maior idade', max_age, help='Idade do entregador mais velho')
           
        with col2:
            
            col2.metric('Menor idade', min_age, help='Idade do entregador mais novo')
        with col3:
            
            col3.metric('Melhor condição veículo', max_vehicle_quality, help='Condição do veiculo mais novo')
        with col4:
            
            col4.metric('Pior condição veículo', min_vehicle_quality, help='Condição do veiculo mais velho')

    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.subheader('Avaliação média por entregador')
            avg_rating_per_deliver = df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean()
            st.dataframe(avg_rating_per_deliver, use_container_width=True)
        with col2:
            st.subheader('Avaliação média por trânsito')
            avg_traffic_rating = df.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']].groupby('Road_traffic_density').agg(['mean', 'std']).reset_index()
            #Renomear as colunas
            avg_traffic_rating.columns = ['Road_traffic_density', 'mean_rating', 'std_rating']
            st.dataframe(avg_traffic_rating, use_container_width=True)
            graf = px.bar(avg_traffic_rating, x='Road_traffic_density', y='mean_rating', error_y='std_rating', title='Avaliação média por tipo de tráfego')
            st.plotly_chart(graf, use_container_width=True)
            st.subheader('Avaliação média por clima')
            avg_weather_rating = df.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']].groupby('Weatherconditions').agg(['mean', 'std']).reset_index()
            #Renomear as colunas
            avg_weather_rating.columns = ['Weatherconditions', 'mean_rating', 'std_rating']
            st.dataframe(avg_weather_rating, use_container_width=True)
    
    
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.subheader('Top entregadores mais rápidos')
            fastest_deliverers = df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean()
            fastest_deliverers = fastest_deliverers.sort_values(by=['Time_taken(min)','City'], ascending=True).groupby('City').head(10)
            st.dataframe(fastest_deliverers, use_container_width=True)
        with col2:
            st.subheader('Top entregadores mais lentos')    
            slowest_deliverers = df.loc[:, ['City', 'Delivery_person_ID', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean()
            slowest_deliverers = slowest_deliverers.sort_values(by=['City', 'Time_taken(min)'], ascending=False).groupby('City').head(10)
            st.dataframe(slowest_deliverers, use_container_width=True)