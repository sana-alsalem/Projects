import pandas as pd
from dash import Dash, dcc, html
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import kagglehub
import os
path = kagglehub.dataset_download("adilshamim8/predict-calorie-expenditure")

print("Path to dataset files:", path)
folder_path = path
print(os.listdir(folder_path))
calories_df = pd.read_csv(f'{path}/train.csv')
calories_df.columns
#calculating BMI
calories_df['BMI'] = calories_df['Weight'] / ((calories_df['Height']/100) ** 2)
calories_df.head()
#Idetifing BMI Categories basod on BMI
def classify_bmi(bmi):
    if bmi <= 18.4:
        return 'Underweight'
    elif 18.5 <= bmi <= 24.9:
        return 'Healthy'
    elif 25 <= bmi <= 29.9:
        return 'Overweight'
    elif bmi >= 30:
        return 'Obese'
calories_df['BMI_Category'] = calories_df['BMI'].apply(classify_bmi)
#Age intervals
bins = list(range(20, 90, 10)) # [20, 30, 40, 50, 60, 70, 80]
labels = [f'{i}-{i+10}' for i in range(20, 80, 10)] # ['20-30', '30-40', '40-50', '50-60', '60-70', '70-80']

# Use pd.cut to create the new column 'Age_Group' based on the bins and labels.
calories_df['Age_Group'] = pd.cut(calories_df['Age'], bins=bins, labels=labels, right=False)
# Create duration bins and labels
duration_bins = [0, 10, 20, 30]
duration_labels = ['1-10', '10-20', '20-30']

# Add a new column for duration intervals
calories_df['Duration_Interval'] = pd.cut(calories_df['Duration'], bins=duration_bins, labels=duration_labels, right=False)
calories_df.head()
import plotly.graph_objects as go

def bmi_cal_fig(df, age_group):
    filtered_df = df[df['Age_Group'] == age_group]
    grouped_df = filtered_df.groupby(['Sex', 'BMI_Category'])['Calories'].mean().reset_index()

    genders = grouped_df['Sex'].unique()
    fig = go.Figure()

    for gender in genders:
        gender_data = grouped_df[grouped_df['Sex'] == gender]
        fig.add_trace(go.Pie(
            labels=gender_data['BMI_Category'],
            values=gender_data['Calories'],
            name=gender,
            hole=0.3,
            title=f'{gender}',
            domain={'x': [0, 0.5]} if gender == 'female' else {'x': [0.5, 1]}
        ))

    fig.update_layout(
        title_text=f'Avarege Calories Burned by BMI Category (Age Group: {age_group})',
        showlegend=True
    )
    return fig
def wieght_cal_fig_line(df, age_group):
    filtered_df = df[df['Age_Group'] == age_group]
    cal_weight_df = filtered_df.groupby(['Sex', 'Weight'])['Calories'].mean().reset_index()
    fig = px.line(cal_weight_df, x='Weight', y='Calories', color='Sex',
                  title=f'Average Calories Burned vs Weight (Age Group: {age_group})',
                  labels={'Weight': 'Weight (kg)', 'Calories': 'Average Calories Burned'})
    fig.update_layout(template='plotly_white')
    return fig

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def training_cal_fig(df, age_group):
    filtered_df = df[df['Age_Group'] == age_group]
    women_df = filtered_df[filtered_df['Sex'] == 'female']
    men_df = filtered_df[filtered_df['Sex'] == 'male']

    w_activity_cal = women_df.groupby('Duration')[['Calories', 'Body_Temp', 'Heart_Rate']].mean().reset_index()
    m_activity_cal = men_df.groupby('Duration')[['Calories', 'Body_Temp', 'Heart_Rate']].mean().reset_index()

    # Create subplots: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Women", "Men"),
        shared_yaxes=True
    )

    # Women scatter plot
    fig.add_trace(go.Scatter(
        x=w_activity_cal['Duration'],
        y=w_activity_cal['Calories'],
        mode='markers',
        marker=dict(
            size=12,
            color=w_activity_cal['Body_Temp'],
            colorscale='YlOrRd',
            showscale=True,
            colorbar=dict(title='Body Temp')
        ), 
        showlegend=False
    ), row=1, col=1)

    # Men scatter plot
    fig.add_trace(go.Scatter(
        x=m_activity_cal['Duration'],
        y=m_activity_cal['Calories'],
        mode='markers',
        marker=dict(
            size=12,
            color=m_activity_cal['Body_Temp'],
            colorscale='YlOrRd',
            showscale=False
            
        ), showlegend=False
    ), row=1, col=2)

    fig.update_layout(
        title_text=f'Calories Burned vs Duration for Age Group: {age_group}',
        xaxis_title='Duration (minutes)',
        yaxis_title='Average Calories Burned',
        template='plotly_white',
    )

    return fig
