import pandas as pd
import numpy as np
import streamlit as st

# Everything will be in english except text meant to be read by the user.

#Available tariffs for queries
options_tariffs = ['GDMTH', 'DIST', 'DIT']

#Turn CSV to Pandas Dataframe
data = pd.read_csv('TFSB.csv')
data = data.replace(np.nan,'-',regex=True)


#Get only GDMTH DIST and DIT Tariffs
data = data[data['Tarifa'].isin(options_tariffs)]

#Get unique months list for multiselection
options_months = data['Mes'].unique().tolist()

#Get unique division list for multiselection
options_division = data['Division'].unique().tolist()


def get_regulated_charges(data):
    transmision = float(data.loc[data['Segmento'] == 'Transmision','Cargos tarifarios'].item())
    cenace = float(data.loc[data['Segmento'] == 'CENACE','Cargos tarifarios'].item())
    SCnMEM = float(data.loc[data['Segmento'] == 'SCnMEM','Cargos tarifarios'].item()) 
    regulated_charges = transmision + cenace + SCnMEM
    return regulated_charges

def add_regulated_to_energy_tariffs(data,regulated_charges):
    for i in ['B','I','P','SP']:
        try:
            data.loc[data['Int. Horario'] == i,'Cargos tarifarios'] = float(data.loc[data['Int. Horario'] == i,'Cargos tarifarios'].item()) +  regulated_charges
        except:
            pass

def delete_unwanted_rows(data):
    data = data[~data['Segmento'].str.contains('Transmision')]
    data = data[~data['Segmento'].str.contains('CENACE')]
    data = data[~data['Segmento'].str.contains('SCnMEM')]
    data = data[~data['Int. Horario'].str.contains('SP')]
    return data



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

selected_division = st.sidebar.radio('Seleccion una división:', options_division)




try:
    data = data[(data['Mes'] == selected_months[0]) &
                  (data['Division'] == selected_division) &
                  (data['Tarifa'] == selected_tariff)]


    reg_charges = get_regulated_charges(data)
    add_regulated_to_energy_tariffs(data,reg_charges)

    data = data.drop(columns=['Mes','Division','Tarifa'])

    data = delete_unwanted_rows(data)




    st.subheader(f'{selected_tariff} - {selected_months[0].capitalize()} - {selected_division}')
    st.write(data)
except:
    st.warning('''🚧 Por ahora solo podemos trabajar con un mes seleccionado.
    Estamos trabajando para que puedas consultar multiples meses.''')
