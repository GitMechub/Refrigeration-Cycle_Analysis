import streamlit as st

for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os

path = os.path.dirname(__file__)
my_file = path + '/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='References - Refrigeration Cycle Analysis',
    layout="wide",
    page_icon=img
)

st.sidebar.image(img)
st.sidebar.markdown(
    "[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@Mechub?sub_confirmation=1) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GitMechub)")

hide_menu = '''
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        '''
st.markdown(hide_menu, unsafe_allow_html=True)

st.header("References", anchor=False, divider='gray')
st.write("1.   CoolProp: http://www.coolprop.org/coolprop/HighLevelAPI.html#parameter-table")
st.write("2.   MORAN, M.J.; SHAPIRO, H.N.; BOETTNER, D.D.; BAILEY, M.B. Fundamentals of Engineering Thermodynamics. 8. ed. Hoboken: Wiley, 2014. ISBN 9781118832301.")
st.write("3.   STEWART, Susan W.; SHELTON, Sam V. The usefulness of entropic average temperatures. In: Proceedings of the ASME International Mechanical Engineering Congress and Exposition. Anaheim, California, 2004. p. 1-6. DOI: 10.1115/IMECE2004-60235.")
st.write("4.   SEYAM, Shaimaa. Energy and Exergy Analysis of Refrigeration Systems. 2019. ISBN 978-1-83880-666-8. DOI 10.5772/intechopen.88862.")
st.write("5.   TAO, Y.B.; HE, Y.L.; TAO, W.Q. Exergetic analysis of transcritical CO2 residential air-conditioning system based on experimental data. State Key Laboratory of Multiphase Flow in Power Engineering, School of Energy & Power Engineering, Xi’an Jiaotong University, Xi’an, Shaanxi 710049, China, 2009.")
st.write("6.   PATIL, Omprakash S.; SHET, Shrikant A.; JADHAO, Manish; AGRAWAL, Neeraj. Energetic and exergetic studies of modified CO2 transcritical refrigeration cycles. Departamento de Engenharia Mecânica, Dr. B. A. Technological University Lonere, Raigad, Maharashtra 402103, Índia, 2020.")

