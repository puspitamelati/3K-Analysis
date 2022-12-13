# RFM Analysis

# import library
import pandas as pd
import datetime
import altair as alt
from pyodide.http import open_url

# get dataset
url = "https://raw.githubusercontent.com/puspitamelati/3K-Analysis/main/3K_Data.csv?token=GHSAT0AAAAAAB3TEWTV6654JYPIQAJHIUQWY37QDRA"
df = pd.read_csv(open_url(url), parse_dates=["Date"])

# cleaning data
df.drop("Unnamed: 0", axis=1, inplace=True)
df = df.dropna()
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.to_period("Y").astype(str)
df["Quantity"] = df["Quantity"].astype(int)
df["Price"] = df["Price"].astype(float)
df["Customer ID"] = df["Customer ID"].astype(str)
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
df["Date"] = pd.to_datetime(df["Date"])
df["Sales"] = (df["Price"]) * (df["Quantity"])
df = df[df["Quantity"] >= 0]

# make datafram grouped Customer ID
df_group_3 = df.copy()
df_group_3["Date_2"] = df_group_3[
    "Date"
].copy()  # make two date, one for calculate recency and one for calculate frequency (number of purchase)
df_group_3 = (
    df_group_3.groupby(["Customer ID", "Year"])
    .agg(
        {
            "Date": lambda Date: (Date.max() - Date.min()).days,
            "Date_2": lambda num: len(num),
            "Quantity": lambda quant: quant.sum(),
            "Sales": lambda sales: sales.sum(),
        }
    )
    .reset_index()
)

# change group_3 column's name
df_group_3.columns = [
    "Customer ID",
    "Year",
    "Recency",
    "Frequency",
    "Quantity",
    "Monetary Value",
]

# ranking customer
df_group_3["R_rank"] = df_group_3.groupby(["Year"])["Recency"].rank(method="first")
df_group_3["F_rank"] = df_group_3.groupby(["Year"])["Frequency"].rank(method="first")
df_group_3["M_rank"] = df_group_3.groupby(["Year"])["Monetary Value"].rank(
    method="first"
)

df_group_3["R"] = pd.cut(
    df_group_3["R_rank"], 4, labels=[4, 3, 2, 1]
)  # If the customer bought in recent past, he gets higher points
df_group_3["F"] = pd.cut(df_group_3["F_rank"], 4, labels=[1, 2, 3, 4])
df_group_3["M"] = pd.cut(df_group_3["R_rank"], 4, labels=[1, 2, 3, 4])
df_group_3["RFM Score"] = (
    df_group_3["R"].astype(str)
    + df_group_3["F"].astype(str)
    + df_group_3["M"].astype(str)
)

# categorize the customer based on RFM value
def status(r, f):
    status_name = {
        (4, 4): "Champions",
        (4, 3): "Loyal Customer",
        (3, 4): "Loyal Customers",
        (3, 3): "Potential Loyalist",
        (4, 2): "Potential Loyalist",
        (4, 1): "Recent Customers",
        (3, 1): "Recent Customers",
        (3, 2): "Needing Atention",
        (2, 3): "Needing Atention",
        (2, 1): "About to Sleep",
        (1, 3): "At Risk",
        (2, 2): "At Risk",
        (2, 4): "Cant Lose",
        (1, 4): "Hibernating",
        (1, 1): "Lost",
    }
    return status_name[(r, f)]


# Create a new variable RFM_Level
df_group_3["RFM Level"] = df_group_3.apply(lambda x: status(x["R"], x["F"]), axis=1)

# add bin and selection
pts = alt.selection_multi(encodings=["y"])
ad_bin = alt.binding_select(
    options=["2016", "2017", "2018", "2020", "2021"], name="Year"
)
ad_selec = alt.selection_single(fields=["Year"], bind=ad_bin)

segment = (
    alt.Chart(df_group_3, title="Customer Segmentation by RFM Value")
    .mark_bar(color="maroon")
    .encode(
        alt.Y("RFM Level"),
        alt.X("distinct(Customer ID):Q"),
        color=alt.condition(
            pts, alt.Color("distinct(Customer ID):Q"), alt.value("grey")
        ),
        tooltip=["RFM Level", "count(Customer ID)"],
    )
    .add_selection(pts)
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
    .properties(height=250, width=400)
)

# function for generate graph
def chart(x, y, agg, tipe, title):
    return (
        alt.Chart(df_group_3, title=title)
        .mark_bar(color="maroon")
        .encode(
            alt.X(x, bin=alt.Bin(maxbins=20)),
            alt.Y(y, aggregate=agg, type=tipe),
        )
        .add_selection(pts)
        .transform_filter(pts)
        .add_selection(ad_selec)
        .transform_filter(ad_selec)
    )


# Customer Monatary Value
g_mon = chart(
    "Monetary Value",
    "Customer ID",
    "distinct",
    "quantitative",
    "Customer Monatary Value",
)

# Customer by Orders
g_orders = chart(
    "Quantity", "Customer ID", "count", "quantitative", "Customer by Orders"
)

alt.vconcat(segment, g_mon | g_orders, center=True)
