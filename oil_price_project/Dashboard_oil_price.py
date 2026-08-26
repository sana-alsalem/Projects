import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Reading the CSV file to DataFrame 
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'oil_price.csv')

oil_df = pd.read_csv(csv_path)
# Renaming Columns
oil_df.rename(columns={
    'دولار أمريكي للبرميل': 'US Dollars per Barrel',
    'النفط': 'Oil Type',
    'السنة': 'Year'
}, inplace=True)

oil_df.drop(columns=['فئة السعر'], inplace=True)
Oil_Types = {'النفط العربي الخفيف': 'Arab Light', 
             'بحر الشمال (برنت)': 'North Sea (Brent)', 
             'سلة أوبك': 'OPEC Basket'}
oil_df['Oil Type'] = oil_df['Oil Type'].replace(Oil_Types)
oil_df = oil_df.sort_values(['Year', 'Oil Type']).reset_index(drop=True)
oil_df['Difference'] = oil_df.groupby('Oil Type')['US Dollars per Barrel'].diff()
oil_df['Price_Change_Direction'] = np.where(oil_df['Difference'] > 0, 'Increased', 'Decreased')
oil_df['Price_Change_Percentage'] = oil_df.groupby('Oil Type')['US Dollars per Barrel'].pct_change() * 100


# Dashboard
st.set_page_config(layout="wide")
st.title("*Oil Prices per Barrel in USD (1970-2020)*")
st.markdown(
    """
    <p style="font-family: Arial, sans-serif; font-size: 20px; color: var(--text-color); line-height: 1.5;">
        This dashboard provides an overview of a dataset of Three Types of Oil prices per Barrel in USD from 1970 to 2020. 
        The series exhibits a stochastic (random walk) process, meaning future price changes cannot be reliably predicted from past trends. 
        You can explore the data by selecting a specific oil type to see the trends in prices, the price change direction, and the price change rate.
    </p>
    """,
    unsafe_allow_html=True,
)
container = st.container(border=True, width="content")
container.markdown(
    "<p style='font-family: Arial, sans-serif; font-size: 18px; color: var(--text-color); line-height: 1.5;'>"
    "Created by Data Scientist : <b>Sana'a Salem </b> "
    #"<a href='https://www.linkedin.com/in/sana-aloufi' target='_blank' style='color: var(--primary-color);'>LinkedIn</a>"
    "</p>",
    unsafe_allow_html=True,
)
Historical_Event = [
    {"year": 1971, "name": "U.S. spare capacity exhausted", "color": "#8B4513"},                   # Saddle Brown
    {"year": 1973, "name": "Arab Oil Embargo", "color": "#D9534F"},                                # Crimson / Coral
    {"year": 1978, "name": "Iranian Revolution", "color": "#E67E22"},                              # Pumpkin Orange
    {"year": 1980, "name": "Iran-Iraq War", "color": "#C0392B"},                                   # Dark Red
    {"year": 1986, "name": "Saudis abandon swing producer role", "color": "#16A085"},             # Teal Green
    {"year": 1990, "name": "Iraq invades Kuwait", "color": "#8E44AD"},                              # Dark Purple
    {"year": 1997, "name": "Asian financial crisis", "color": "#2980B9"},                          # Strong Blue
    {"year": 1999, "name": "OPEC cuts production targets by 1.7M barrels a day", "color": "#27AE60"},  # Emerald Green
    {"year": 2001, "name": "9/11 attacks", "color": "#7F8C8D"},                                    # Cool Gray
    {"year": 2005, "name": "Low spare capacity", "color": "#D35400"},                              # Burnt Orange
    {"year": 2008, "name": "Global financial collapse", "color": "#1B4F72"},                       # Deep Navy Blue
    {"year": 2008, "name": "OPEC cuts production targets by 4.2M barrels a day", "color": "#2196F3"},  # Bright Sky Blue
    {"year": 2015, "name": "OPEC production quota unchanged despite low oil prices", "color": "#009688"}, # Deep Teal
    {"year": 2020, "name": "Global pandemic reduces oil demand", "color": "#9C27B0"},                # Bright Purple
    {"year": 2022, "name": "Russia invades Ukraine", "color": "#FF5722"}                           # Orange Red
]
st.markdown('<p style="color: #4CAF50; font-size: 18px; font-weight: bold;">Select Oil Type :</p>', unsafe_allow_html=True)
oils = st.multiselect('Select Oil Type :', oil_df['Oil Type'].unique(), default='Arab Light', label_visibility="collapsed")

chosen_oil = oil_df[oil_df['Oil Type'].isin(oils)]
# Plotting Trend with line plot after Filtering
st.subheader(f"Prices Trend per Barrel in (USD) for {oils}")

fig_trend = px.line(
    chosen_oil,
    x="Year",
    y="US Dollars per Barrel",
    color="Oil Type",
    markers=True,
    title="Prices Trend per Barrel in (USD)",
)

# 2. Add solid arrow lines in side legend
for event in Historical_Event:
    fig_trend.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            name=event["name"],
            line=dict(color=event["color"], width=2),
            showlegend=True,
            legendgroup="events",
            legendgrouptitle_text="Historical Events",
        )
    )

# 3. Add clean arrow annotations without text boxes
for idx, event in enumerate(Historical_Event):
    year = event["year"]
    event_name = event["name"]
    event_color = event["color"]

    matching_data = chosen_oil[chosen_oil["Year"] == year]

    if not matching_data.empty:
        y_val = matching_data["US Dollars per Barrel"].values[0]

        # Alternating arrow height to prevent overlapping
        y_offset = -50 if idx % 2 == 0 else -90

        fig_trend.add_annotation(
            x=year,
            y=y_val,
            text=f"<b>{year}</b><br>{event_name}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.8,
            arrowcolor=event_color,
            ax=0,
            ay=y_offset,
            font=dict(size=10, color="#222222"),
            align="center",
            # --- REMOVE BOXES & BACKGROUND HERE ---
            borderwidth=0,  # Removes the box border completely
            borderpad=0,  # Removes padding inside the box
            bgcolor="rgba(0,0,0,0)",  # Makes background transparent
        )

# 4. Layout formatting
fig_trend.update_layout(
    plot_bgcolor="white",
    hovermode="x unified",
    margin=dict(t=80, b=40, l=40, r=40),
)

st.plotly_chart(fig_trend, use_container_width=True)

st.subheader(f"Price Change Direction per Barrel in (USD) for {oils}")
fig_diff = px.bar(chosen_oil, x='Year', y='Difference', color='Oil Type')

st.plotly_chart(fig_diff, use_container_width=True)
st.subheader(f"Year-Over-Year Percent Change in {oils} Prices (1970–2020)")
fig_pct = px.line(
        chosen_oil,
        x="Year",
        y="Price_Change_Percentage",
        color="Oil Type",
        markers=True,
    )
st.plotly_chart(fig_pct, use_container_width=True)
