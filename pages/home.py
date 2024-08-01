from dash import html, Input, Output, State, dcc, no_update
import dash_bootstrap_components as dbc
import dash
import requests
import flask
import time



# Register page
dash.register_page(__name__, path='/', title="Short Listing dash", description="summary", image="assets/logo.png")

# Text content
text_content = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H1(html.B(" Resume Shortlisting Application", className="text-black")),
            html.Br(),
            html.Br(),
        ], width=6, className="text-center mx-auto")
    ], className="justify-content-center")
])

# Inline CSS for card styling
card_style = {
    'width': '100%',
    'height': 'auto',
    'borderRadius': '15px',
    'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)',
}

# Login form
login_form = dbc.CardBody(
    [
        html.H2("Login", className="card-title text-center mb-4 text-black"),
        dbc.CardGroup(
            [
                dbc.Label("Email", className="sr-only fw-bold text-black"),
                dbc.Input(type="email", id="login-email", placeholder="Enter email"),
            ]
        ),
        dbc.CardGroup(
            [
                dbc.Label("Password", className="sr-only fw-bold text-black"),
                dbc.InputGroup(
                    [
                        dbc.Input(
                            type="password", id="login-password", placeholder="Enter password"
                        ),
                        dbc.InputGroupText(
                            html.I(className="bi-eye-slash", id="login-eye-icon"),
                            style={"cursor": "pointer"}
                        )
                    ]
                )
            ]
        ),
        html.Br(),
        dbc.Button("Login", color="primary", className="w-100", id="login-button"),
        html.Div(id="login-output", className="mt-4"),
        html.H6(html.B(" New User Please Signup First", className="text-black"), className="text-center"),
    ]
)

# Sign-Up form
signup_form = dbc.CardBody(
    [
        html.H2("Sign Up", className="card-title text-center mb-4 text-black"),
        dbc.CardGroup(
            [
                dbc.Label("Email", className="sr-only fw-bold text-black"),
                dbc.Input(type="email", id="signup-email", placeholder="Enter email"),
            ]
        ),
        dbc.CardGroup(
            [
                dbc.Label("Password", className="sr-only fw-bold text-black"),
                dbc.InputGroup(
                    [
                        dbc.Input(
                            type="password", id="signup-password", placeholder="Enter password",
                        ),
                        dbc.InputGroupText(
                            html.I(className="bi-eye-slash", id="signup-eye-icon"),
                            style={"cursor": "pointer"}
                        )
                    ]
                )
            ]
        ),
        html.Br(),
        dbc.Button("Sign Up", color="primary", className="w-100", id="signup-button"),
        html.Div(id="signup-output", className="mt-4"),
        html.H6(html.B("Already have an account? Please log in ", className="text-black"), className="text-center"),
    ]
)

# Single Card with Tabs for Login and Sign-Up
single_card = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [

                                html.Div(id='tabs-content'),
                                dcc.Tabs(
                                    id="tabs",
                                    value='login',
                                    children=[
                                        dcc.Tab(label='Login', value='login', className="fw-bold"),
                                        dcc.Tab(label='Sign Up', value='signup', className="fw-bold"),
                                    ],
                                    className="mb-4"
                                ),
                                # html.Div(id='tabs-content')
                            ]
                        ),
                    ],
                    style=card_style,
                    className="shadow p-4"
                ),
                width=8,
                md="auto",
                className="vh-100 align-items-center",
            ),
            justify="center",
            className="vh-100 align-items-center"
        )
    ]
)


################# layout #######################
layout = html.Div(
    [
        dcc.Location(id="url", refresh=True),
        html.Div(id="page-content"),
        html.Div(
            [
                text_content,
                single_card
            ],
            style={
                'position': 'absolute',
                'top': 0,
                'left': 0,
                'width': '100%',
                'height': '100%',
                'overflow': 'auto',
                'backgroundRepeat': 'no-repeat',
                'backgroundPosition': 'right top',
                'backgroundSize': 'cover',
            },
        ),
    ]
)

# Callback to handle tab content switching
@dash.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def tab_switching(tab):
    if tab == 'signup':
        return signup_form
    else:
        return login_form


######################################### Callback to handle signup API ###########################################
@dash.callback(
    Output("signup-output", "children"),
    Input("signup-button", "n_clicks"),
    State("signup-email", "value"),
    State("signup-password", "value"),
)
def signup(n_clicks, email, password):
    if n_clicks:
        if not email or not password:
            return dbc.Alert("Email and password are required.", color="danger")
        
        response = requests.post("http://127.0.0.1:8000/signup/", json={"email": email, "password": password})
        
        if response.status_code == 200:
            return dbc.Alert("Signup Successful", color="success")
        else:
            error_detail = response.json().get("detail")
            error_message = "Signup failed"

            if isinstance(error_detail, list) and len(error_detail) > 0:
                error_message = error_detail[0].get("msg", "Signup failed")
                if "must have exactly one @" in error_message:
                    error_message = "Invalid Email"
                elif "The part after the @-sign is not valid. It should have a period." in error_message:
                    error_message = "Invalid Email"
            elif isinstance(error_detail, str):
                error_message = error_detail

            return dbc.Alert(error_message, color="danger")
    return None

###################################### Callback to handle login API ##########################################################
@dash.callback(
    [Output("login-output", "children"), Output("url", "pathname")],
    Input("login-button", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
)
def login(n_clicks, email, password):
    if n_clicks:
        if not email or not password:
            return dbc.Alert("Email and password are required.", color="danger"), no_update

        response = requests.post("http://127.0.0.1:8000/login/", json={"email": email, "password": password})

        if response.status_code == 200:
            token = response.json().get("token")
            flask.session['token'] = token

            # dely
            # time.sleep(2) 

            return dbc.Alert("Login Successful", color="success"), "/jd_skills"
        else:
            error_detail = response.json().get("detail")
            error_message = "Login failed "

            if isinstance(error_detail, list) and len(error_detail) > 0:
                error_message = error_detail[0].get("msg", "Login failed")
                if "must have exactly one @" in error_message:
                    error_message = "Invalid Email"
                elif "The part after the @-sign is not valid. It should have a period." in error_message:
                    error_message = "Invalid Email"
            elif isinstance(error_detail, str):
                error_message = error_detail

            return dbc.Alert(error_message, color="danger"), no_update
    return None, None