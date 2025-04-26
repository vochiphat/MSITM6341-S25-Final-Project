import requests
import pandas as pd
from datetime import date, timedelta

# Define time range
end_date = date.today() # end date as today
start_date = end_date - timedelta(days=365*2) # start from last 2 years
today = date.today().strftime('%Y-%m-%d') # current date
#OR
#start_date = datetime.strptime("2023-11-01", "%Y-%m-%d").date()
#end_date = datetime.strptime("2024-04-23", "%Y-%m-%d").date()

base = 'USD'
symbols = 'KRW,AUD,CAD,PLN,MXN,EUR,INR,CNY,HKD,THB,SGD'

currency_names = {
    'KRW': 'KRW-South Korean Won',
    'AUD': 'AUD-Australian Dollar',
    'CAD': 'CAD-Canadian Dollar',
    'PLN': 'PLN-Polish Zloty',
    'MXN': 'MXN-Mexican Peso',
    'EUR': 'EUR-Euro',
    'INR': 'INR-Indian Rupee',
    'CNY': 'CNY-Chinese Yuan',
    'HKD': 'HKD-Hong Kong Dollar',
    'THB': 'THB-Thai Baht',
    'SGD': 'SGD-Singapore Dollar',
    'USD': 'US Dollar'
}

# Frankfurter API URL
url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base}&to={symbols}"

# Fetch data
response = requests.get(url)
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data['rates']).T  # Dates as rows
df.index.name = 'Date'
df.reset_index(inplace=True)


# Save to CSV
df.to_csv('frankfurter_exchange_rates.csv', index=False)

#print(df.head())


#dashbaord build

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load local CSV instead of calling API
df = pd.read_csv('frankfurter_exchange_rates.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
df.rename(columns={'Date': 'Week_start'}, inplace=True)

print(f' Display Data: /n {df.head()}')
print(f'Statistical Summary: \n {df.describe()}')
print(f'Checking Null Value: \n {df.isnull().sum()}')

# Dash app
app = Dash(__name__)
app.layout = html.Div([
    html.H2("Currency Exchange Rates vs USD",
            style={ #styling format for dash title
                  'textAlign': 'center',
                  'color': 'Black',
                  'fontSize': '32px',
                  'fontWeight': 'bold',
                  'marginTop': '20px'
    }),
    html.H4(f"Current Date: {today}"), #display current daet on dash
    dcc.Dropdown(
    options=[{'label': currency_names.get(col, col), 'value': col} for col in df.columns if col != 'Week_start'],
    value='EUR',
    id='currency-dropdown'
    ),
    dcc.Graph(id='line-chart'),
    html.Label("USD Amount:",
                style={'fontWeight': 'bold'}),
    dcc.Input(id='usd-input', type='number', value=1),
    html.Div(id='converted-value')
])

@app.callback(
    Output('line-chart', 'figure'),
    Output('converted-value', 'children'),
    Input('currency-dropdown', 'value'),
    Input('usd-input', 'value')
)
def update_chart(currency, amount):
    full_currency_name = currency_names.get(currency, currency)  # get full name
    fig = px.line(df, x='Week_start', y=currency, title=f"{currency} per 1 {base}", labels= {'Week_start': 'Week Start (Mondays)', currency : full_currency_name})
    latest_rate = df.iloc[-1,:][currency]
    converted = amount * latest_rate
    return fig, f"{amount:,.2f} USD = {converted:,.2f} {currency} (latest)"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
