import pandas as pd
import streamlit as st

# Everything will be in english except text meant to be read by the user.

#Available tariffs for queries
options_tariffs = ['GDMTH', 'DIST', 'DIT']

#Turn CSV to Pandas Dataframe
data = pd.read_csv('TFSB.csv')

#Get only GDMTH DIST and DIT Tariffs
data = data[data['Tarifa'].isin(options_tariffs)]

#Get unique months list for multiselection
options_months = data['Mes'].unique().tolist()

#Get unique division list for multiselection
options_division = data['Division'].unique().tolist()


# In streamlit

#Header and welcome text
'''
# Tarifas de Suministro Básico
## Comisión Federal de Electricidad
#

'''


selected_months = st.sidebar.multiselect(
    'Selecciona un mes:', options_months)

if not selected_months:
    st.sidebar.info('Selecciona un mes')


selected_tariff = st.sidebar.radio('Seleccion una tarifa:', options_tariffs)

selected_division = st.sidebar.radio(
    'Seleccion una división:', options_division)


try:
    result = data[(data['Mes'] == selected_months[0]) &
                  (data['Division'] == selected_division) &
                  (data['Tarifa'] == selected_tariff)]

    st.subheader(f'{selected_tariff} - {selected_months[0].capitalize()}')
    st.write(result)
except:
    st.warning('''🚧 Por ahora solo podemos trabajar con un mes seleccionado.
    Estamos trabajando para que puedas consultar multiples meses.''')
