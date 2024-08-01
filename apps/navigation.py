import dash_bootstrap_components as dbc
from dash import html,Input,Output,State


### branding logo ###

COM_LOGO = "assets/logo.png"


######### navbar #########

navbar = dbc.Navbar(
    dbc.Container(
        [
            ### row no 1 for company name and logo 


            dbc.Row([
                dbc.Col([
                    html.Img(src=COM_LOGO,height="30px"),
                    dbc.NavbarBrand("ELITEWARE SOLUTION",className="ms-2")
                ],width={"size":"auto"})
            ],
            align="center",
            className="g-0"),


            ### row no 2 for navbar items ###

            dbc.Row([
                dbc.Col([
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Account",href="/")),
                        dbc.NavItem(dbc.NavLink("Short List Resumes ",href="/jd_skills")),
                        # dbc.NavItem(dbc.NavLink("Upload Resume",href="/upload_cv")),
                    ],navbar=True)
                ],width={"size":"auto"})
            ],align="center"),

            ### navbar toggler

            dbc.Col(dbc.NavbarToggler(id="navbar-toggler",n_clicks=0)),

            ### row no 3 for instagram link and other links

            dbc.Row([
                dbc.Col(
                    dbc.Collapse(
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink(html.I(className="bi bi-instagram text-white"),href="https://www.instagram.com/elitewaresoultions?igsh=MWJ0ajgwaHp0bWR2aw==")),
                            dbc.NavItem(dbc.NavLink(html.I(className="bi bi-buildings text-white "),href="https://elitewaresolutions.com/")),
                        ]),
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                        className="center",
                    
                    )
                )
            ],align="center")


        ],fluid=True
    ),
    color="dark",
    dark=True
)