import pandas as pd
import numpy as np
from pkg_resources import Distribution
import streamlit as st

# Everything will be in english except text meant to be read by the user.

st.set_page_config(
    page_title="Tarifas de CFE",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)


#Available tariffs for queries
options_tariffs = ['GDMTH', 'DIST', 'DIT']

#Turn CSV to Pandas Dataframe

@st.cache
def get_data():
    data = pd.read_csv('TFSB.csv')
    #Replace NaN with dashes "-" for readability
    data = data.replace(np.nan,'-',regex=True)
    #Get only GDMTH DIST and DIT Tariffs
    data = data[data['Tarifa'].isin(options_tariffs)]
    return data

data = get_data()



#Get unique months list for multiselection
options_months = data['Mes'].unique().tolist()
#Get unique division list for multiselection
options_division = data['Division'].unique().tolist()


def get_regulated_charges(data):
    global transmision, cenace, SCnMEM
    transmision = float(data.loc[data['Segmento'] == 'Transmision','Cargos tarifarios'].item())
    cenace = float(data.loc[data['Segmento'] == 'CENACE','Cargos tarifarios'].item())
    SCnMEM = float(data.loc[data['Segmento'] == 'SCnMEM','Cargos tarifarios'].item()) 
    regulated_charges = transmision + cenace + SCnMEM
    return regulated_charges


def add_regulated_to_energy_tariffs(data,regulated_charges):
    for i in ['B','I','P','SP']:
        try:
            data.loc[data['Int. Horario'] == i,'Cargos tarifarios'] = round(float(data.loc[data['Int. Horario'] == i,'Cargos tarifarios'].item()) +  regulated_charges,4)
        except:
            pass

def delete_unwanted_rows(data):
    data = data[~data['Segmento'].str.contains('Transmision')]
    data = data[~data['Segmento'].str.contains('CENACE')]
    data = data[~data['Segmento'].str.contains('SCnMEM')]
    data = data[~data['Int. Horario'].str.contains('SP')]
    return data

def get_cfe_tariffs(data,selected_tariff):
    e_price_base = float(data.loc[data['Int. Horario'] == 'B','Cargos tarifarios'].item())
    e_price_int = float(data.loc[data['Int. Horario'] == 'I','Cargos tarifarios'].item())
    e_price_peak = float(data.loc[data['Int. Horario'] == 'P','Cargos tarifarios'].item())

    capacity_price = float(data.loc[data['Segmento'] == 'Capacidad','Cargos tarifarios'].item())

    if selected_tariff == 'GDMTH':
        distribution_price = float(data.loc[data['Segmento'] == 'Distribucion','Cargos tarifarios'].item())
    else:
        distribution_price = 0

    monthlyfixed_price = float(data.loc[data['Segmento'] == 'Suministro','Cargos tarifarios'].item().replace(',',''))

    return e_price_base, e_price_int, e_price_peak, capacity_price, distribution_price,monthlyfixed_price

days_in_month = {'enero':31,
 'febrero':28,
 'marzo':31,
 'abril':30,
 'mayo':31,
 'junio':30,
 'julio':31,
 'agosto':31,
 'septiembre':30,
 'octubre':31,
 'noviembre':30,
 'diciembre':31}

def calculate_cfe(tariffs,Eb,Ei,Ep,Db,Di,Dp,selected_months,selected_tariff):
    energy_charges = round(tariffs[0] * Eb + tariffs[1] * Ei + tariffs[2] * Ep,2)

    load_factor = 0.57 if selected_tariff == 'GDMTH' else 0.74 if selected_tariff == 'DIST' else 0.71

    capacity_charge = round(tariffs[3] * min(Dp,(Eb+Ei+Ep)/( 24 * days_in_month[selected_months.split(' ',1)[0]]  * load_factor )),2)

    distribution_charge = round(tariffs[4] * min(max(Db,Di,Dp),(Eb+Ei+Ep)/( 24 * days_in_month[selected_months.split(' ',1)[0]]  * load_factor )),2)

    return energy_charges,capacity_charge,distribution_charge


# In streamlit



# SIDEBAR
st.sidebar.header('Busca tu tarifa')
selected_months = st.sidebar.multiselect('Selecciona un mes:', options_months,help="Solo 1 mes")

if not selected_months:
    st.sidebar.info('Selecciona un mes')

