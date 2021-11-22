import pandas as pd
import streamlit as st
from download import download_button
from pandasql import sqldf

st.set_page_config(layout='wide')

aruti_report = st.sidebar.file_uploader("Enter the Payroll Report (Aruti Data) file as a Excel")
custom_report = st.sidebar.file_uploader("Enter the Custom Report file as an CSV")
# deducted_breaks_report = st.sidebar.file_uploader("Enter the Deducted Breaks file as a CSV")

# def cost_automator(custom, payroll):
custom = pd.read_csv(custom_report)
payroll = pd.read_excel(aruti_report)
# deducted_breaks = pd.read_csv(deducted_breaks_report)



custom.replace("Call Center",'Support Office (Call Center)',inplace=True)
custom.replace("Umoja Clinic",'Umoja 2',inplace=True)

pysqldf = lambda q: sqldf(q, globals())
q = """
    SELECT *
    FROM custom
"""
custom2 = pysqldf(q)

pysqldf = lambda q: sqldf(q, globals())
q = """
    SELECT location, schedule_name, eid, sum(total_time) as total_time,
    "Total Earning" as Total_Earning
    FROM custom, payroll
    WHERE eid = code
    GROUP BY location,eid
"""
custom = pysqldf(q)

# q = """
#     SELECT location, schedule_name, eid, sum(total_time) as total_time, Total_Earning, Hours
#     FROM custom, deducted_breaks
#     where eid = eid2
#     GROUP BY location, eid
#     ORDER BY eid;
# """
# custom = pysqldf(q)

# st.write(custom)

q = """
    SELECT location, schedule_name, sum(total_time) as total_time, SUM(Total_Earning) as Total_Earning
    FROM custom
    GROUP BY location,schedule_name
"""
custom = pysqldf(q)

custom2 = custom

q = """
    SELECT location, sum(total_time) as total_time, SUM(Total_Earning) as Total_Earning
    FROM custom
    GROUP BY location
"""
custom = pysqldf(q)

st.header("Staff Cost by Location")
st.write(custom)

download_button_str = download_button(custom, f"Staff Cost by Location.csv", 'Download CSV', pickle_it=False)
st.markdown(download_button_str, unsafe_allow_html=True)

custom2.replace("Labtech",'Lab Tech',inplace=True)

q = """
    SELECT schedule_name, sum(total_time) as total_time, SUM(Total_Earning) as Total_Earning
    FROM custom2
    GROUP BY schedule_name
"""
custom2 = pysqldf(q)

st.header("Staff Cost by Cadre")
st.write(custom2)

download_button_str = download_button(custom2, f"Staff Cost by Cadre.csv", 'Download CSV', pickle_it=False)
st.markdown(download_button_str, unsafe_allow_html=True)
