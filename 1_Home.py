import streamlit as st
st.session_state.update(st.session_state)
for k, v in st.session_state.items():
    st.session_state[k] = v

from PIL import Image
import os
path = os.path.dirname(__file__)
my_file = path+'/pages/images/mechub_logo.png'
img = Image.open(my_file)

st.set_page_config(
    page_title='Refrigeration Cycle Analysis',
    layout="wide",
    page_icon=img
                   )

st.sidebar.image(img)
st.sidebar.markdown("[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@Mechub?sub_confirmation=1) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GitMechub)")

hide_menu = '''
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        '''
st.markdown(hide_menu, unsafe_allow_html=True)


from CoolProp import AbstractState
from CoolProp.CoolProp import PhaseSI, PropsSI, get_global_param_string
import CoolProp.CoolProp as CoolProp
from CoolProp.HumidAirProp import HAPropsSI
import CoolProp.Plots as CPP

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

################# SETUP #################

st.title("Refrigeration Cycle Analysis v1.1.0", anchor=False)

col1, col2 = st.columns([1, 2])

col1.subheader("Setup", divider="gray", anchor=False)


if 'active_page' not in st.session_state:
    st.session_state.active_page = '1_Home'
    st.session_state.kT_evap = 273.15+10
    st.session_state.kT_cond = 273.15+40
    st.session_state.kT_L = 273.15+20
    st.session_state.kT_H = 273.15+30
    st.session_state.kQ_evap = 120e3
    st.session_state.kT_sup = 0
    st.session_state.kT_sub = 0

    st.session_state.kfluid_list = ['R134a', 'Ammonia', 'R11', 'R12', 'R22', 'R1234yf', 'R410A', 'R32','CO2', 'N2O']

    st.session_state.kfluido_1 = 'CO2'

T_evap = col1.number_input(
    label='Evaporation temperature',
    min_value=0.,
    format="%f",
    step=1.,
    key='kT_evap',
    help="Evaporation temperature [K]"
)

T_cond = col1.number_input(
    label='Condensation temperature',
    min_value=0.,
    format="%f",
    step=1.,
    key='kT_cond',
    help="Outlet temperature from gas cooler if transcritical [K]"
)

n_is = col1.slider(
    "Isentropic efficiency", 0., 1., 0.85, help='Isentropic efficiency of the compressor'
)

Q_evap = col1.number_input(
    label='Heat load',
    min_value=0.,
    format="%f",
    step=1.,
    key='kQ_evap',
    help="Heat load [W]"
)

r_Qc = col1.slider(
    "% Heat rejected in compressor", 0., 0.9, 0., help='Fraction of the compressor input power that is lost as heat to the surroundings'
)

T_sup = col1.number_input(
    label='Superheating temperature difference',
    min_value=0.,
    format="%f",
    step=1.,
    key='kT_sup',
    help="Superheating temperature difference [K]"
)

T_sub = col1.number_input(
    label='Subcooling temperature difference',
    min_value=0.,
    format="%f",
    step=1.,
    key='kT_sub',
    help="Subcooling temperature difference [K] - only for subcritical cycles"
)

with col1.expander('Reference Data (Exergy Analysis)'):
    T_H = st.number_input(
    label='High-temperature medium',
    min_value=0.,
    max_value=T_cond,
    format="%f",
    step=1.,
    key='kT_H',
    help="Reference temperature for refrigeration cycles [K] - Must be below condensation temperature"
    )

    T_L = st.number_input(
    label='Low-temperature medium',
    min_value=T_evap,
    format="%f",
    step=1.,
    key='kT_L',
    help="Low-temperature medium [K] - Must be above evaporation temperature"
    )

    fluid_list = st.multiselect(
    label="Select Fluids for Comparisons",
    options = ["R134a", "R12", "R22", "R404A", "R407C", "R410A", "R507A", "Ammonia", "CO2","R1234yf", "R23", "R32", "R11", "R123", "R13", "R1234ze", "R245fa","Ethane", "Isopentane", "Isohexane", "IsoButane", "n-Propane", "n-Butane", "n-Pentane","CycloPropane", "CycloPentane", "Propylene", "Xenon", "SulfurDioxide", "EthylBenzene","Ethanol", "Ethylene", "N2O"],
    key='kfluid_list',
    )

fluido_1 = col1.selectbox(
    'Refrigerant Fluid', ["R134a", "R12", "R22", "R404A", "R407C", "R410A", "R507A", "Ammonia", "CO2",
    "R1234yf", "R23", "R32", "R11", "R123", "R13", "R1234ze", "R245fa",
    "Ethane", "Isopentane", "Isohexane", "IsoButane", "n-Propane", "n-Butane", "n-Pentane",
    "CycloPropane", "CycloPentane", "Propylene", "Xenon", "SulfurDioxide", "EthylBenzene",
    "Ethanol", "Ethylene","N2O"],
    key='kfluido_1'
)

