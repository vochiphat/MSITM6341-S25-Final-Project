import streamlit as st
import pandas as pd
from exchange_rate_tracker import generate_fake_historical_data

st.set_page_config(page_title="Currency Exchange Rate Tracker", layout="centered")

st.title("💱 Currency Exchange Rate Tracker")

# Generate data
df_cop = generate_fake_historical_data('COP')
df_eur = generate_fake_historical_data('EUR')

# Merge data
df = pd.merge(df_cop, df_eur, on='Date')

st.subheader("📊 Last 10 Days of USD to COP and USD to EUR")
st.dataframe(df)

st.line_chart(df.set_index('Date'))
st.subheader("📈 USD to COP and USD to EUR Exchange Rate")

            