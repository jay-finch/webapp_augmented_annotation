import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from PIL import Image

# connect to main app.py file
from app import app
from app import server

# connect apps pages
from apps import dashboard, sme_annotation


logo = Image.open('assets/PD Color.png')

# Include the DM Sans font from Google Fonts in the external_stylesheets
app.css.append_css({
    "external_url": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap"
})

#the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#000000",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "21rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [   
        html.Img(src=logo, height='25px', style={'margin-bottom':'5rem'}),
        html.H1("COURSE COMPETENCY PROTOTYPE", style={'font-family':'Roboto Mono', 'color':'#F0F0F0', 'margin-bottom':0}),
        html.Hr(),
        html.P(
            "Augmented annotation and simple dashboard demo", className="lead",
            style={'font-family':'Lato', 'color':'#F0F0F0'}),
        dbc.Nav(
            [
                dbc.NavLink("Augmented Annotation", href="/augmented-annotation", id="sme_annotation_link"),
                dbc.NavLink("Dashboard", href="/dashboard", id="dashboard_link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=sme_annotation.layout, style=CONTENT_STYLE)

app.layout = html.Div(
    style={
        "fontFamily": "DM Sans, sans-serif !important"
    },
    children=[
        dcc.Location(id="url", children='/augmented-annotation'),
        sidebar,
        content
    ]
)
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard.layout
    if pathname == '/augmented-annotation':
        return sme_annotation.layout
    else:
        return sme_annotation.layout


if __name__ == '__main__':
    app.run_server(debug=True)