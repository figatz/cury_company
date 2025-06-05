import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)


#image_path = 'logo_fg.png'  # Caminho para a imagem do logo
image = Image.open('logo_fg.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.write("# Welcome to the Cury Company Marketplace Dashboard")
st.write("#### This dashboard provides insights into the operations of Cury Company, including delivery performance, order statistics, and more.")
st.write("#### Use the sidebar to navigate through different sections of the dashboard.")
st.write("#### Feel free to explore the data and gain insights into our delivery operations.")
st.write("##### Select a section from the sidebar to get started!")
st.write("##### Powered by Filipe Gatz")
st.write("##### For any questions or feedback, please contact us at Discord @figatz") 
