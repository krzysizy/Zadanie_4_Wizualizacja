import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
# import kaggle
# from kaggle.api.kaggle_api_extended import KaggleApi
import plotly.graph_objects as go

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Russia Ukraine War Dashboard", page_icon=":crossed_swords:", layout="wide")

# ---- PAGE TIME REFREASH ----
st_autorefresh(interval=60 * 60 * 1000, key="dataframerefresh")

# ---- KAGGLE API ----
# api = KaggleApi()
# api.authenticate()

# ---- CHANGE DATA ----
def change_data (column_name, df):
    temp = []
    for i in range(0, len(df)):
        if i == 0:
            temp.append(df.iloc[i][column_name])
        else:
            temp.append(df.iloc[i][column_name] - df.iloc[i-1][column_name])
    df.drop([column_name], inplace=True, axis=1)
    df[column_name] = temp

# ---- READ KAGGLE ----
def get_data_from_kaggle():
    # api.dataset_download_file('piterfm/2022-ukraine-russian-war', 
    #                             file_name = 'russia_losses_equipment.csv')
    df = pd.read_csv('russia_losses_equipment.csv')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.dropna(axis=1, how='any')
    return df

# ---- HEATMAP ----
def get_heatmap(df, columns):
    if df.shape[1] > 1 : 
        #Days
        x_i = df['day'].tolist()
        #Columns(categories)
        y_i = columns
        df = df.loc[:, columns]
        z_i = []
        for i in range(df.index[0], df.index[-1]+1):
            temp = df.loc[ i, :].values.flatten().tolist()
            z_i.append(temp)

        fig = go.Figure(data=go.Heatmap(
                        z = z_i,
                        x = y_i,
                        y = x_i,
                        
                        hoverongaps = False))
        fig.layout.height = 700
        fig.layout.width = 1000

        tab1, tab2 = st.tabs(["Default theme", "Native theme"])
        with tab1:
            st.plotly_chart(fig, theme="streamlit")
        with tab2:
            st.plotly_chart(fig, theme=None)


rle = get_data_from_kaggle()
rle_columns_without_date_day = list(rle.columns)
rle_columns_without_date_day.remove('day')
rle_columns_without_date_day.remove('date')
for c in rle_columns_without_date_day:
    change_data(c, rle)

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")

days = st.sidebar.slider(
     'Select a range of values',
     int(rle['day'].iloc[0]), int(rle['day'].iloc[-1]), (int(rle['day'].iloc[0]), int(rle['day'].iloc[-1])))

categories = st.sidebar.multiselect(
    "Select the categories:",
    options = rle_columns_without_date_day,
    default = rle_columns_without_date_day
)

categories_with_days = categories
categories_with_days.insert(0, 'day')

df_selection = rle.loc[:, categories_with_days]

# ---- Final selection dataframe ----
df_selection = df_selection[df_selection['day'].between(days[0], days[1])]

# ---- MAIN PAGE ----
st.title(":bar_chart: Russia Ukraine War Dashboard")
categories.remove('day')
get_heatmap(df_selection, categories)