run_button = col1.button("Run",use_container_width = True)

################# FUNCTIONS #################

#   REF CYCLE
def ciclo_refrigeracao(T_evap, T_cond, n_is, Q_evap, r_Qc, fluido_1, T_sup=0, T_sub=0, fluido_escolhido=1):

  try:

      # State 1 - Saturated vapor in the evaporator (Q = 1)

      P1 = PropsSI("P", "T", T_evap, "Q", 1, fluido_1)
      T1 = T_evap + T_sup
      try:
        H1 = PropsSI("H", "P", P1, "T", T1, fluido_1)
        S1 = PropsSI("S", "P", P1, "T", T1, fluido_1)
      except:
        T1 = PropsSI("T", "P", P1, "Q", 1, fluido_1)
        H1 = PropsSI("H", "P", P1, "Q", 1, fluido_1)
        S1 = PropsSI("S", "P", P1, "Q", 1, fluido_1)


      # Supercritical cycle?

      T_critica = PropsSI("TCRIT", fluido_1)  # Critical temperature of the fluid
      if T_cond >= T_critica:   # If supercritical
          transc_cycle = True
      else:
          transc_cycle = False


      # States 2 and 3 - Condenser/Gas cooler

      ## Subcritical:

      if transc_cycle is False:
        P_cond = PropsSI("P", "Q", 1, "T", T_cond, fluido_1)    # Condensation pressure
        P2 = P_cond
        S2s = S1  # Isentropic
        H2s = PropsSI("H", "S", S2s, "P", P2, fluido_1)
        H2 = ((H2s - H1) / n_is) + H1
        S2 = PropsSI("S", "P", P2, "H", H2, fluido_1)
        T2 = PropsSI("T", "P", P2, "S", S2, fluido_1)   # Temperature at point 2 (above condensation temperature)

        P3 = P2
        T3 = PropsSI("T", "P", P3, "Q", 0, fluido_1) - T_sub

        try:
          # Subcooled: uses T3
          H3 = PropsSI("H", "P", P3, "T", T3, fluido_1)
          S3 = PropsSI("S", "P", P3, "T", T3, fluido_1)
        except:
          # Saturated: uses Q = 0
          T3 = PropsSI("T", "P", P3, "Q", 0, fluido_1)
          H3 = PropsSI("H", "P", P3, "Q", 0, fluido_1)    # Considering saturated liquid at condenser outlet
          S3 = PropsSI("S", "P", P3, "Q", 0, fluido_1)


      ## Supercritical:

      ### NOTE: T_cond will be calculated later. The entry temperature is the outlet temperature of the gas cooler (ambient):

      else:

        ### Get P2 for better COP:
        P2_min = PropsSI("PCRIT", fluido_1) * 1.05  # Initial pressure (greater than critical)
        P2_max = P2_min * 2  # Upper limit of P2
        P2 = P2_min
        melhor_COP = 0
        P2_list = []
        COP_list = []

        while P2 < P2_max:
          try:

            S2s = S1  # Isentropic
            H2s = PropsSI("H", "S", S2s, "P", P2, fluido_1)
            H2 = ((H2s - H1) / n_is) + H1
            T2 = PropsSI("T", "H", H2, "P", P2, fluido_1)
            S2 = PropsSI("S", "P", P2, "H", H2, fluido_1)

            T3 = T_cond
            P3 = P2  # Gas cooler pressure = P2
            H3 = PropsSI("H", "P", P3, "T", T3, fluido_1)
            S3 = PropsSI("S", "P", P3, "H", H3, fluido_1)

            # Evaporator cooling [J/kg]
            q_evap_spec = H1 - H4

            # Compressor specific work input [J/kg], corrected for shell heat losses
            w_comp_spec = (H2 - H1) / (1 - r_Qc)

            COP = q_evap_spec / w_comp_spec

            P2_list.append(P2 / 1e5)  # Converting to bar
            COP_list.append(COP)

            if COP > melhor_COP:
                melhor_COP = COP
                melhor_P2 = P2

          except:
            pass

          P2 += 1e4  # Pressure increment [Pa]

        if fluido_escolhido == 1:
            #### Plot the COP vs. P2 curve
            plt.figure(figsize=(10, 6))
            plt.plot(P2_list, COP_list, label="COP vs P2", color="blue", linewidth=2)
            plt.axvline(melhor_P2 / 1e5, color="red", linestyle="--", label=f"Optimal P2 = {melhor_P2/1e5:.2f} bar")
            plt.xlabel("P2 (bar)", fontsize=12)
            plt.ylabel("COP", fontsize=12)
            plt.title("COP vs P2 Curve (Supercritical Fluid)", fontsize=14)
            plt.legend()
            plt.grid()
            #plt.show()
            with col2:
                with st.expander("Optimal Performance"):
                    optimal_cop_text = "Coefficient of Performance (COP) = "+str(melhor_COP)
                    st.markdown(optimal_cop_text)
                    st.pyplot(plt.gcf())

        ### Results for States 2 and 3:
        P2 = melhor_P2
        S2s = S1  # Isentropic
        H2s = PropsSI("H", "S", S2s, "P", P2, fluido_1)
        H2 = ((H2s - H1) / n_is) + H1
        T2 = PropsSI("T", "H", H2, "P", P2, fluido_1)
        S2 = PropsSI("S", "P", P2, "H", H2, fluido_1)

        T3 = T_cond
        P3 = P2  # Gas cooler pressure = P2
        H3 = PropsSI("H", "P", P3, "T", T3, fluido_1)
        S3 = PropsSI("S", "P", P3, "H", H3, fluido_1)

      # State 4

      H4 = H3
      P4 = P1
      T4 = PropsSI("T", "P", P4, "H", H4, fluido_1)

      ## Entropy at state 4
      try:
        Q4 = PropsSI("Q", "P", P4, "H", H4, fluido_1)
        S4 = PropsSI("S", "P", P4, "Q", Q4, fluido_1)
      except:
        ### Loop to obtain S4 (coolprop error):
        for i in np.arange(0, 1, 0.01):
          H4_vapor_saturado = PropsSI("H", "P", P4, "Q", i, fluido_1)
          if abs(H4 - H4_vapor_saturado)/H4 <= 0.01:
            Q4 = i
        S4 = PropsSI("S", "P", P4, "Q", Q4, fluido_1)


      # Mass flow rate

      m_dot = Q_evap/(H1 - H4)


      # Compressor power (Subcritical)

      W_c = ((H2-H1)*m_dot)/(1-r_Qc) # Compressor power [W]
      Q_c_loss = W_c * r_Qc  # Compressor losses [W]
      Q_cond = Q_evap + W_c - Q_c_loss  # Rejected heat [W]
      COP = Q_evap/W_c


      # Cycle points

      h_vals = [H1, H2, H3, H4, H1]
      s_vals = [S1, S2, S3, S4, S1]
      T_vals = [T1, T2, T3, T4, T1]
      p_vals = [P1, P2, P3, P4, P1]
      labels = ['1', '2', '3', '4', '1']



      if fluido_escolhido == 1:

          # Saturation curve

          T_min = PropsSI('Tmin', fluido_1) + 1
          T_max = PropsSI('Tcrit', fluido_1)
          temperatures = np.linspace(T_min, T_max, 500)
          s_liquid = [PropsSI('S', 'T', T, 'Q', 0, fluido_1) for T in temperatures]
          s_vapor = [PropsSI('S', 'T', T, 'Q', 1, fluido_1) for T in temperatures]
          h_liquid = [PropsSI('H', 'T', T, 'Q', 0, fluido_1) for T in temperatures]
          h_vapor = [PropsSI('H', 'T', T, 'Q', 1, fluido_1) for T in temperatures]
          p_sat = [PropsSI('P', 'T', T, 'Q', 0, fluido_1) / 1000 for T in temperatures]

          plt.figure(figsize=(10, 6))
          plt.plot(np.array(h_liquid) / 1000, p_sat, 'black')
          plt.plot(np.array(h_vapor) / 1000, p_sat, 'black')


          # P-h diagram

          plt.xlabel('Enthalpy (kJ/kg)')
          plt.ylabel('Pressure (kPa)')
          plt.title(f'P-h Diagram for the standard refrigeration cycle with {fluido_1}')
          plt.grid(True)

          ## Isentropic line between points 1 and 2
          if transc_cycle is False:
              press = np.linspace(P1, P2, 500)
              h_isent = []
              for P in press:
                  h_isent = h_isent + [PropsSI("H", "S", S1, "P", P, fluido_1)]

              plt.plot(np.array(h_vals[1:]) / 1000, np.array(p_vals[1:]) / 1000, 'bo-')
              plt.plot(np.array(h_isent) / 1000, press/1000, 'b--')
          else:
              plt.plot(np.array(h_vals) / 1000, np.array(p_vals) / 1000, 'bo-')

          ## Add numerical labels for each point using plt.annotate
          for i, label in enumerate(labels):
              plt.annotate(label,  # Label text
                          (h_vals[i]/1000, p_vals[i]/1000),  # Point position
                          textcoords="offset points",  # Offset coordinates to avoid overlap
                          xytext=(5,5),  # Position offset to adjust text visualization
                          ha='center', fontsize=10, color='blue')  # Alignment and style

          with col2:
              with st.expander("P-h Cycle Diagram"):
                st.pyplot(plt.gcf())


          # T-s diagram

          plt.figure(figsize=(10, 6))
          plt.plot(s_liquid, temperatures, 'black')
          plt.plot(s_vapor, temperatures, 'black')
          plt.plot(s_vals[0:2], [T1, T2], 'ro-')
          #plt.plot(s_vals[2:4], [T3, T4], 'ro-')

          ## Isobaric line between points 2 and 3

          P_critica = PropsSI("PCRIT", fluido_1)  # Critical pressure of the fluid

          if transc_cycle is True:   # If supercritical
              temp = np.linspace(T3, T2, 500)
              s_isob = []
              for T in temp:
                  s_isob = s_isob + [PropsSI("S", "T", T, "P", P2, fluido_1)]

          else:   # If subcritical
              T_sat0 = PropsSI("T", "Q", 0, "P", P2, fluido_1)
              T_sat1 = PropsSI("T", "Q", 1, "P", P2, fluido_1)

              temp = np.linspace(T3, T2, 500).astype(int)   # Remove CoolProp bugs
              temp = np.unique(temp)
              s_isob = []
              for T in temp:
                  if T<T_sat0:
                      s_isob = s_isob + [PropsSI("S", "T", T, "P", P2, fluido_1)]
                  elif T>=T_sat0 and T<=T_sat1:
                      titulo = PropsSI("Q", "T", T, "P", P2, fluido_1)
                      s_isob = s_isob + [PropsSI("S", "Q", titulo, "P", P2, fluido_1)]
                  elif T>T_sat1:
                      s_isob = s_isob + [PropsSI("S", "T", T, "P", P2, fluido_1)]

          #s_isob = [PropsSI('S', 'T', T, 'P', P2, fluido_1) for T in temp]

          plt.plot(s_isob, temp, 'red')

          ## Isobaric line between points 4 and 1

          T_sat0 = PropsSI("T", "Q", 0, "P", P1, fluido_1)
          T_sat1 = PropsSI("T", "Q", 1, "P", P1, fluido_1)
          S_sat1 = PropsSI("S", "Q", 1, "P", P1, fluido_1)

          if T1 > T_sat1:   # For the supersaturated portion
              plt.plot(s_vals[2:4], [T3, T4], 'ro-')
              plt.plot([s_vals[3], S_sat1, s_vals[4]], [T4, T_sat1, T1], 'r-', marker='o', markevery=[0, 2])
          else:
              plt.plot(s_vals[2:5], [T3, T4, T1], 'ro-')

          plt.xlabel('Entropy (J/kg·K)')
          plt.ylabel('Temperature (K)')
          plt.title(f'T-s Diagram for the standard refrigeration cycle with {fluido_1}')
          plt.grid(True)

          ## Add labels for each point
          for i, label in enumerate(labels):
              plt.annotate(label,  # Label text
                          (s_vals[i], T_vals[i]),  # Point position
                          textcoords="offset points",  # Offset coordinates to avoid overlap
                          xytext=(5,5),  # Position offset to adjust text visualization
                          ha='center', fontsize=10, color='red')  # Alignment and style
          with col2:
              with st.expander("T-s Cycle Diagram"):
                st.pyplot(plt.gcf())

      # * Volumetric cooling capacity [kJ/m³]
      try:
        VCC = ((H1-H4)/1000)*PropsSI("D", "Q", 1, "P", P1, fluido_1)
      except:
        VCC = np.nan

      # Return results

      dict_result = {
          "State": labels[:-1],
          "h [J/kg]": h_vals[:-1],
          "s [J/kg·K]": s_vals[:-1],
          "T [K]": T_vals[:-1],
          "P [Pa]": p_vals[:-1],
          "Mass flow rate [kg/s]": m_dot,
          "Q_f [W]": Q_evap,
          "W_c [W]": W_c,
          "Q_c [W]": Q_c_loss,
          "Q_q [W]": Q_cond,
          'COP': COP,
          'Volumetric Cooling Capacity [kJ/m³]': VCC,
          'Isentropic Efficiency of Compressor': n_is,
          "Transcritical?": transc_cycle,
          "Fluid": fluido_1
      }

      if transc_cycle is True:    # Isentropic Average Temperature for the Gas Cooler
        dict_result['Gas Cooler Avg. Temperature [K]'] = abs(
            (dict_result['h [J/kg]'][1] - dict_result['h [J/kg]'][2]) /
            (dict_result['s [J/kg·K]'][1] - dict_result['s [J/kg·K]'][2])
        )

      if fluido_escolhido == 1:
          #display(pd.DataFrame(dict_result))
          col2.dataframe(pd.DataFrame(dict_result), use_container_width=True)


      return dict_result


  except:
    return 0