selected_tariff = st.sidebar.radio('Seleccion una tarifa:', options_tariffs)
selected_division = st.sidebar.radio('Seleccion una división:', options_division)



# MAIN BODY
#Header and welcome text
'''
## Tarifas de Suministro Básico
Comisión Federal de Electricidad
'''


# EXPANDERS
info_expander = st.beta_expander('Cómo Funciona ❓')
about_expander = st.beta_expander('¡Hola! 👋')

with info_expander:
    '''
    ### Para consultar la tarifa:
    En el panel de la izquierda asegurate de seleccionar:

    - Mes de consulta
    - Tarifa a Consultar (por ahora solo incluye GDMTH, DIST y DIT)
    - División de CFE

    
    ### Para calcular tu recibo de CFE:
    1. Asegura primero haber consultado una tarifa siguiendo los pasos anteriores
    2. Inserta tu consumo de energía en horario base, intermedia y punta en kWh
    3. Inserta tu demanda en horario base, intermedia y punta en kW
    4. Haz clic en "Calcular mi recibo"

    **Nota:** No considera cálculo de cargo y/o bonificación por factor de potencia.
    

    '''

with about_expander:
        '''
        ¡Hola! Mucho gusto, soy [Gerardo](https://www.linkedin.com/in/geramr/).
        Hice esta herramienta para consultar las tarifas de CFE y puedas estimar tu recibo.

        Para sugerencias, ideas o cambios de esta herramienta (o si algo no funciona), [mándame un correo.](mailto:geramoralesrico@gmail.com)
        También puedes ver el código en [GitHub](https://github.com/geramrico/tarifas-cfe).

        _Tech Stack_:
        - Python
        - Librerías: Pandas y Numpy
        - Datos: CSV
        - Frontend: Streamlit


        Si tienes necesidad o idea de un proyecto, escríbeme y con gusto te ayudo con lo que pueda.

        -GM

    '''

st.markdown('***')

has_ran = False

# Display Results
try:
    data = data[(data['Mes'] == selected_months[0]) &
                  (data['Division'] == selected_division) &
                  (data['Tarifa'] == selected_tariff)]

    reg_charges = get_regulated_charges(data)
    add_regulated_to_energy_tariffs(data,reg_charges)

    data = data.drop(columns=['Mes','Division','Tarifa'])
    data = delete_unwanted_rows(data)
    data = data.reset_index(drop=True)

    st.subheader(f'{selected_tariff} - {selected_months[0].capitalize()} - {selected_division}')
    st.write(data)
    has_ran = True

except:
    st.warning('''🚧 Hay un error. No hay info disponible o quizá no seleccionaste un mes.''')


if has_ran:
    tariffs = get_cfe_tariffs(data,selected_tariff)

    view_reg_charges = st.checkbox('Mostrar cargos regulados')
    if view_reg_charges:
        st.write('Tarifas Reguladas (MXN/kWh)')
        st.write({'Transmision':transmision,
                'CENACE':cenace,
                'Servicios Conexos no MEM':SCnMEM})
    st.markdown('***')


    with st.form(key='my_form'):
        st.subheader('Calcula tu recibo de CFE')
        col1,col2 = st.beta_columns(2)
        
        kWh_base = col1.number_input('Consumo Base kWh',min_value=0)
        kWh_intermediate = col1.number_input('Consumo Intermedia kWh',min_value=0)
        kWh_peak = col1.number_input('Consumo Punta kWh',min_value=0)
        kW_base = col2.number_input('Demanda Base kW',min_value=0)
        kW_intermediate = col2.number_input('Demanda Intermedia kW',min_value=0)
        kW_peak = col2.number_input('Demanda Punta kW',min_value=0)
        submit_button = st.form_submit_button('Calcula mi recibo')
        energy_charge, capacity_charge, distribution_charge = calculate_cfe(tariffs,kWh_base,kWh_intermediate,kWh_peak,kW_base,kW_intermediate,kW_peak,selected_months[0],selected_tariff)
    
    if submit_button:
        
        st.write('Cargo por Energía: ',energy_charge, 'MXN')
        st.write('Cargo por Capacidad: ',capacity_charge, 'MXN')
        st.write('Cargo por Distribución: ',distribution_charge, 'MXN')
        st.write('Cargo Fijo Mensual: ',tariffs[5], 'MXN')
        st.write('TOTAL: ',tariffs[5], 'MXN')


