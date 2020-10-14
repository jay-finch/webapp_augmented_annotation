import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import pathlib
import re
import json
from app import app

# read & format data
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('../datasets').resolve()
course_data = pd.read_csv(DATA_PATH.joinpath('combined_course_data.csv'))
course_by_competency_data = pd.read_csv(DATA_PATH.joinpath('course_by_competency.csv'))
competency_matrix = pd.read_csv(DATA_PATH.joinpath('competency_correlation.csv'))
course_data.columns = course_data.columns.str.lower()
starting_annotation_value = ['No annotations submitted']
course_data['user_annotations']= [starting_annotation_value for i in course_data.index]
# regex = re.compile('[^a-zA-Z ]')
# competency_list = [regex.sub('', competency).strip() for competency in competency_matrix.columns[1:]]
competency_list = [competency for competency in competency_matrix.columns[1:]]


# cards
course_card = dbc.Card(dbc.CardBody([
    html.H1(f'{len(course_data)}'),
    html.P('TOTAL COURSES'),
]))

competency_card = dbc.Card(dbc.CardBody([
    html.H1(f'{len(competency_list)}'),
    html.P('TOTAL MOSAIC COMPETENCIES'),
]))

curriculum_card = dbc.Card(dbc.CardBody([
    html.H1(f'{len(course_data.curriculum_category.unique())}'),
    html.P('TOTAL CURRICULUM CATEGORIES'),
]))

summary_cards = dbc.CardDeck([
    course_card, competency_card, curriculum_card
])


def split(no_of_competencies, data=course_by_competency_data):
    competency_counts = course_by_competency_data['competency'].value_counts()
    competency_percentages = course_by_competency_data['competency'].value_counts(normalize=True)
    competency_pie_chart_data = pd.DataFrame({
        'Competency' : competency_counts.index.to_list(),
        'Competency Counts' : competency_counts.to_list(),
        'Competency Percentage' : competency_percentages.to_list(),
        },)
    sum_of_other_competencies = competency_pie_chart_data[no_of_competencies:]
    sum_total_row = ['Other Competencies', sum_of_other_competencies['Competency Counts'].sum(), sum_of_other_competencies['Competency Percentage'].sum()]
    dynamic_competency_pie_chart_data = competency_pie_chart_data.head(no_of_competencies+1)
    dynamic_competency_pie_chart_data = dynamic_competency_pie_chart_data.copy()
    dynamic_competency_pie_chart_data.iloc[no_of_competencies] = sum_total_row
    fig = px.pie(dynamic_competency_pie_chart_data, values='Competency Counts', names='Competency',)
    return fig

competency_pie_chart_card = dbc.Card(dbc.CardBody([
    html.H3('COMPETENCY INVENTORY'), 
    dcc.Graph(id='competency_pie_chart_card', figure=split(5)),
    dcc.Slider(id='competency_pie_chart_slider', min=3, max=15, step=1, value=5, marks={3:{'label':'3 Competencies'},15:{'label':'15 Competencies'}}),
]))

def build_table(x,combined_course_data=course_data):
    course_curriculum_count = combined_course_data.curriculum_category.value_counts().head(x).sort_values(ascending=True)
    course_curriculum_percentage = combined_course_data.curriculum_category.value_counts(normalize=True).head(x).sort_values(ascending=True)
    df = {
        'Title':course_curriculum_count.index.to_list(),
        'Count':course_curriculum_count.to_list(),
        'Percentage':course_curriculum_percentage.to_list(),
    }
    fig = px.bar(df, y='Title', x='Count', title='Curriculum Category Inventory', orientation='h', hover_name='Title', hover_data={'Count':True, 'Title':False,},)
    return fig


curriculum_chart_card = dbc.Card(dbc.CardBody([ 
    html.H3('CURRICULUM INVENTORY'), 
    dcc.Graph(id='curriculum_chart_card', figure=build_table(5)),
    dcc.Slider(id='curriculum_chart_slider', min=3, max=15, step=1, value=5, marks={3:{'label':'3 Courses'},15:{'label':'15 Courses'}}),
]))



# main layout
layout = dbc.Container([

    html.H1('MOSAIC COMPETENCY INVENTORY'),
    html.P('A summary of Mosaic competency annotations to courses', className='mt-3'),
    dbc.Row([dbc.Col([summary_cards])]),
    
    # dbc.Row([dbc.Col([competency_pie_chart_card], width=12)])
    dbc.Row(dbc.Col([competency_pie_chart_card], width=12, className='mt-3')),

    dbc.Row(dbc.Col([curriculum_chart_card], width=12, className='mt-3')),

    # dbc.Row([]),
])



@app.callback(Output('competency_pie_chart_card','figure'),
            [Input('competency_pie_chart_slider', 'value')])
def update_competency_pie_chart(value):
    updated_figure = split(value)
    return updated_figure

@app.callback(Output('curriculum_chart_card','figure'),
            [Input('curriculum_chart_slider', 'value')])
def update_competency_pie_chart(value):
    updated_figure = build_table(value)
    return updated_figure