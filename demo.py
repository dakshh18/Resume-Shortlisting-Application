import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests
import base64

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Resume Shortlisting Application"),
    
    # Job Description Textarea
    html.Label('Job Description'),
    dcc.Textarea(
        id='job-description',
        placeholder='Copy and paste job description here...',
        style={'width': '100%', 'height': 100},
        value=''  # Initial value can be set if needed
    ),
    
    # Skills Textarea
    html.Label('Skills'),
    dcc.Textarea(
        id='skills',
        placeholder='Enter skills separated by commas...',
        style={'width': '100%', 'height': 100, 'margin-top': '10px'},
        value=''  # Initial value can be set if needed
    ),
    
    # Upload PDFs
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select PDF Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px 0'
        },
        multiple=True
    ),
    
    # Submit Button
    html.Button('Submit', id='submit-button', n_clicks=0, style={'margin-top': '10px'}),
    
    # Table to display results
    html.Div(id='table-container', style={'margin-top': '20px'})
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return {
        'filename': filename,
        'content': decoded
    }

@app.callback(
    Output('table-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('job-description', 'value'),
     State('skills', 'value'),
     State('upload-data', 'contents'),
     State('upload-data', 'filename')]
)
def update_table(n_clicks, job_description, skills, upload_contents, upload_filenames):
    if n_clicks > 0:
        # Prepare files for API request
        files = []
        if upload_contents and upload_filenames:
            files = [parse_contents(contents, filename) for contents, filename in zip(upload_contents, upload_filenames)]
        
        files_data = [
            ('files', (file['filename'], file['content'], 'application/pdf'))
            for file in files
        ]

        # Prepare data for API request
        data = {
            'job_description': job_description,
            'skills': skills
        }

        try:
            # Make a POST request to the FastAPI endpoint
            response = requests.post("http://127.0.0.1:8000/process_text", data=data, files=files_data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Debug: Print the response for inspection
            print(response.json())

            # Extract and format the result
            results = response.json().get('result', [])
            if not isinstance(results, list):
                results = []

            result_table = html.Table([
                html.Thead(html.Tr([html.Th("Candidate's Name"), html.Th("Percentage Matching Score")])),
                html.Tbody([
                    html.Tr([
                        html.Td(candidate['name']), 
                        html.Td(f"{candidate['percentage_matching_score']}%")
                    ]) for candidate in results
                ])
            ])
            
            return result_table
        
        except requests.exceptions.RequestException as e:
            return html.Div(f"Error: {e}")

    return None

if __name__ == '__main__':
    app.run_server(debug=True)
