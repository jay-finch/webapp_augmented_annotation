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
competency_matrix = pd.read_csv(DATA_PATH.joinpath('competency_correlation.csv'))
course_data.columns = course_data.columns.str.lower()
starting_annotation_value = ['No annotations submitted']
course_data['user_annotations']= [starting_annotation_value for i in course_data.index]
# regex = re.compile('[^a-zA-Z ]')
# competency_list = [regex.sub('', competency).strip() for competency in competency_matrix.columns[1:]]
competency_list = [competency for competency in competency_matrix.columns[1:]]


# create reference dictionary and load to json
reference_dict = {
    'current_course_location': 0,
    'course_data': course_data.to_dict(),
    'competency_list': competency_list,
    'course_layout': 1
    }
reference_json1 = json.dumps(reference_dict)

# build course layout template
def course_layout_build(reference_json1):
    # load and upack json object
    reference_dict = json.loads(reference_json1) 
    current_course_location = reference_dict.get('current_course_location')
    course_data = pd.DataFrame(reference_dict.get('course_data'))
    competency_list = reference_dict.get('competency_list')
    course_list = course_data['course title'].to_list()

    # predefined labels for current view of current course
    current_course = course_data.iloc[current_course_location]
    course_code = current_course['course_code']
    course_title = current_course['course title']
    course_description = current_course['description']
    course_category = current_course['curriculum_category']
    tag_rows = [row for row in current_course.index if 'competency' in row and 'score' not in row]
    suggested_annotations = [current_course.loc[row] for row in tag_rows]
    course_data.to_csv('clb-course_data_test.csv')
    current_course.to_csv('clb-current_course_test.csv')
    print('\nSuggested Annotations:\n',suggested_annotations)
    print('\nUser Annotations:\n',current_course.user_annotations)
    prefilled_multiselect_values = current_course.user_annotations
    print('\nPrefilled Multiselect Values:\n', prefilled_multiselect_values)
    if 'No annotations submitted' in prefilled_multiselect_values:
        prefilled_multiselect_values = suggested_annotations


    # apply reference data to the layout template
    course_template_layout = html.Div([

        # search bar and button
        html.Div([
            dcc.Dropdown(
                id='searchbar', 
                options=[{'label': course_title , 'value': course_title} for course_title in course_list],
                placeholder='Search by Course Title ...',
                style={'height':'25px',},
                ),
            ], 
            style={'width':'50%', 'display':'inline-block'}),
        html.Button('Go',id='search_button', className='btn btn-primary', n_clicks=0, style={'width': '10%', 'height':'37px', 'vertical-align':'top', 'margin-left':'1em'}),

        html.Button('Annotations', id='toggle', n_clicks=0,
            className='btn btn-outline-primary',
            style={ 
                'height':'37px', 
                'vertical-align':'top', 
                'margin-left':'1em',
                'float':'right',
                }),

        # course code, title, description, and title
        html.H4(id='course_category | course_code', children=f'{course_category} | {course_code}',style={'margin-top':'2em'}),
        html.H1(id='course_title', children=course_title.upper()),
        html.H6('COURSE DESCRIPTION'),
        html.P(id='course_description', children=course_description, style={'margin-bottom':'4em'}),
        html.H6('SUGGESTED COMPETENCY ANNOTATIONS', className='mt-6'),
        
        # annotation view and buttons
        dcc.Dropdown(
            id='multiselect',
            options=[{'label': competency, 'value': competency} for competency in competency_list],
            value=prefilled_multiselect_values,
            placeholder='Select Competency Annotations',
            multi=True),
        html.Div([
            html.Button('Refresh Suggested Competencies', id='refresh_button', className='btn btn-outline-primary mt-3 mr-3', n_clicks=0),
            html.Button('ANNOTATE', id='annotate_button', n_clicks=0, className='btn btn-annotate mt-3', ),
        ])
    ])

    return course_template_layout

