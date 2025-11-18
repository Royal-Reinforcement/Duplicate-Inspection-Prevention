import streamlit as st
import pandas as pd

APP_NAME = 'Duplicate Inspection Prevention'

st.set_page_config(page_title=APP_NAME, page_icon='🕵🏻‍♂️', layout='wide')

st.image(st.secrets['images']["rr_logo"], width=100)

st.title(APP_NAME)
st.info('Check for duplicate inspections to avoid redundancy.')

file = st.file_uploader('breezeway-task-custom-export.csv', type=['csv'])

if file:
    def determine_inspection(row):
        for inspection in st.secrets['inspections']['all']:
            if inspection in row['Task title']:
                return inspection


    df = pd.read_csv(file)
    df = df.drop(columns=['Status','Export status','Property Time Zone'])

    df = df[df['Reservation ID'].notna()]

    df['Inspection'] = df.apply(determine_inspection, axis=1)

    dupe_df = df[df.duplicated(subset=['Inspection','Reservation ID'], keep=False)]

    can_move_df = df[df['Inspection'].isin(st.secrets['inspections']['non_b2b'])]
    cannot_move_df = df[df['Inspection'].isin(st.secrets['inspections']['b2b'])]
    merged_df = pd.merge(can_move_df, cannot_move_df, on=['Reservation ID','Property'], suffixes=(' (nonB2B)', ' (B2B)'))
    merged_df = merged_df.drop(columns=['Inspection (nonB2B)', 'Inspection (B2B)'])
    main_columns = ['Property','Reservation ID']
    merged_df = merged_df[main_columns + [col for col in merged_df.columns if col not in main_columns]]


    if not dupe_df.empty or not merged_df.empty:
    
        st.subheader('Duplicates')

        if not dupe_df.empty:

            with st.expander('**1 : 1**'):

                st.info('The same task is scheduled for the same reservation more than once.')

                st.dataframe(dupe_df, hide_index=True)
        
        if not merged_df.empty:

            with st.expander('**B2B : nonB2B**'):

                st.info('Tasks that can be moved vs tasks that cannot be moved for the same reservation.')

                st.dataframe(merged_df, hide_index=True)
    
    else:

        st.success('No duplicate inspections found!')