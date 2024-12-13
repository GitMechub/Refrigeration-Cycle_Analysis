https://refcycleanalysis.streamlit.app/

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
