import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# pandas dataframe to html table
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
    ])])

app = dash.Dash(__name__, external_stylesheets=stylesheet)

server = app.server

df =pd.read_csv('overall.csv')
df = df[["city", "price", "reviews", "guests", "bedrooms", "score", "freeparking", "wifi", "country"]]
df = df.groupby(["city", "country"]).mean()
df['city_name'] = df.index.get_level_values('city')
df['country_name'] = df.index.get_level_values('country')
fig = px.bar(df, x=df.index.get_level_values('city'), y="price", hover_data=['guests', 'bedrooms', 'score', 'freeparking', 'wifi', df.index.get_level_values('country')], color="reviews", barmode="group")

app.layout = html.Div([
    html.H1(' Aibnb comparison Checker', style={'textAlign': 'center'}),
    html.Div([html.H4('Number of rows to display:'),
              dcc.Slider(id="num_row_slider", min=0, max=min(10, len(df)), value=6,
              marks={i:str(i) for i in range(len(df)+1)}),
              html.H4('Select Cities to display:'),
              dcc.Checklist(options=[{'label': 'Birmingham', 'value': 'Birmingham'},
                                     {'label': 'London', 'value': 'London'},
                                     {'label': 'barcelona', 'value': 'barcelona'},
                                     {'label': 'losangles', 'value': 'losangles'},
                                     {'label': 'newyork', 'value': 'newyork'},
                                     {'label': 'tokyo', 'value': 'tokyo'}],
                           id="city_select_checklist",
                           value=['Birmingham', 'London', 'barcelona', 'losangles', 'newyork', 'tokyo']),
            html.H4('Select parameters to display on hover:'),
            dcc.Checklist(options=[{'label': 'guests', 'value': 'guests'},
                                     {'label': 'bedrooms', 'value': 'bedrooms'},
                                     {'label': 'score', 'value': 'score'},
                                     {'label': 'freeparking', 'value': 'freeparking'},
                                     {'label': 'wifi', 'value': 'wifi'}],
                           id="column_select_checklist",
                           value=['guests', 'bedrooms', 'score', 'freeparking', 'wifi']),
             html.H4('Sort table by:'),
             dcc.Dropdown(options=[{'label': 'city', 'value': 'city'},
                                    {'label': 'price', 'value': 'price'},
                                    {'label': 'reviews', 'value': 'reviews'}],
                           id='sort_by_dropdown',
                           value='city'),
            html.H4('Select Y-axis by:'),
             dcc.Dropdown(options=[{'label': 'price', 'value': 'price'},
                                    {'label': 'bedrooms', 'value': 'bedrooms'},
                                     {'label': 'score', 'value': 'score'},
                                     {'label': 'freeparking', 'value': 'freeparking'},
                                     {'label': 'wifi', 'value': 'wifi'},
                                     {'label': 'guests', 'value': 'guests'}
                                    ],
                           id='Select_Y_axis_by',
                           value='price')],
             style={'width': '49%', 'display': 'inline-block'}),
    html.Div(html.Div(id="df_div"),
             style={'width': '49%', 'display': 'inline-block', 'float': 'right'}),
    dcc.Graph(id="bar-chart")
    ])

# Update the table
@app.callback(
    Output(component_id='df_div', component_property='children'),
    [Input(component_id='num_row_slider', component_property='value'),
     Input(component_id='city_select_checklist', component_property='value'),
     Input(component_id='sort_by_dropdown', component_property='value')]
)
def update_table(num_rows_to_show, cities_to_display, sort_by):
    x = df[df.index.get_level_values('city').isin(cities_to_display)].sort_values(sort_by, ascending=(sort_by != "price"))
    return generate_table(x, max_rows=num_rows_to_show)

# Update the slider max
@app.callback(
    Output(component_id='num_row_slider', component_property='max'),
    [Input(component_id='city_select_checklist', component_property='value')]
)
def update_slider(cities_to_display):
    x = df[df.index.get_level_values('city').isin(cities_to_display)]
    return min(10, len(x))

#update the chart based on city names
@app.callback(
    Output("bar-chart", "figure"), 
    [Input(component_id='city_select_checklist', component_property='value')],
    [Input(component_id='column_select_checklist', component_property='value')],
    [Input(component_id='Select_Y_axis_by', component_property='value')])
def update_bar_chart(cities_to_display,columns_to_display,Select_Y_axis_by):
    result_df = df[df.index.get_level_values('city').isin(cities_to_display)]
    fig = px.bar(result_df, x=result_df.index.get_level_values('city'), y=Select_Y_axis_by,  hover_data=columns_to_display, color="reviews", labels={'x':'City Names'},barmode="group")
    return fig

#update the chart based on column names selected


if __name__ == '__main__':
    app.run_server(debug=True)