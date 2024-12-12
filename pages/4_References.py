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

st.header("Refrigeration Cycle Analysis v1.0.0", divider="gray", anchor=False)

st.markdown('''
## About Gear Train Sizer:

Spur Gear Sizing is a Python app designed to help you quickly and easily size a compound spur gear train according to Norton's "Machine Design: An Integrated Approach" methodology and AGMA standards.

## How it Works:

To use Gear Train Sizer, you simply need to input a few key parameters:
- Distance between the first and last shafts
- Torque and resistance requirements
- Pressure angle
- Selected material for the gears

The app will then generate a detailed table showing the main dimensions, stresses, and safety factors for each gear in the train. It will also display the full configuration, including each gear's identification number.
In addition, Gear Train Sizer will create a separate sheet with the precise coordinates of each gear's profile. You can use these coordinates to easily create a CAD model for each gear.

## Key Features:

- Fast and easy sizing - Input a few parameters and get a complete gear train design
- Detailed analysis - Table shows dimensions, stresses, safety factors for each gear
- Full configuration - Displays complete gear train layout with IDs
- CAD integration - Generates gear profile coordinates for CAD modeling

--- 

- Tutorial Video:

  [![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/T1YwprHeOw4)

- How can you help me to improve this code:

  [![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=z66-aUrW6dE&t=58s)

  ---
  '''
            )

path2 = os.path.dirname(__file__)
my_file2 = path2 + '/images/Thumb_Mechub.png'
img2 = Image.open(my_file2)

st.image(img2)