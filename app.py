import pandas as pd
import streamlit as st
from download import download_button
from pandasql import sqldf

st.set_page_config(layout='wide')

aruti_report = st.sidebar.file_uploader("Enter the Payroll Report (Aruti Data) file as a Excel")
custom_report = st.sidebar.file_uploader("Enter the Custom Report file as an CSV")
deducted_breaks_report = st.sidebar.file_uploader("Enter the Deducted Breaks file as a CSV")

# def cost_automator(custom, payroll, deducted_breaks):
custom = pd.read_csv(custom_report)
payroll = pd.read_excel(aruti_report)
deducted_breaks = pd.read_csv(deducted_breaks_report)

payroll = payroll[['Code','Total Earning']]
total_earning = payroll['Total Earning'].sum()

custom.replace("Call Center",'Support Office (Call Center)',inplace=True)
custom.replace("Umoja Clinic",'Umoja 2',inplace=True)
custom.replace("Labtech",'Lab Tech',inplace=True)

custom2 = custom.groupby(['eid'], as_index=False)['total_time'].sum()

custom2 = pd.merge(
        custom2,
        deducted_breaks,
        left_on='eid',
        right_on = 'eid',
        how = 'left'
    )

custom2 = custom2[['eid', 'total_time', 'Hours']]

custom = custom.groupby(['employee','eid','location','schedule_name'], as_index=False)['total_time'].sum()

custom = pd.merge(
    custom,
    custom2,
    left_on='eid',
    right_on='eid',
    how='left'
)

custom = pd.merge(
    custom,
    payroll,
    left_on='eid',
    right_on='Code',
    how='left'
)

custom['total_time'] = (custom['total_time_x']/custom['total_time_y']) * custom['Hours']
custom['Total_Earning'] = (custom['total_time_x']/custom['total_time_y']) * custom['Total Earning']

del custom['total_time_x']
del custom['total_time_y']
del custom['Hours']
del custom['Code']
del custom['Total Earning']

location = custom.groupby(['location'], as_index=False).agg({'total_time':'sum','Total_Earning':'sum'})
so_cost = total_earning - location['Total_Earning'].sum()
new_row = {'location':'Support Office', 'total_time':0, 'Total_Earning':so_cost}
location = location.append(new_row, ignore_index=True)
st.write(location)
download_button_str = download_button(location, f"Staff Cost by Location.csv", 'Download CSV', pickle_it=False)
st.markdown(download_button_str, unsafe_allow_html=True)

cadre = custom.groupby(['schedule_name'], as_index=False).agg({'total_time':'sum','Total_Earning':'sum'})
st.write(cadre)
download_button_str = download_button(cadre, f"Staff Cost by Cadre.csv", 'Download CSV', pickle_it=False)
st.markdown(download_button_str, unsafe_allow_html=True)

del payroll
del deducted_breaks
del custom
del custom2

# pysqldf = lambda q: sqldf(q, globals())
# q = """
#     SELECT *
#     FROM custom
# """
# custom2 = pysqldf(q)

# download_button_str = download_button(custom2, f"Staff Cost by Cadre.csv", 'Download CSV', pickle_it=False)
# st.markdown(download_button_str, unsafe_allow_html=True)