#   PERFORMANCE ANALYSIS
def calculo_exergia_padrao(dados, T_H, T_L):
    # Ambient conditions
    P0 = 101325  # Ambient pressure [Pa]
    T0 = T_H  # In refrigeration systems, the reference temperature is typically set to the temperature of the high-temperature medium

    # Exergy Destruction Rate for the Compressor (1-2)

    B_dc = (
            (1 - (T0 / ((dados['T [K]'][0] + dados['T [K]'][1]) / 2))) * dados['Q_c [W]'] + dados['W_c [W]']
            + dados['Mass flow rate [kg/s]'] *
            (dados['h [J/kg]'][0] - dados['h [J/kg]'][1]
             - T0 * (dados['s [J/kg·K]'][0] - dados['s [J/kg·K]'][1]))
    )

    # Exergy Destruction Rate for the Gas Cooler/Condenser (2-3)

    # Tme_Q = dados['T [K]'][1] if dados['Transcritical?'] is False else abs(
    #    (dados['h [J/kg]'][1] - dados['h [J/kg]'][2]) / (dados['s [J/kg·K]'][1] - dados['s [J/kg·K]'][2])
    # )  # Entropic average temperature if transcritical

    B_dQ = (
            (1 - (T0 / T_H)) * dados['Q_q [W]']
            + dados['Mass flow rate [kg/s]'] *
            (dados['h [J/kg]'][1] - dados['h [J/kg]'][2]
             - T0 * (dados['s [J/kg·K]'][1] - dados['s [J/kg·K]'][2]))
    )

    # Exergy Destruction Rate for the Expansion Device (3-4)

    B_dE = (
            dados['Mass flow rate [kg/s]'] * T0 * (dados['s [J/kg·K]'][3] - dados['s [J/kg·K]'][2])
    )

    # Exergy Destruction Rate for the Evaporator (4-1)

    B_dF = (
            ((T0 / T_L) - 1) * dados['Q_f [W]']
            + dados['Mass flow rate [kg/s]'] *
            (dados['h [J/kg]'][3] - dados['h [J/kg]'][0]
             - T0 * (dados['s [J/kg·K]'][3] - dados['s [J/kg·K]'][0]))
    )

    # Total Exergy Destruction Rate
    B_d_total = B_dc + B_dQ + B_dE + B_dF

    B_d = {
        'Compressor': B_dc / 1e3,
        'Gas Cooler': B_dQ / 1e3,
        'Expansion Device': B_dE / 1e3,
        'Evaporator': B_dF / 1e3
    } if dados["Transcritical?"] == True else {
        'Compressor': B_dc / 1e3,
        'Condenser': B_dQ / 1e3,
        'Expansion Device': B_dE / 1e3,
        'Evaporator': B_dF / 1e3
    }

    # Relative Exergy Destruction Rates
    r_B = {
        'Compressor': B_dc / B_d_total,
        'Gas Cooler': B_dQ / B_d_total,
        'Expansion Device': B_dE / B_d_total,
        'Evaporator': B_dF / B_d_total
    } if dados["Transcritical?"] == True else {
        'Compressor': B_dc / B_d_total,
        'Condenser': B_dQ / B_d_total,
        'Expansion Device': B_dE / B_d_total,
        'Evaporator': B_dF / B_d_total
    }

    # Exergy Efficiency
    B_gain_expr = ((T0 / T_L) - 1) * dados['Q_f [W]']
    B_cost_expr = (
            dados['Mass flow rate [kg/s]'] *
            (dados['h [J/kg]'][1] - dados['h [J/kg]'][0])  # Compressor work
    )
    n_B = B_gain_expr / B_cost_expr

    # Final result in a dictionary in kW
    resultados = {
        'B_d [kW]': B_d,
        'B_d_total [kW]': B_d_total / 1e3,
        'r_B': r_B,
        'n_B': n_B,
        'VCC [MJ/m³]': dados['Volumetric Cooling Capacity [kJ/m³]'] / 1000 if dados[
                                                                                  'Volumetric Cooling Capacity [kJ/m³]'] is not np.nan else np.nan,
        'COP': dados['COP'] if dados['COP'] is not np.nan else np.nan,
        'Compressor Power [kW]': dados['W_c [W]'] / 1000 if dados['W_c [W]'] is not np.nan else np.nan,
        'Fluid': dados['Fluid']
    }

    # print(dados['COP'], dados['Fluid'])

    return resultados

