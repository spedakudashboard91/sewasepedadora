# -*- coding: utf-8 -*-
"""DashboardFixRevision3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Rultb_euMON0G15K7aFnBjXnXgrpZRnw
"""

# Libraries Used
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime
import streamlit as st

# Load the dataset
day_df = pd.read_csv("https://raw.githubusercontent.com/spedakudashboard91/biiike/main/data/day_dataset_bike_sharing.csv")

# Data Preprocessing
if 'instant' in day_df.columns:
    day_df.drop(columns=['instant'], inplace=True)

day_df['dteday'] = pd.to_datetime(day_df['dteday'])

day_df['weekday'] = day_df['dteday'].dt.day_name()
day_df['year'] = day_df['dteday'].dt.year

day_df['season'] = day_df['season'].map({
    1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
})

day_df['weathersit'] = day_df['weathersit'].map({
    1: 'Clear/Partly Cloudy',
    2: 'Misty/Cloudy',
    3: 'Light Snow/Rain',
    4: 'Severe Weather'
})

# Monthly Rental Data
monthly_rent_df = day_df.resample(rule='M', on='dteday').agg({
    "casual": "sum",
    "registered": "sum",
    "cnt": "sum"
})

monthly_rent_df.index = monthly_rent_df.index.strftime('%b-%y')
monthly_rent_df = monthly_rent_df.reset_index()

monthly_rent_df.rename(columns={
    "dteday": "yearmonth",
    "cnt": "total_rides",
    "casual": "casual_rides",
    "registered": "registered_rides"
}, inplace=True)

# Aggregated Data
day_df['month'] = pd.to_datetime(day_df['dteday']).dt.month
aggregated_stats_by_month = day_df.groupby('month')['cnt'].agg(['max', 'min', 'mean', 'sum'])
aggregated_stats_by_weather = day_df.groupby('weathersit')['cnt'].agg(['max', 'min', 'mean', 'sum'])
aggregated_stats_by_holiday = day_df.groupby('holiday')['cnt'].agg(['max', 'min', 'mean', 'sum'])
aggregated_stats_by_weekday = day_df.groupby('weekday')['cnt'].agg(['max', 'min', 'mean'])
aggregated_stats_by_season = day_df.groupby('season').agg({
    'casual': 'mean',
    'registered': 'mean',
    'cnt': ['max', 'min', 'mean']
})

# Streamlit App
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

st.title("Welcome to the Bike Sharing Dashboard")
st.markdown("""
### Insight:
- **Pertanyaan Bisnis ke 1**: Bagaimana perkembangan jumlah penyewaan sepeda dari tahun ke tahun?
- **Pertanyaan Bisnis ke 2**: Sejauh mana faktor cuaca berpengaruh terhadap tingkat penggunaan sepeda oleh pengguna?
- **Pertanyaan Bisnis ke 3**: Apa perbedaan pola penggunaan sepeda pada hari kerja, hari libur, dan hari biasa?
- **Pertanyaan Bisnis ke 4**: Apakah terdapat hubungan antara suhu udara dan tingkat penyewaan sepeda yang tinggi?
""")

# Metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_all_rides = day_df['cnt'].sum()
    st.metric("Total Rides", value=total_all_rides)

with col2:
    total_casual_rides = day_df['casual'].sum()
    st.metric("Total Casual Rides", value=total_casual_rides)

with col3:
    total_registered_rides = day_df['registered'].sum()
    st.metric("Total Registered Rides", value=total_registered_rides)

st.markdown("---")

# Sidebar for Filtering
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input('Mulai dari', pd.to_datetime(day_df['dteday']).min())
end_date = st.sidebar.date_input('Sampai dengan', pd.to_datetime(day_df['dteday']).max())

filtered_data = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & (day_df['dteday'] <= pd.to_datetime(end_date))]

# Line Chart for Monthly Rentals
st.subheader("Monthly Bike Rentals Over Time")
fig_monthly = px.line(monthly_rent_df, x='yearmonth', y=['casual_rides', 'registered_rides', 'total_rides'],
                      title='Monthly Bike Rentals',
                      labels={'value': 'Number of Rides', 'yearmonth': 'Month-Year', 'variable': 'Ride Type'})
st.plotly_chart(fig_monthly, use_container_width=True)
# Bar Plot for Rentals by Weather
st.subheader("Total Bike Rentals by Weather Type")

# Use Plotly Express for interactive bar plot
fig_weather = px.bar(aggregated_stats_by_weather.reset_index(),
                     x='weathersit',
                     y='sum',
                     labels={'sum': 'Total Rentals', 'weathersit': 'Weather Situation'},
                     title='Total Bike Rentals by Weather Type',
                     color='weathersit',
                     color_discrete_sequence=px.colors.qualitative.Pastel)

fig_weather.update_xaxes(type='category') # Ensure x-axis is treated as categorical
st.plotly_chart(fig_weather, use_container_width=True)

# Box Plots for Working Day, Holiday, and Weekday
st.subheader("Bike Rental Distribution")
col1, col2, col3 = st.columns(3)

with col1:
    fig1 = px.box(filtered_data, x='workingday', y='cnt', color='workingday',
                  title='By Working Day',
                  labels={'workingday': 'Working Day', 'cnt': 'Total Rentals'},
                  color_discrete_sequence=['#00FFFF', '#FF00FF'])
    fig1.update_xaxes(type='category')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.box(filtered_data, x='holiday', y='cnt', color='holiday',
                  title='By Holiday',
                  labels={'holiday': 'Holiday', 'cnt': 'Total Rentals'},
                  color_discrete_sequence=['#FFFF00', '#00FF00'])
    fig2.update_xaxes(type='category')
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    fig3 = px.box(filtered_data, x='weekday', y='cnt', color='weekday',
                  title='By Weekday',
                  labels={'weekday': 'Weekday', 'cnt': 'Total Rentals'},
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_xaxes(type='category')
    st.plotly_chart(fig3, use_container_width=True)

# Bar Plot for Rentals by Season
st.subheader("Bike Rental Counts by Season")
seasonal_usage = filtered_data.groupby('season')[['registered', 'casual']].sum().reset_index()
fig_season = px.bar(seasonal_usage, x='season', y=['registered', 'casual'],
                    title='Bike Rental Counts by Season',
                    labels={'season': 'Season', 'value': 'Total Rentals', 'variable': 'User Type'},
                    color_discrete_sequence=["#00FF00", "#0000FF"], barmode='group')
st.plotly_chart(fig_season, use_container_width=True)

st.caption('Copyright (c), created by Dora Leonny Giselle')