def course_list_layout(reference_json):
    reference_dict = json.loads(reference_json) 
    current_course_location = reference_dict.get('current_course_location')
    course_data = pd.DataFrame(reference_dict.get('course_data'))
    competency_list = reference_dict.get('competency_list')
    course_list = course_data['course title'].to_list()

    print('\n\nToggled. Third printing: \nUpdated Reference JSON:\n',reference_dict['course_data']['user_annotations'].items())

    course_data.to_csv('cll-broken-course_data_test.csv')
    
    # filter the dataframe to only show annotated course
    # create a string column to filter on
    course_data['user_annotations_string'] = course_data['user_annotations'].apply(lambda x: ', '.join(x))
    annotated_course_list = course_data[~course_data['user_annotations_string'].str.contains('No annotations submitted')] 

    layout_df = pd.DataFrame({
        'COURSE CODE': annotated_course_list['course_code'],
        'COURSE TITLE': annotated_course_list['course title'], 
        'SUBMITTED ANNOTATIONS': annotated_course_list['user_annotations_string'],
    })

    print(layout_df)

    course_list_layout = html.Div([
        
        # Button
        html.Div([html.Button('Courses', id='toggle', n_clicks=0, className='btn btn-outline-primary mt-3 mr-3',
        style={
            'height':'37px', 
            'vertical-align':'top', 
            'margin-left':'1em',
            'float':'right',
        })],style={'width':'100%'}),
        
        # Title
        html.H1('SUBMITTED ANNOTATIONS', style={'margin-top':'75px', 
        'clear':'both'}),

        dbc.Table.from_dataframe(layout_df, striped=True, bordered=True, hover=True, style={}),


        # hidden dash components not used in this view
        dcc.Dropdown(
            id='searchbar', 
            options=[{'label': course_title , 'value': course_title} for course_title in course_list],
            placeholder='Search by Course Title ...',
            style={'display':'none'},), 
        html.Button('Go',id='search_button', n_clicks=0, style={'display':'none'}),
        dcc.Dropdown(
            id='multiselect',
            options=[{'label': competency, 'value': competency} for competency in competency_list],
            placeholder='Select Competency Annotations',
            multi=True,
            style={'display':'none'},),
        html.Button('Annotate', id='annotate_button', n_clicks=0, style={'display':'none'}),
            
        ])
    
    return course_list_layout


# main layout
layout = html.Div([
    html.Div(id='layout_container', children=course_layout_build(reference_json1)), 
    html.P(id='data_div', children=reference_json1, style={'display':'none'}),  
    ])


# callbacks
# reference button callback
@app.callback(Output('multiselect', 'value'),
              [Input('refresh_button', 'n_clicks')],
              [State('data_div','children')])
def refresh_suggested_annotations(n_clicks,children):
    # load and upack json object
    reference_dict = json.loads(children)
    current_course_location = reference_dict.get('current_course_location')
    course_data = pd.DataFrame(reference_dict.get('course_data'))
    current_course = course_data.iloc[current_course_location]
    tag_rows = [row for row in current_course.index if 'competency' in row and 'score' not in row]
    suggested_annotations = [current_course.loc[row] for row in tag_rows]
    if n_clicks < 1:
        raise PreventUpdate
    else:
        print('N_clicks', n_clicks)
        print(type(n_clicks))
        return suggested_annotations


@app.callback(Output('data_div', 'children'),
            [Input('search_button', 'n_clicks'),
            Input('annotate_button', 'n_clicks'),
            Input('toggle', 'n_clicks')],
            [State('data_div','children'),
            State('searchbar','value'),
            State('multiselect', 'value')])
def update_data_div(search_button, annotate_button, toggle, children, searchbar_value, annotation_value):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # load and unpack
    reference_dict = json.loads(children)
    current_course_location = reference_dict.get('current_course_location')
    course_data = pd.DataFrame(reference_dict.get('course_data'))
    course_list = course_data['course title'].to_list()

    if 'search_button' in changed_id:
        print('\n\n******New Search******')
        new_current_course_location = course_list.index(searchbar_value)
        reference_dict['current_course_location'] = new_current_course_location
        updated_reference_json = json.dumps(reference_dict)
        return updated_reference_json

    elif 'annotate_button' in changed_id:
        print('\n\n******New Annotation******')
        new_course_data_dict = course_data.to_dict()
        new_course_data_dict['user_annotations'][str(current_course_location)] = annotation_value
        reference_dict['course_data'] = new_course_data_dict
        print(reference_dict['course_data']['user_annotations'][str(current_course_location)])
        reference_dict['current_course_location'] = current_course_location + 1
        updated_reference_json = json.dumps(reference_dict)
        return updated_reference_json

    elif 'toggle' in changed_id:
        print('toggling...')
        reference_dict['course_layout'] *= -1 
        updated_reference_json = json.dumps(reference_dict)
        return updated_reference_json

    else: 
        return children


@app.callback(Output('layout_container','children'),
             [Input('data_div','children')])
def update_layout(children):
    reference_dict = json.loads(children)
    print('\n\nUpdated Reference JSON:\n',reference_dict['course_data']['user_annotations'].items())
    if reference_dict['course_layout'] < 0:
        print('\n\nToggled. Second printing: \nUpdated Reference JSON:\n',reference_dict['course_data']['user_annotations'].items())
        return course_list_layout(children)
    else:
        return course_layout_build(children)