import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd


data = pd.read_csv('tempdump.csv')
df = pd.DataFrame({
    'price': data['price'],
    '+(100-120) to maximum Mana': data['+(100-120) to maximum Mana']
})
fig = px.scatter(df, y='price', x='+(100-120) to maximum Mana')

app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1(children='Analytics'),
        dcc.Graph(id='price-graph', figure=fig),
    ]
)

if __name__ == '__main__':
    pass
    app.run_server(debug=True)