#   EXERGY PLOT
def Bd_comparativo(list_dict_exergia, list_dados):

  # Extracting the exergy destruction data for all fluids

  states = [dados["Fluid"] for dados in list_dados]
  transcritical = [dados["Transcritical?"] for dados in list_dados]

  # Initializing the lists of exergy destruction by component
  compressor = [dict_exergia['B_d [kW]']['Compressor'] for dict_exergia in list_dict_exergia]

  # Checking if the key name is 'Gas Cooler' or 'Condenser' and adjusting
  condenser = [
      dict_exergia['B_d [kW]'].get('Condenser', dict_exergia['B_d [kW]'].get('Gas Cooler', 0))
      for dict_exergia in list_dict_exergia
  ]

  expansion = [dict_exergia['B_d [kW]']['Expansion Device'] for dict_exergia in list_dict_exergia]
  evaporator = [dict_exergia['B_d [kW]']['Evaporator'] for dict_exergia in list_dict_exergia]

  # Setting up the chart
  plt.figure(figsize=(10, 6))
  x = np.arange(len(states))  # Positions for the bars
  width = 0.6  # Width of the bars

  # Creating the stacked chart
  compressor_bars = plt.bar(x, compressor, width=width, label='Compressor', color='#1984c5')
  condenser_bars = plt.bar(x, condenser, width=width, bottom=compressor, label='Condenser/Gas Cooler', color='#FF7F50')
  expansion_bars = plt.bar(x, expansion, width=width, bottom=np.array(compressor) + np.array(condenser), label='Expansion Device', color='#9B9B9B')
  evaporator_bars = plt.bar(x, evaporator, width=width, bottom=np.array(compressor) + np.array(condenser) + np.array(expansion), label='Evaporator', color='#badbdb')


  # Adding the COP value inside the bars
  for i, (comp_bar, cond_bar, exp_bar, evap_bar, dados) in enumerate(zip(compressor_bars, condenser_bars, expansion_bars, evaporator_bars, list_dados)):
    # Calculating the positions for the values inside the bars
    y_pos = comp_bar.get_height() + cond_bar.get_height() + exp_bar.get_height() + evap_bar.get_height() / 2
    # Adding the text (COP) on the bar, rotated vertically
    plt.text(comp_bar.get_x() + comp_bar.get_width() / 2, y_pos, f'COP = {dados["COP"]:.2f}', ha='center', va='center', rotation=90, fontsize=10)


  # Setting custom labels
  plt.xticks(x, states, rotation=45, ha='right')  # Initial tilt
  labels = plt.gca().get_xticklabels()  # Getting the X-axis labels

  # Adjusting colors locally based on a condition
  for i, (state, transcritical_) in enumerate(zip(states, transcritical)):
      if transcritical_:  # Condition for a different color (True)
          labels[i].set_color('red')  # Red
      else:
          labels[i].set_color('black')  # Default black

  plt.ylabel('Exergy Destruction (kW)')
  plt.xlabel('Cycles')
  plt.title('Exergy Destruction by Component')
  plt.legend()

  # Show the chart
  #plt.show()
  st.markdown(":red[Transcritical] | Subcritical")
  st.pyplot(plt.gcf())


