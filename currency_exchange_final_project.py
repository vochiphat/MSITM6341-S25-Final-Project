import os
import requests
import pandas as pd
from datetime import date, timedelta
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px

# ---------------------------- Data Fetch and Preparation ---------------------------- #

# Define time range
end_date = date.today()
start_date = end_date - timedelta(days=365 * 2)
today = date.today().strftime('%Y-%m-%d')

# Base currency and symbols
base = 'USD'
symbols = 'KRW,AUD,CAD,PLN,MXN,EUR,INR,CNY,HKD,THB,SGD'

# Currency full names
currency_names = {
    'KRW': 'KRW - South Korean Won',
    'AUD': 'AUD - Australian Dollar',
    'CAD': 'CAD - Canadian Dollar',
    'PLN': 'PLN - Polish Zloty',
    'MXN': 'MXN - Mexican Peso',
    'EUR': 'EUR - Euro',
    'INR': 'INR - Indian Rupee',
    'CNY': 'CNY - Chinese Yuan',
    'HKD': 'HKD - Hong Kong Dollar',
    'THB': 'THB - Thai Baht',
    'SGD': 'SGD - Singapore Dollar',
    'USD': 'USD - US Dollar'
}

# Frankfurter API URL
url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base}&to={symbols}"

# Data file name
data_file = 'frankfurter_exchange_rates.csv'

# Check if data file exists; if not, fetch it
if not os.path.exists(data_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['rates']).T
        df.index.name = 'Date'
        df.reset_index(inplace=True)
        df.to_csv(data_file, index=False)
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Failed to fetch data: {e}")

# Load the data
df = pd.read_csv(data_file)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
df.rename(columns={'Date': 'Week_start'}, inplace=True)

# ✅ Your original print outputs (keep them)
print(f'Display Data:\n{df.head()}')
print(f'Statistical Summary:\n{df.describe()}')
print(f'Checking Null Values:\n{df.isnull().sum()}')

# ---------------------------- Dashboard Build ---------------------------- #

# Initialize Dash app
app = Dash(__name__)
server = app.server

# Pick default dropdown currency dynamically
default_currency = df.columns[1] if len(df.columns) > 1 else None

# Pre-calculate data for additional graphs
latest_rates = df.iloc[-1].drop('Week_start')
first_rates = df.iloc[0].drop('Week_start')
percentage_change = ((latest_rates - first_rates) / first_rates) * 100

# Calculate volatility and keep Week_start
volatility = df.drop('Week_start', axis=1).rolling(window=4).std()
volatility['Week_start'] = df['Week_start']   # ✅ Fix: Add dates back

# App layout
app.layout = html.Div([
    html.Div([
        html.H2("Currency Exchange Rates vs USD", style={
            'textAlign': 'center',
            'color': 'Black',
            'fontSize': '32px',
            'fontWeight': 'bold',
            'fontFamily': 'Arial Black',
            'marginTop': '20px'
        }),
        html.H4(f"Current Date: {today}", style={'textAlign': 'center'}),
        dcc.Dropdown(
            options=[{'label': currency_names.get(col, col), 'value': col} for col in df.columns if col != 'Week_start'],
            value=default_currency,
            id='currency-dropdown'
        ),
        html.Label("USD Amount:", style={'fontWeight': 'bold'}),
        dcc.Input(id='usd-input', type='number', value=1),
        html.Div(id='converted-value'),
        dcc.Graph(id='line-chart'),
    ], style={'width': '80%', 'margin': 'auto'}),

    html.Div([
        html.Div([
            html.H3("Latest Exchange Rates (vs USD)", style={
                'textAlign': 'center',
                'color': 'black',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'fontFamily': 'Arial Black',
                'marginBottom': '10px'
            }),
            dash_table.DataTable(
                id='latest-rates-table',
                columns=[
                    {'name': 'Currency', 'id': 'Currency'},
                    {'name': 'Rate vs USD', 'id': 'Rate'}
                ],
                data=[
                    {'Currency': currency_names.get(cur, cur), 'Rate': f"{val:,.4f}"}
                    for cur, val in latest_rates.items()
                ],
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                style_table={
                    'width': '100%',
                    'height': '500px',
                    'overflowY': 'auto',
                    'overflowX': 'auto'
                },
                style_cell={
                    'textAlign': 'center',
                    'fontSize': 16,
                    'fontFamily': 'Arial',
                    'padding': '10px'
                },
                style_header={
                    'backgroundColor': 'lightgrey',
                    'fontWeight': 'bold',
                    'fontFamily': 'Arial Black',
                    'textAlign': 'center'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'Currency'}, 'width': '70%', 'textAlign': 'left'},
                    {'if': {'column_id': 'Rate'}, 'width': '30%', 'textAlign': 'center'},
                ],
            )
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Graph(
                id='bar-change',
                figure=px.bar(
                    x=percentage_change.index,
                    y=percentage_change.values,
                    labels={'x': 'Currency', 'y': '% Change'},
                    title='1-Year % Change vs USD'
                ).update_layout(
                    title_font=dict(size=20, family='Arial Black', color='black'),
                    title_x=0.5
                )
            )
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'width': '80%', 'margin': 'auto', 'paddingTop': '50px'}),

    html.Div([
        html.H3("", style={
            'textAlign': 'center',
            'color': 'black',
            'fontSize': '20px',
            'fontWeight': 'bold',
            'fontFamily': 'Arial Black'
        }),
        dcc.Graph(
            id='volatility-line',
            figure=px.line(
                volatility,
                x=volatility.index,   
                y=volatility.columns.drop('Week_start'), 
                labels={'value': 'Volatility', 'variable': 'Currency'},
                title='Currency Volatility (Weekly Std Dev)'
            ).update_layout(
                title_font=dict(size=20, family='Arial Black', color='black'),
                title_x=0.5
            )
        )
    ], style={'width': '80%', 'margin': 'auto', 'paddingTop': '50px'})
])

# Callbacks to update the graph and conversion
@app.callback(
    Output('line-chart', 'figure'),
    Output('converted-value', 'children'),
    Input('currency-dropdown', 'value'),
    Input('usd-input', 'value')
)
def update_chart(currency, amount):
    full_currency_name = currency_names.get(currency, currency)
    fig = px.line(
        df,
        x='Week_start',
        y=currency,
        title=f"{full_currency_name} per 1 {currency_names.get(base, base)}",
        labels={'Week_start': 'Week Start (Monday)', currency: full_currency_name}
    )
    fig.update_layout(
        xaxis_range=[df['Week_start'].min(), df['Week_start'].max()],
        title_font=dict(size=20, family='Arial Black', color='black'),
        title_x=0.5
    )

    latest_rate = df[currency].iloc[-1]
    converted = amount * latest_rate
    return fig, f"{amount:,.2f} USD = {converted:,.2f} {currency} (latest)"


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
