import os
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import math

from config import DATA_DIR


# item_name = 'Alpha\'s Howl'
# item_name = 'Atziri\'s Promise'
# item_name = 'Atziri\'s Foible'
item_name = 'Bottled Faith'

fp = os.path.join(DATA_DIR, 'csv', f'{item_name}.csv')
percentile = 0.95
figs_per_row = 2

def load_data(fp, percentile):
    df_all = pd.read_csv(fp)
    df = df_all.nsmallest(int(len(df_all) * percentile), 'price')
    df = pd.DataFrame(df, index=sorted(df.index))
    df.reset_index(drop=True, inplace=True)
    return df

def get_figure(df, x_col, y_col, selectedpoints):
    fig = px.scatter(df, x=df[x_col], y=df[y_col], text=df.index)
    fig.update_traces(
        selectedpoints=selectedpoints,
        customdata=df.index,
        mode='markers',
        marker={ 'color': 'rgba(255, 0, 0, 0.7)', 'size': 10 },
        unselected={
            'marker': {
                'color': 'rgba(0, 116, 217, 0.2)',
                'size': 7,
            },
        }
    )
    fig.update_layout(dragmode='select')
    return fig

def intersect(a, b):
    return [v for v in a if v in b]

# load data
df = load_data(fp, percentile)

# calculate dash layout
num_figs = len(df.columns) - 1
num_rows = math.ceil(num_figs / figs_per_row)
fig_width = math.floor(100 / figs_per_row)

# create figures
rows = []
for row_num in range(num_rows):
    row = [
        dcc.Graph(id=f'graph-{i + row_num * figs_per_row}', style={'width': f'{fig_width}vw', 'height': '45vh'})
    for i in range(figs_per_row)]
    rows.append(html.Div(row, style={'display': 'flex'}))

# create dashboard
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1(children=item_name),
    *rows
])

@app.callback(
    [Output(f'graph-{i}', 'figure') for i in range(num_figs)],
    [Input(f'graph-{i}', 'selectedData') for i in range(num_figs)]
)
def update_graph(*args):
    selected_points = df.index
    for selected_data in [*args]:
        if selected_data and selected_data['points']:
            selected_points = intersect(selected_points, [p['customdata'] for p in selected_data['points']])
    return [
        get_figure(df, df.columns[i], df.columns[0], selected_points)
    for i in range(1, len(df.columns))]


if __name__ == '__main__':
    pass
    app.run_server()