#   PROCESSING
def processar_ciclos_refrigeracao(T_evap, T_cond, T_L, T_H, n_is, Q_evap, r_Qc, fluido_1, fluid_list, T_sup=0, T_sub=0):

    # Basic input validation
    if not isinstance(T_evap, (int, float)) or not isinstance(T_cond, (int, float)):
        col2.error("Error: T_evap and T_cond must be numbers.")
        return False
    if not isinstance(n_is, (int, float)) or not (0 <= n_is <= 1):
        col2.error("Error: n_is must be a number between 0 and 1.")
        return False
    if not isinstance(Q_evap, (int, float)) or Q_evap <= 0:
        col2.error("Error: Q_evap must be a positive number.")
        return False
    if not isinstance(r_Qc, (int, float)) or r_Qc < 0:
        col2.error("Error: r_Qc must be a positive number.")
        return False
    if not isinstance(fluido_1, str):
        col2.error("Error: Failed to process the chosen fluid.")
        return False

    # List of alternative fluids
    lista_de_fluidos = fluid_list

    # Remove the chosen initial fluid from the list
    if fluido_1 in lista_de_fluidos:
        lista_de_fluidos.remove(fluido_1)

    try:

        # Calculate the cycle for the chosen fluid
        st.subheader("Refrigerant Cycle", anchor=False)
        result_fluido_escolhido = ciclo_refrigeracao(
            T_evap, T_cond, n_is, Q_evap, r_Qc, fluido_1=fluido_1, T_sup=T_sup, T_sub=T_sub, fluido_escolhido=1
        )

        # Check if the result for the chosen fluid is valid
        if result_fluido_escolhido == 0 or result_fluido_escolhido is None:
            col2.error(f"Error: Failed to process the chosen fluid '{fluido_1}'.")
            return False

        # Initialize lists for data and exergies
        list_dict_exergia = [calculo_exergia_padrao(result_fluido_escolhido, T_H, T_L)]
        list_dados = [result_fluido_escolhido]

        # Calculate the average condensation temperature (Tc_)
        Tc_ = abs(
            (result_fluido_escolhido['h [J/kg]'][1] - result_fluido_escolhido['h [J/kg]'][2]) /
            (result_fluido_escolhido['s [J/kg·K]'][1] - result_fluido_escolhido['s [J/kg·K]'][2])
        )
        
        fluidos_remover = []
        # Process cycles for alternative fluids
        for fluido in lista_de_fluidos:
            try:

                T_critica = PropsSI("TCRIT", fluido)  # Critical temperature of the fluid

                if T_cond >= T_critica:   # If supercritical
                    dados_ = ciclo_refrigeracao(
                    T_evap, T_cond, n_is, Q_evap, r_Qc, fluido_1=fluido, T_sup=T_sup, T_sub=T_sub, fluido_escolhido=0
                )
                else:
                    dados_ = ciclo_refrigeracao(
                    T_evap, Tc_, n_is, Q_evap, r_Qc, fluido_1=fluido, T_sup=T_sup, T_sub=T_sub, fluido_escolhido=0
                )

                # Add results to the lists
                list_dados.append(dados_)
                list_dict_exergia.append(calculo_exergia_padrao(dados_, T_H, T_L))

            except Exception as e:
                print(f"Error processing fluid {fluido}: {e}")
                fluidos_remover.append(fluido)
                continue

        
        # Process the data for the exergy table
        lista_de_fluidos = [f for f in lista_de_fluidos if f not in fluidos_remover]
        fluidos = [fluido_1] + lista_de_fluidos
        
        tabela = []
        #print("\n\n * Exergy Destruction Data and Exergy Efficiency:\n")
        for i, item in enumerate(list_dict_exergia):

            if fluidos[i] in fluidos_remover:
                continue
            linha = {
                'Fluid': fluidos[i],
                'Exergy Loss Compressor [kW]': item['B_d [kW]'].get('Compressor', None),
                'Exergy Loss Condenser/Gas Cooler [kW]': item['B_d [kW]'].get('Condenser', item['B_d [kW]'].get('Gas Cooler', None)),
                'Exergy Loss Expansion Device [kW]': item['B_d [kW]'].get('Expansion Device', None),
                'Exergy Loss Evaporator [kW]': item['B_d [kW]'].get('Evaporator', None),
                'Total Exergy Loss [kW]': item['B_d_total [kW]'],
                'Relative Exergy Loss Compressor': item['r_B'].get('Compressor', None),
                'Relative Exergy Loss Condenser/Gas Cooler': item['r_B'].get('Condenser', item['r_B'].get('Gas Cooler', None)),
                'Relative Exergy Loss Expansion Device': item['r_B'].get('Expansion Device', None),
                'Relative Exergy Loss Evaporator': item['r_B'].get('Evaporator', None),
                'Exergy Efficiency': item['n_B'],
                'Volumetric Cooling Capacity [MJ/m³]': item['VCC [MJ/m³]'] if 'VCC [MJ/m³]' in item else np.nan,
                'COP': item['COP'] if 'COP' in item else np.nan,
                'Compressor Power [kW]': item['Compressor Power [kW]'] if 'Compressor Power [kW]' in item else np.nan
            }
            tabela.append(linha)

        # Create the DataFrame
        df_list_dict_exergia = pd.DataFrame(tabela)

        # Display the table
        #display(df_list_dict_exergia.head(1))
        st.divider()
        st.subheader("Performance Analysis", anchor=False)
        col2.dataframe(df_list_dict_exergia.head(1), use_container_width=True)

        list_dados = [x for x in list_dados if x != 0]

        return list_dados, list_dict_exergia, df_list_dict_exergia

    except KeyError as ke:
        col2.error(f"Key error accessing data for fluid '{fluido_1}': {ke}")
        return False
    except ZeroDivisionError as zde:
        col2.error(f"Zero division error calculating Tc_: {zde}")
        return False
    except Exception as e:
        col2.error(f"Unexpected error processing cycles: {e}")
        return False


