import streamlit as st

for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os

path = os.path.dirname(__file__)
my_file = path + '/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='About - Refrigeration Cycle Analysis',
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

st.header("Refrigeration Cycle Analysis v1.0.0", divider="gray", anchor=False)

st.markdown('''
## About Refrigeration Cycle Analysis:

Refrigerant Cycle is a Python app designed to help you quickly and easily analyze and optimize refrigeration cycles based on thermodynamic principles.

## How it Works:

To use Refrigerant Cycle, you simply need to input a few key parameters:
- Evaporation and condensation temperatures (for transcritical systems, the gas cooler outlet temperature is used instead of the condensation temperature).
- Isentropic efficiency of the compressor
- Heat load
- Percentage of heat rejected in the compressor
- Superheating and subcooling temperature differences
- Selection of the refrigerant fluid (e.g., CO2)

The app will then generate a detailed table showing the thermodynamic states (enthalpy, entropy, temperature, and pressure) for each point in the cycle. It also calculates key performance indicators such as:
- Coefficient of Performance (COP)
- Heat transfer rates
- Compressor power input
- Mass flow rate

Additionally, Refrigerant Cycle creates P-h and T-s diagrams for a better understanding of the system's operation and provides an exergy analysis to identify system inefficiencies.

## Key Features:

- **Fast and easy analysis:** Input a few parameters and get a complete thermodynamic breakdown of the cycle.
- **Performance metrics:** Detailed tables with state points, heat transfer rates, and COP.
- **Diagrams:** Visualizes cycle behavior with P-h and T-s diagrams.
- **Exergy analysis:** Identifies exergy destruction and inefficiencies in the system components.
- **Comparing different fluids:** Compare COP and exergy data for the same input.
- **Customizable options:** Supports a wide range of refrigerants and allows fine-tuning of system parameters.

  '''
            )

path2 = os.path.dirname(__file__)
my_file2 = path2 + '/images/Thumb_Mechub.png'
img2 = Image.open(my_file2)

st.image(img2)
