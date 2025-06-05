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
    page_title="Visão Restaurantes",
    page_icon="🍔" ,
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

#=====================================================

#=====================================================
# Layout barra lateral no Streamlit
#=====================================================
st.header('Marketplace - Visão Restaurantes')

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

with st.container():
    
    st.markdown('### Métricas gerais')

    col1, col2, col3, col4 = st.columns(4, gap='large')

    with col1:
        # Número de pedidos
        num_orders = df.shape[0]
        st.metric(label='Número de Pedidos', value=num_orders)

    with col2:
        # Entregadores únicos
        num_delivery_persons = df['Delivery_person_ID'].nunique()
        st.metric(label='Entregadores Únicos', value=num_delivery_persons)

    with col3:
        # Avaliação média dos entregadores
        avg_rating = df['Delivery_person_Ratings'].mean().round(2)
        st.metric(label='Avaliação Média dos Entregadores', value=avg_rating, help='Avaliação média dos entregadores')
    with col4:
        def calcular_distancia_geopy(row):
            origem = (row['Restaurant_latitude'], row['Restaurant_longitude'])
            destino = (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
            # geodesic retorna um objeto de distância, pegamos o valor em km
            return geodesic(origem, destino).km

        # 3. Aplicar a função ao DataFrame
        df['distancia_km_geopy'] = df.apply(calcular_distancia_geopy, axis=1)

        avg_distance = df['distancia_km_geopy'].mean()
        avg_distance = round(avg_distance, 1)
        abg = (f'{avg_distance}km')
        st.metric(label='Distância Média (km)', value=abg, help='Distância média dos pedidos')    

with st.container(border=True):
    st.markdown('### Tempo médio de entrega por cidade')
    avg_delivery_time = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg(['mean', 'std']).reset_index()
    avg_delivery_time.columns = ['City', 'Time_taken(min)', 'std_time_taken(min)']
    graf=px.bar(avg_delivery_time, x='City', y='Time_taken(min)', error_y='std_time_taken(min)', title='Tempo médio de entrega por cidade')    
    st.plotly_chart(graf, use_container_width=True)

with st.container(border=True):
    st.markdown('### Tempo médio de entrega por cidade e tipo de tráfego')
    avg_delivery_time_traffic = df.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg(['mean', 'std']).reset_index()
    # Renomear as colunas MultiIndex para strings simples
    avg_delivery_time_traffic.columns = ['City', 'Road_traffic_density', 'mean_time', 'std_time']
    graf = px.sunburst(avg_delivery_time_traffic, path=['City', 'Road_traffic_density'], values='mean_time')
    st.plotly_chart(graf, use_container_width=True)

with st.container(border=True):
    st.markdown('### Tempo médio durante o festival e sem festival')
    avg_time_festival = df.loc[:, ['Festival', 'Time_taken(min)']].groupby('Festival').agg(['mean', 'std']).reset_index()

    avg_time_festival.columns = ['Festival', 'mean_time', 'std_time']
    graf = px.bar(avg_time_festival, x='Festival', y='mean_time', error_y='std_time')
    st.plotly_chart(graf, use_container_width=True)