#   ENVIRONMENT

def environmental_effects(fluido_1, fluid_list):
    # List of alternative fluids
    lista_de_fluidos = fluid_list

    # Remove the chosen initial fluid from the list
    if fluido_1 in lista_de_fluidos:
        lista_de_fluidos.remove(fluido_1)

    refrigerants = lista_de_fluidos + [fluido_1]

    gwp20 = []
    gwp100 = []
    gwp500 = []

    # Retrieve GWP values for each refrigerant
    for refrigerant in refrigerants[:]:
        try:
            gwp20_value = PropsSI('GWP20', refrigerant)
            gwp100_value = PropsSI('GWP100', refrigerant)
            gwp500_value = PropsSI('GWP500', refrigerant)

            gwp20.append(gwp20_value)
            gwp100.append(gwp100_value)
            gwp500.append(gwp500_value)

        except Exception as e:
            refrigerants.remove(refrigerant)  # Remove invalid refrigerants
            print(f"Error with {refrigerant}: {e}")
            pass

    y = np.arange(len(refrigerants))  # Positions for the refrigerants
    height = 0.2  # Bar height

    fig, ax = plt.subplots(figsize=(10, 6))

    # Creating horizontal bars for GWP20, GWP100, and GWP500
    bars_gwp20 = ax.barh(y - height, gwp20, height, label='20-year GWP', color='#1984c5')
    bars_gwp100 = ax.barh(y, gwp100, height, label='100-year GWP', color='#FF7F50')
    bars_gwp500 = ax.barh(y + height, gwp500, height, label='500-year GWP', color='#9B9B9B')

    # Adding the values to the right of the bars
    for bar in bars_gwp20:
        width = bar.get_width()
        ax.text(width + 30, bar.get_y() + bar.get_height() / 2, f'{int(width)}', va='center', fontsize=10,
                color='#1984c5')

    for bar in bars_gwp100:
        width = bar.get_width()
        ax.text(width + 30, bar.get_y() + bar.get_height() / 2, f'{int(width)}', va='center', fontsize=10,
                color='#FF7F50')

    for bar in bars_gwp500:
        width = bar.get_width()
        ax.text(width + 30, bar.get_y() + bar.get_height() / 2, f'{int(width)}', va='center', fontsize=10,
                color='#9B9B9B')

    # Customizing the Y-axis
    ax.set_yticks(y)
    ax.set_yticklabels(refrigerants)
    ax.set_xlabel('GWP')
    ax.set_ylabel('Refrigerants')
    ax.set_title('Global Warming Potential (GWP) for Different Refrigerants')

    # Adjusting the X-axis limit to ensure the values fit
    ax.set_xlim(0, max(max(gwp20), max(gwp100), max(gwp500)) + 1000)  # Adjust the upper limit of the X-axis

    # Displaying the legend
    fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))

    # Adjusting the layout to avoid clipping
    plt.tight_layout()

    # Display the chart
    st.pyplot(plt.gcf())
        #plt.show()


