from apps import navigation
from dash import html, Input, Output, dcc, no_update
import dash_bootstrap_components as dbc
import dash
import requests
import flask

# Register page
dash.register_page(__name__, path='/history', title="Past Runs", description="summary", image="assets/logo.png")

layout = html.Div([
    dcc.Location(id="history-url", refresh=True),
    navigation.navbar,
    dbc.Container([
        html.Br(),
        html.H2(html.B("Past Shortlisting Runs", className="text-black"), className="text-center my-4"),
        dcc.Loading(html.Div(id="history-content")),
    ]),
], style={
    'position': 'absolute',
    'top': 0,
    'left': 0,
    'width': '100%',
    'height': '100%',
    'overflow': 'auto',
    'background-repeat': 'no-repeat',
    'background-position': 'right top',
    'background-size': 'cover',
})

# Guard: bounce to login if there's no session token
@dash.callback(
    Output('history-url', 'pathname'),
    Input('history-url', 'pathname'),
)
def guard_history(_pathname):
    if not flask.session.get('token'):
        return '/'
    return no_update

def _results_table(results):
    header = html.Thead(html.Tr([
        html.Th("Name"), html.Th("Shortlisted"), html.Th("Match"), html.Th("Highlights"), html.Th("Risks")
    ]))
    rows = [
        html.Tr([
            html.Td(r["candidate_name"]),
            html.Td("Yes" if r["shortlisted"] else "No"),
            html.Td(f'{r["match_score"]}%'),
            html.Td(r["highlights"]),
            html.Td(r["risk_factor"]),
        ]) for r in results
    ]
    return dbc.Table([header, html.Tbody(rows)], bordered=True)

@dash.callback(
    Output('history-content', 'children'),
    Input('history-url', 'pathname'),
)
def load_history(pathname):
    if pathname != '/history':
        return no_update

    token = flask.session.get('token')
    if not token:
        return no_update

    response = requests.get('http://localhost:8000/history', headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 401:
        return dbc.Alert("Session expired. Please log in again.", color="danger")
    if response.status_code != 200:
        return dbc.Alert(f"Failed to load history: {response.status_code}", color="danger")

    runs = response.json()
    if not runs:
        return dbc.Alert("No past runs yet.", color="info")

    items = []
    for run in runs:
        items.append(dbc.AccordionItem(
            [
                html.P(html.B("Job Description")),
                html.P(run["job_description"]),
                html.P(html.B("Skills")),
                html.P(run["skills"]),
                _results_table(run["results"]),
            ],
            title=f'{run["created_at"]} — {len(run["results"])} candidate(s)',
        ))

    return dbc.Accordion(items, always_open=False)
