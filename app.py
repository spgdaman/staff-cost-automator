import pandas as pd
import streamlit as st
from download import download_button
from pandasql import sqldf
import numpy as np

st.set_page_config(layout='wide')

with st.expander("Click me to view instruction on how to use the tool"):
    st.info("For the tool to work, 2 files are required as listed below")
    st.markdown(
        '''
 1. **Custom Payroll Report** : This should be in **excel** format, and the key columns listed below should be present and not empty for accurate results in the final output:
	 - Code 
	 - Total Earning
2. **Shifts Schedule (Custom Report)**: This should be in **csv** format, with no blanks in the ***eid*** columns.

        '''
    )

def cost_automator(custom, payroll):
    custom = pd.read_csv(custom_report)
    payroll = pd.read_excel(aruti_report)
    # deducted_breaks = pd.read_csv(deducted_breaks_report)

    payroll = payroll[['Code','Total Earning']]
    total_earning = payroll['Total Earning'].sum()
    
    # cleaning custom report data
    custom.replace("Call Center",'Support Office (Call Center)',inplace=True)
    custom.replace("Umoja Clinic",'Umoja 2',inplace=True)
    custom.replace("Labtech",'Lab Tech',inplace=True)

    # unique list of total hours worked per individual staff
    custom2 = custom.groupby(['eid'], as_index=False)['total_time'].sum()
    
    # custom2 = pd.merge(
    #         custom2,
    #         deducted_breaks,
    #         left_on='eid',
    #         right_on = 'eid',
    #         how = 'left'
    #     )

    # custom2 = custom2[['eid', 'total_time']]
    work_type = custom.groupby(['employee','eid','schedule_name','skills'], as_index=False)['total_time'].sum()
    custom = custom.groupby(['employee','eid','location','schedule_name','skills'], as_index=False)['total_time'].sum()
    
    # merge to get total hours worked per staff for apportioning cost
    custom = pd.merge(
        custom,
        custom2,
        left_on='eid',
        right_on='eid',
        how='left'
    )
    
    # merge with payroll data to apportion cost to cost center
    custom = pd.merge(
        custom,
        payroll,
        left_on='eid',
        right_on='Code',
        how='left'
    )
    
    # cost apportioning to respective mc based on hours worked
    custom3 = custom
    custom3['Total Earning'] = (custom3['total_time_x']/custom3['total_time_y']) * custom3['Total Earning']
    custom3['total_time'] = custom3['total_time_x']
    custom3 = custom3.groupby(['location'], as_index=False).agg({'total_time':'sum','Total Earning':'sum'})

    # custom['total_time'] = (custom['total_time_x']/custom['total_time_y']) * custom['Hours']
    # custom['Total_Earning'] = (custom['total_time_x']/custom['total_time_y']) * custom['Total Earning']

    # del custom['total_time_x']
    # del custom['total_time_y']
    # del custom['Hours']
    # del custom['Code']
    # del custom['Total Earning']

    st.header("Staff cost by location")
    location = custom3
    del custom3
    st.write(custom['Total Earning'].sum())
    so_cost = total_earning - location['Total Earning'].sum()
    new_row = {'location':'Support Office', 'total_time':0, 'Total Earning':so_cost}
    location = location.append(new_row, ignore_index=True)
    st.write(location)
    download_button_str = download_button(location, f"Staff Cost by Location.csv", 'Download CSV', pickle_it=False)
    st.markdown(download_button_str, unsafe_allow_html=True)

    st.header("Staff cost by cadre")
    cadre = custom.groupby(['schedule_name','skills'], as_index=False).agg({'total_time':'sum','Total Earning':'sum'})
    st.write(cadre)
    download_button_str = download_button(cadre, f"Staff Cost by Cadre.csv", 'Download CSV', pickle_it=False)
    st.markdown(download_button_str, unsafe_allow_html=True)

    st.header("Staff cost by location and cadre")
    location2 = custom.groupby(['location','schedule_name','skills'], as_index=False).agg({'total_time':'sum','Total Earning':'sum'})
    st.write(location2)
    download_button_str = download_button(location2, f"Staff Cost by Location and Cadre.csv", 'Download CSV', pickle_it=False)
    st.markdown(download_button_str, unsafe_allow_html=True)

    st.header("Staff cost by work type")
    work_type = custom.groupby(['location','schedule_name', 'eid','skills'], as_index=False).agg({'total_time':'sum','Total Earning':'sum'})
    work_type = work_type[work_type['schedule_name'] != 'Locum']
    work_type.loc[(work_type['total_time'] <= 200 ), 'Type' ] = 'Normal Hours'
    # work_type.loc[(work_type['total_time'] >200) & (work_type['schedule_name'] == 'Locum'), 'Type'] = 'Locum Hours'
    work_type.loc[(work_type['total_time'] > 200 ) & (work_type['schedule_name'] != 'Locum'), 'Type' ] = 'Overtime'
    work_type = work_type.groupby(['location','Type'], as_index=False).agg({'total_time':'sum','Total Earning':'sum'})
    st.write(work_type)
    download_button_str = download_button(work_type, f"Staff Cost by work_type.csv", 'Download CSV', pickle_it=False)
    st.markdown(download_button_str, unsafe_allow_html=True)

    del payroll
    del custom


aruti_report = st.sidebar.file_uploader("Enter the Payroll Report (Aruti Data) file as a Excel")
custom_report = st.sidebar.file_uploader("Enter the Scheduled Shifts (Custom Report) file as an CSV")
# deducted_breaks_report = st.sidebar.file_uploader("Enter the Deducted Breaks file as a CSV")

if aruti_report == None or custom_report == None :
    st.warning("Please upload all required files!")
else:
    st.success("Files uploaded successfully!")
    st.balloons()
    cost_automator(custom_report,aruti_report)