################# RUNNING #################

col2.subheader("Results", anchor=False, divider='gray')

if run_button:

  with col2:

    with st.spinner('Loading...'):

        list_dados, list_dict_exergia, df_list_dict_exergia = processar_ciclos_refrigeracao(T_evap, T_cond, T_L, T_H, n_is, Q_evap, r_Qc, fluido_1, fluid_list, T_sup, T_sub)

        with st.expander("Comparative analysis for various fluids"):
            if list_dados[0]['Transcritical?'] == True:
                st.warning('In transcritical systems, comparisons with subcritical systems are based on the average entropic temperature of the gas cooler, which is assumed to be the condensing temperature for subcritical systems.', icon="⚠️")
            st.dataframe(df_list_dict_exergia, use_container_width=True)
            Bd_comparativo(list_dict_exergia, list_dados)

        st.divider()
        st.subheader("Environmental Effects", anchor=False)
        with st.expander("GWP Analysis"):
            environmental_effects(fluido_1, fluid_list)

        ################# DOWNLOAD #################

        st.divider()

        # Download Button

        import io

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as excel_writer:

            df_list_dados = pd.DataFrame(list_dados[0])
            df_list_dados.to_excel(excel_writer, sheet_name='Refrigeration Cycle Data', index=True)
            df_list_dict_exergia.to_excel(excel_writer, sheet_name='Exergetic Analysis', index=False)

            # Close the Pandas Excel writer and output the Excel file to the buffer
            excel_writer.close()

            col2.download_button(
                label="⬇️ Download Refrigeration Cycle Data",
                data=buffer,
                file_name=str(fluido_1)+"_Ref_Cycle_Data.xlsx",
                use_container_width=True
            )

else:
  col2.markdown("Click on 'Run'")