training_cal_fig(calories_df, '20-30')
from dash.dependencies import Input, Output
age_groups = calories_df['Age_Group'].unique()

app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.H1("Calories Expenditure Based on Factors", style={
            'textAlign': 'center',
            'color': 'black',
            'fontSize': '40px',
            'textShadow': '2px 2px 4px rgba(0,0,0,0.6)',
            'margin': '0',
            'padding': '20px 0 0 0',
            'fontFamily': 'Georgia, serif'
        }),
        html.H2("By Sana'a Aloufi", style={
            'textAlign': 'center',
            'color': 'black',
            'fontSize': '22px',
            'textShadow': '1px 1px 2px rgba(0,0,0,0.6)',
            'margin': '0',
            'padding': '0 0 30px 0',
            'fontFamily': 'Arial, sans-serif',
            'fontWeight': 'normal',
            'fontStyle': 'italic'
        })
    ], style={
        'backgroundImage': 'url("/assets/header_banner.jpg")',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'textAlign': 'center',
        'position': 'relative'
    }), 
    html.P(
        "Factors that influence calories burned include individual characteristics like age, gender, body weight, and muscle mass, "
        "as well as exercise-related variables such as the duration, intensity, and type of activity.",
         style={'textAlign': 'center', 'fontSize': 20, 'fontFamily': 'times new roman'}
    ),
    html.Label("Select a Factor and Age Group :", style={'fontSize': 20, 'marginRight': '10px', 'marginBottom': '10px'}),
    dcc.Dropdown(
        id='age_group',
        style={'width': '200px', 'marginBottom': '20px'},
        options=[{'label': str(age), 'value': str(age)} for age in age_groups],
        value=age_groups[0],
        clearable=False,
    ),
    dcc.Tabs(id='tabs_factors', value='tab_weight', children=[
        dcc.Tab(label='Weight', value='tab_weight'),
        dcc.Tab(label='BMI', value='tab_bmi'),
        dcc.Tab(label='Training Intensity', value='tab_training')]),
    html.Div(id='factor_graph')
])
@app.callback(Output('factor_graph', 'children'), 
              Input('tabs_factors', 'value'), 
              Input('age_group', 'value'))
def render_content(tab, age_group):
    if tab == 'tab_weight':
        return html.Div([
            html.H3('“Generally, the more you weigh, the more calories you’ll burn per session,” says Kyle Gonzalez, CSCS, the Los Angeles-based head of content for Momentus, a supplement company. ' \
            '\nPeople with larger bodies also tend to have larger internal organs (such as the heart, liver, kidneys, and lungs), which is a significant factor in how many calories are burned during exercise and at rest, ' \
            'because these organs and their processes require energy.', style={'textAlign': 'center', 'fontSize': 20, 'fontFamily': 'times new roman'}),
            dcc.Graph(figure=wieght_cal_fig_line(calories_df, age_group= age_group))
            ])
    elif tab == 'tab_bmi':
        return html.Div([
            html.H3('The BMI formula is determined by taking your weight in Kg and dividing that number by your height in cm , squared. The BMI calculation is: weight (Kg) / height (cm) x height (cm).' \
            'That number correlates to one of the weight categories assigned to various ranges of BMIs. There are four main categories: underweight, normal weight, overweight, and obese.'),
            dcc.Graph(figure=bmi_cal_fig(calories_df, age_group= age_group))
        ])
    elif tab == 'tab_training':
        return html.Div([
            html.H3('Higher training intensity leads to a greater calorie burn because it requires more oxygen and boosts your metabolism,' \
            'resulting in a higher rate of energy expenditure during and after the workout.'),
            dcc.Graph(figure=training_cal_fig(calories_df, age_group= age_group))
        ])
    
    # Finally Running the App

if __name__ == '__main__':
    app.run(debug=True)

    # Done By Sana'a Alharbi