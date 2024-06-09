import streamlit as st
import datetime as dt
import pandas as pd
from typing import List, Tuple

# Establishing connection

# Load equity data from CSV

equity_data = pd.read_csv("Equitydata.csv",parse_dates=['Eq_Date'], dayfirst=True)
equity_data['Eq_Date'] = pd.to_datetime(equity_data['Eq_Date'])
equity_data['Eq_Data'] = equity_data['Eq_Date'].dt.date

# Define function to filter data based on date range
def filter_data_by_date_range(data, start_date, end_date):
    return data[(data['Eq_Date'] >= start_date) & (data['Eq_Date'] <= end_date)]

def filter_data(data: pd.DataFrame, column: str, values: List[str]) -> pd.DataFrame:
    return data[data[column].isin(values)] if values else data


def display_sidebar(data: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:

    st.sidebar.header("Filters")
    #start_date = pd.Timestamp(st.sidebar.date_input("Start date", data['Eq_Date'].min().date()))
    #end_date = pd.Timestamp(st.sidebar.date_input("End date", data['Eq_Date'].max().date()))

    start_date = st.sidebar.date_input('Start Date')
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = st.sidebar.date_input('End Date')
    end_date = end_date.strftime('%Y-%m-%d')

    filtered_data = filter_data_by_date_range(equity_data, start_date, end_date)

    #product_lines = sorted(data['Eq_Symbol'].unique())

    selected_Eq_Symbol = st.sidebar.multiselect("Equity Symbol", data['Eq_Symbol'].unique())
    top_n = st.sidebar.number_input('Top N',min_value=1, value=1, step=1)
    order = st.sidebar.number_input('Order',min_value=-100, value=1, step=1)
    stopwatch = st.sidebar.number_input('Stop Loss',min_value=-100, value=1, step=1)
    Gainer_Losers = st.sidebar.radio(
    "Choose Gainer/Losers",
    ('Gainer', 'Losers')
    )
    Buy_Sell = st.sidebar.radio(
    "Choose Buy/Sell",
    ('Buy', 'Sell')
    )

    st.sidebar.info('Select Prompts')
    return selected_Eq_Symbol,start_date,end_date,top_n,order,stopwatch

def Top_N(filtered_data,top_n):
    filtered_data['Profit'] = filtered_data['Close'] - filtered_data['PrevClose']
    filtered_data['Profit%'] = ((filtered_data['Close'] - filtered_data['PrevClose'])/filtered_data['Close'])*100
    sorted_profit = filtered_data.sort_values(by=['Date','Profit%'],ascending=[True,False])
    grouped = sorted_profit.groupby('Date')
    # Select the top N regions with the highest sales
    # Choose the top N regions
    top_sales = grouped.head(top_n)
    top_sales['Lead_Date'] = top_sales['Date'].shift(-1)
    return top_sales

def Analysis(Filtered_data,equity_data):
    result_inner = pd.merge(Filtered_data, equity_data, left_on=['Lead_Date','Symbol'], right_on=['Eq_Data','Eq_Symbol'], how='inner')
    return result_inner

def Order_Stopwatch(filtered_data,order,stopwatch):
    filtered_data['Open_Order'] = filtered_data['Open']*order*0.01+filtered_data['Open']
    filtered_data['Stop_Loss'] = filtered_data['Open_Order']*stopwatch*0.01+filtered_data['Open_Order']
    filtered_data['New_StopLoss'] = 0 if (filtered_data['Stop_Loss'] < filtered_data['Low']).any() else filtered_data['Stop_Loss']
    return filtered_data

# Streamlit App
def main(): 

    st.title("📊 Stock Market Analsysis")

    selected_Eq_Symbol,start_date,end_date,top_n,order,stopwatch = display_sidebar(equity_data)

    
    filtered_data = equity_data.copy()
    filtered_data = filter_data(filtered_data, 'Eq_Symbol', selected_Eq_Symbol)
    filtered_data = filter_data_by_date_range(filtered_data, start_date, end_date)
    filtered_data = filtered_data[['Eq_Data','Eq_Symbol', 'Eq_PrevClose', 'Eq_Open','Eq_High','Eq_Low','Eq_Close']]
    filtered_data.columns = ['Date', 'Symbol','PrevClose', 'Open','High','Low','Close']
    filtered_data = Top_N(filtered_data,top_n)
    filtered_data = Analysis(filtered_data,equity_data)
    filtered_data = filtered_data[['Eq_Data','Eq_Symbol', 'Eq_PrevClose', 'Eq_Open','Eq_High','Eq_Low','Eq_Close']]
    filtered_data.columns = ['Date', 'Symbol','PrevClose', 'Open','High','Low','Close']
    filtered_data = Order_Stopwatch(filtered_data,order,stopwatch)



    # Display Data Table
    st.write(
        f"""
        <style>
            div.stDataFrame>div:first-child {{
                width: 1500px !important;
                overflow-x: auto;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.dataframe(filtered_data.set_index(filtered_data.columns[0]))

if __name__ == '__main__':
    main()
