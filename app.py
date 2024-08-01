########### main app ######
import dash
import dash_bootstrap_components as dbc
from dash import html,Input,Output
import dash_uploader as du
import os


app = dash.Dash(__name__,
                use_pages=True,
                external_stylesheets=[dbc.themes.MORPH,dbc.icons.BOOTSTRAP],     
                suppress_callback_exceptions=True,
              
          
                )
                    

server = app.server
server.secret_key = '9a8fc018d7458fb54c91d745f7358ead20d3452c3d7421d647bc1f44e7168916'

UPLOAD_FOLDER_ROOT = os.path.join(os.path.dirname(__file__),"uploads")
du.configure_upload(app,UPLOAD_FOLDER_ROOT)

app.layout = html.Div(children=[
    dash.page_container
])

if __name__ =="__main__":
    app.run_server(debug = True)
    