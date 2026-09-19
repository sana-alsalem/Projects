import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import pyxlsb # Library of Reading Excel Files

# Reading CSV file
stc_df = pd.read_csv("/Users/sanaa/Desktop/Data_Science/Projects/STC/First_Task/stc_TV_Data_Set_T1.csv")
stc_df.sort_values(by='date_', ascending=True, inplace=True)
months_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
stc_df['month'] = pd.to_datetime(stc_df['date_']).dt.month
stc_df['month_name'] = stc_df['month'].map(months_names)
stc_df['year'] = pd.to_datetime(stc_df['date_']).dt.year
stc_df['program_name'] = stc_df['program_name'].str.split().str.join(' ')
stc_df['viewers'] = stc_df.groupby('original_name')['user_id_maped'].transform('nunique')
stc_df['duration_hours'] = stc_df['duration_seconds'] / 3600
st.set_page_config(layout="wide")

# Filtring Dataset 
st.title("Jawwy dataset")
st.subheader("The dataset consists of meta details about the movies and tv shows as genre. Also details about Users activities, spent duration and if watching in High definition or standard definition.")
st.subheader("Customers Behavior Overview , identify the following audience segments:")
filter_box = st.container(border=True, width='stretch', horizontal=True)
year = filter_box.radio("Select Year:", options=stc_df['year'].unique())

filtered_df = stc_df[stc_df['year'] == year]


# Studying Customers behaviours 
metrics = ["Watching Time", "Viewers", "Views"]
metric = filter_box.pills(label='Select Metric', options=metrics, default='Watching Time')
chosen_month = filter_box.selectbox("Select Month:", options=filtered_df['month_name'].unique())

if metric == "Watching Time": #Program Class Watch Time
        Watch_df = filtered_df.copy()
        month_df = Watch_df[Watch_df['month_name'] == chosen_month]

        st.subheader(f"Total Watching Hours spent by Program Class in {chosen_month} - {year} in Hours")
        class_watch_time = month_df.groupby('program_class')['duration_hours'].sum().reset_index()
        st.plotly_chart(px.pie(class_watch_time, values='duration_hours', names='program_class'))
        # 1. Filter dataset down to the chosen month first
        # Top 10 Programs by Watch Time
        
        # 2. Get top 10 programs by total duration in that month
        top10_programs = (
            month_df.groupby('program_name')['duration_hours']
            .sum()
            .nlargest(10)
            .index
        )
        # 3. Filter month_df (not full Watch_df) to only include top 10 programs
        top10_by_month = month_df[month_df["program_name"].isin(top10_programs)]
        # 4. Aggregate watch time for plotting
        top10_by_Watch = (
            top10_by_month.groupby(['month_name', 'program_name', 'program_class'])
            .agg(watch_time=('duration_hours', 'sum'))
            .reset_index()
            .sort_values(by='watch_time', ascending=False)
        )
        st.subheader(f"Top 10 Programs by Watch Time in {chosen_month} - {year}")
        st.plotly_chart(
                px.bar(
                        top10_by_Watch, x='program_name', y='watch_time', color='program_class', 
                        hover_data=['program_class'], labels={'watch_time': 'Total Watch Time (Hours)'}))
elif metric == "Viewers":
        # Viewers
        viewers_df = filtered_df.copy()
        month_df = viewers_df[viewers_df['month_name'] == chosen_month]


        st.subheader(f"Total Viewers who Watched by Program Class in {year} in Hours")
        class_total_viewers = month_df.groupby('program_class')['viewers'].sum().reset_index()
        st.plotly_chart(px.pie(class_total_viewers, values='viewers', names='program_class'))
        # Top 10 Programs by Unique Viewers
        month_df = viewers_df[viewers_df['month_name'] == chosen_month]
        # 2. Get top 10 programs by total viewers in that month
        top10_programs = (
            month_df.groupby('program_name')['viewers']
            .sum()
            .nlargest(10)
            .index
        )
        # 3. Filter month_df (not full Watch_df) to only include top 10 programs
        top10_by_month = month_df[month_df["program_name"].isin(top10_programs)]
        # 4. Aggregate watch time for plotting
        top10_by_viewers = (
            top10_by_month.groupby(['month_name', 'program_name', 'program_class'])
            .agg(total_viewers=('viewers', 'sum'))
            .reset_index()
            .sort_values(by='total_viewers', ascending=False)
        )
        st.subheader(f"Top 10 Programs are Watched by Viewers in {chosen_month} - {year}")
        st.plotly_chart(
                px.bar(
                        top10_by_viewers, x='program_name', y='total_viewers', color='program_class', 
                        hover_data=['program_class'], labels={'total_viewers': 'Total Viewers'}))

elif metric == "Views":
        # Total Views by Program Class
        views_df = filtered_df.copy()
        month_df = views_df[views_df['month_name'] == chosen_month]

        st.subheader(f"Total Number of Views by Program Class in {chosen_month} - {year}")
        class_total_views = month_df.groupby('program_class')['user_id_maped'].count().reset_index()
        st.plotly_chart(px.pie(class_total_views, values='user_id_maped', names='program_class'))
        
        top10_programs = (
            month_df.groupby('program_name')['user_id_maped']
            .count()
            .nlargest(10)
            .index
        )
        top10_by_month = month_df[month_df["program_name"].isin(top10_programs)]
        # 4. Aggregate watch time for plotting
        top10_by_views = (
            top10_by_month.groupby(['month_name', 'program_name', 'program_class'])
            .agg(views=('user_id_maped', 'count'))
            .reset_index()
            .sort_values(by='views', ascending=False)
        )
        st.subheader(f"Top 10 Programs by Views in {chosen_month} - {year}")
        st.plotly_chart(
                px.bar(
                        top10_by_views, x='program_name', y='views', color='program_class', 
                        hover_data=['program_class'], labels={'views': 'Total Views'}))
