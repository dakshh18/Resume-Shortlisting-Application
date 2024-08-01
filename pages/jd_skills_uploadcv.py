from apps import navigation
from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import dash
import base64
import requests

# Register page
dash.register_page(__name__, path='/jd_skills', title="Short Listing App", description="summary", image="assets/logo.png")

########### Text content #############
text_content = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H1(html.B("Resume Shortlisting Application", className="text-black")),
            html.Br(),
            html.Br(),
        ], width=6, className="text-center mx-auto")
    ], className="justify-content-center")
])

################ Step 1: Job Description ###############
step_1_jd = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3(html.B("Step-1: Upload Your Job Description Here", className="text-black")),
        ], width={"size": 6, "offset": 3}, className="text-center my-4")
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Textarea(
                id="jd",
                placeholder="Write Your Job Description Here...",
                style={
                    "height": "200px",
                    "width": "100%",
                    "padding": "12px 20px",
                    "box-sizing": "border-box",
                    "border": "2px solid #ccc",
                    "border-radius": "4px",
                    "background-color": "#f8f8f8",
                    "resize": "none",
                }
            ),
        ], width={"size": 6, "offset": 3})
    ])
])

####### Step 2: Skills ############
step_2_skills = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H3(html.B("Step-2: Write Skills You Want to Look Out for", className="text-black")),
        ], width={"size": 6, "offset": 3}, className="text-center my-4")
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Textarea(
                id="skills",
                placeholder="Skills ...",
                style={
                    "height": "200px",
                    "width": "100%",
                    "padding": "12px 20px",
                    "box-sizing": "border-box",
                    "border": "2px solid #ccc",
                    "border-radius": "4px",
                    "background-color": "#f8f8f8",
                    "resize": "none",
                },
            ),
            html.Br(),
            html.Br(),
        ], width={"size": 6, "offset": 3})
    ])
])


####### step3 ######
text_content2 = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.H2(html.B("Please upload your job description and required skills before uploading the candidate's resume.", className="text-black")),
        ], className="text-center ")
    ])
])
######## upload resume ########
cv_uploader = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            html.Br(),
            html.H3(html.B("Step-3: Upload Resume", className="text-black"))
        ], className="text-center")
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H5("Get these resume Shortlisted", className="card-title"),
                    html.P("You can upload up to 10 resumes."),
                    dcc.Upload(
                        id="upload-pdf",
                        children=[
                            'Drag and Drop or ',
                            html.A('Select a Resume File')
                        ],
                        multiple=True,
                        accept=".pdf",
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center'
                        }
                    ),
                    html.Div(id='upload-message', style={
                        "list-style-position": "inside",
                        "height": "200px", 
                        "overflow": "auto", # Enable scrolling if content overflows
                        "margin-top": "10px" 
                    })
                ]),
                style={"height": "400px"}
            )
        ])
    ])
])

####### process button ######

process_button = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Button("Process",id="process-button",color="primary",
                       style={
                           "border":"none",
                           "border-radius":"12px",
                           "padding":"15px 45px",
                           "font-size":"23px",
                           "text-align":"center",
                           "display":"inline-block"
                       })
        ],width={"size":6,"offset":3},className="text-center my-4")
    ])
])


###### table ######
table_header = [
    html.Thead(html.Tr([
                        html.Th("Name"),
                        html.Th("Resume"),
                        html.Th("Shortlisted"),
                        html.Th("Match"),
                        html.Th("Highlights"),
                        html.Th("Risks")
                        ]))
]

table_body = html.Tbody(id='resume-table-body')

table = dbc.Table(table_header + [table_body], bordered=True)

################## Loading spinner ###################
loading_wrapper = dcc.Loading(
    id="loading-wrapper",
    type="default",
    children=table,
)

############################ Layout##########################
layout = html.Div([
    navigation.navbar,
    text_content,
    step_1_jd,
    step_2_skills,
    text_content2 , cv_uploader , process_button ,loading_wrapper
   
  
], style={
    'position': 'absolute',
    'top': 0,
    'left': 0,
    'width': '100%',
    'height': '100%',
    'overflow': 'auto',
    'background-image': 'url("assets/aaron-burden-CKlHKtCJZKk-unsplash.jpg")',
    'background-repeat': 'no-repeat',
    'background-position': 'right top',
    'background-size': 'cover',
})

####################################################################### api integration  ###################################################################
# Callback to handle file upload and update messages and table rows
@dash.callback(
    Output('upload-message', 'children'),
    [Input('upload-pdf', 'filename')]
)
def update_upload_message(filenames):
    if filenames:
        return html.Div([
            html.P(f"Uploaded {len(filenames)} file(s):"),
            html.Ul([html.Li(filename) for filename in filenames])
        ])
    return ""
# call back to handle process text api and link generation 
@dash.callback(
    Output('resume-table-body', 'children'),
    [Input('process-button', 'n_clicks')],
    [State('jd', 'value'),
     State('skills', 'value'),
     State('upload-pdf', 'filename'),
     State('upload-pdf', 'contents')]
)
def process_files(n_clicks, jd, skills, filenames, contents):
    if n_clicks is None:
        return []

    files = []
    if filenames and contents:
        for filename, content in zip(filenames, contents):
            # Decode the uploaded file content
            content_type, content_string = content.split(',')
            file_content = base64.b64decode(content_string)
            files.append(('files', (filename, file_content, 'application/pdf')))

    # Preparing the data for POST request
    data = {
        'job_description': jd,
        'skills': skills
    }
    response = requests.post('http://localhost:8000/process_text', data=data, files=files)

    if response.status_code == 200:
        # Extract data from JSON response
        response_json = response.json()
        result = response_json.get("result", "")

        # Split the result by "- Candidate's name:" to handle multiple candidates
        candidates = result.split("- Candidate's name:")
        table_rows = []

        # Generate resume links
        resume_links = [f"http://localhost:8000/files/{filename}" for filename in filenames]

       
        for candidate_index, candidate in enumerate(candidates[1:]):
            lines = candidate.strip().split('\n')
            candidate_name = lines[0].strip()
            percentage_score = lines[1].split(": ", 1)[1]
            based_on_percentage = lines[2].split(": ", 1)[1]
            important_things = lines[3].split(": ", 1)[1]
            risk_factor = lines[4].split(": ", 1)[1]

            if candidate_index < len(resume_links):
                resume_link = html.A(filenames[candidate_index], href=resume_links[candidate_index], target="_blank")
            else:
                resume_link = "No resume link available"

            # Create table row
            row = html.Tr([
                html.Td(candidate_name),
                html.Td(resume_link),
                html.Td(based_on_percentage),
                html.Td(percentage_score),
                html.Td(important_things),
                html.Td(risk_factor)
            ])
            table_rows.append(row)

        return table_rows

    else:
        return f"Error: {response.status_code} - {response.text}", []
