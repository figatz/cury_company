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
    page_title="Visão Empresa",
    page_icon="📊",
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
df = df.loc[df ['City'] != "NaN", :]
df = df.loc[df ['Festival'] != "NaN ", :]

df = df.reset_index(drop=True)
# Remover espaços em branco extras
df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
df.loc[:,'City'] = df.loc[:,'City'].str.strip()

#VISÃO EMPRESA

#=====================================================
# Layout barra lateral no Streamlit
#=====================================================
st.header('Marketplace - Visão Empresa')

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
# image_path = 'logo_fg.png' # Caminho para a imagem do logo
image = Image.open('logo_fg.png')
st.sidebar.image(image, width=220)
#Filtro de data
df = df.loc[df['Order_Date'] <= date_slider, :].copy()
# Filtro de trânsito
selected_lines = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[selected_lines, :].copy()



#=====================================================
# Layout no Streamlit
#=====================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Quantidade de entregas por dia
        st.markdown('# Orders by Day')
        qtde_dia = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
        # desenhar grafico de barras
        fig = px.bar(qtde_dia, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('## Orders by Traffic Density')
            qtde_traffic = df.loc[:, ['Road_traffic_density', 'ID']].groupby('Road_traffic_density').count().reset_index()
            qtde_traffic = qtde_traffic.loc[qtde_traffic ['Road_traffic_density'] != "NaN", :]
            qtde_traffic['entregas_perc'] = qtde_traffic['ID'] / qtde_traffic['ID'].sum()

            fig = px.pie(qtde_traffic, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('## Orders by City and Traffic Density')
            df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux ['City'] != "NaN", :]
            df_aux = df_aux.loc[df_aux ['Road_traffic_density'] != "NaN", :]

            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        st.markdown('## Orders by Week of Year')
        df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
        qtde_week = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        fig = px.line(qtde_week, x='week_of_year', y='ID' )
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():    
        st.markdown('## Orders by Delivery Men by Week')
        week_quantity = df.loc[:,['ID', 'week_of_year']]. groupby('week_of_year').count().reset_index()
        delivery_person_week = df.loc[:,['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()

        df_aux = pd.merge(week_quantity, delivery_person_week, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart(fig, use_container_width=True)
        
    
with tab3:
    st.markdown('## Central Location by City and Traffic Density')
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux ['City'] != "NaN", :]
    df_aux = df_aux.loc[df_aux ['Road_traffic_density'] != "NaN", :]

    map_ = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],popup=location_info[['City','Road_traffic_density']]).add_to(map_)
    folium_static (map_, width=1024, height=600)