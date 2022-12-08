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
status_name = {
    "444": "Champions",
    "334": "Loyal Customers",
    "342": "Loyal Customers",
    "343": "Loyal Customers",
    "344": "Loyal Customers",
    "433": "Loyal Customers",
    "434": "Loyal Customers",
    "443": "Loyal Customers",
    "332": "Potential Loyalist",
    "333": "Potential Loyalist",
    "341": "Potential Loyalist",
    "412": "Potential Loyalist",
    "413": "Potential Loyalist",
    "414": "Potential Loyalist",
    "431": "Potential Loyalist",
    "432": "Potential Loyalist",
    "441": "Potential Loyalist",
    "442": "Potential Loyalist",
    "421": "Potential Loyalist",
    "422": "Potential Loyalist",
    "423": "Potential Loyalist",
    "424": "Potential Loyalist",
    "411": "Recent Customers",
    "311": "Promising",
    "312": "Promising",
    "313": "Promising",
    "331": "Promising",
    "212": "Needing Atention",
    "213": "Needing Atention",
    "214": "Needing Atention",
    "231": "Needing Atention",
    "232": "Needing Atention",
    "233": "Needing Atention",
    "241": "Needing Atention",
    "314": "Needing Atention",
    "321": "Needing Atention",
    "322": "Needing Atention",
    "323": "Needing Atention",
    "324": "Needing Atention",
    "211": "About to Sleep",
    "112": "At Risk",
    "113": "At Risk",
    "114": "At Risk",
    "131": "At Risk",
    "132": "At Risk",
    "133": "At Risk",
    "142": "At Risk",
    "124": "At Risk",
    "123": "At Risk",
    "122": "At Risk",
    "121": "At Risk",
    "224": "At Risk",
    "223": "At Risk",
    "222": "At Risk",
    "221": "At Risk",
    "134": "Cant Lose",
    "143": "Cant Lose",
    "144": "Cant Lose",
    "234": "Cant Lose",
    "242": "Cant Lose",
    "243": "Cant Lose",
    "244": "Cant Lose",
    "141": "Hibernating",
    "111": "Lost",
}


def status(x):
    return status_name.get(x, "None")


# Create a new variable RFM_Level
df_group_3["RFM Level"] = df_group_3["RFM Score"].apply(status)

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

# Customer Monatary Value
g_mon = (
    alt.Chart(df_group_3, title="Customer Monatary Value")
    .mark_bar(color="maroon")
    .encode(
        alt.X("Monetary Value", bin=alt.Bin(maxbins=20)),
        alt.Y("distinct(Customer ID):Q"),
    )
    .add_selection(pts)
    .transform_filter(pts)
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
)

# Customer Recency
g_recen = (
    alt.Chart(df_group_3, title="Customer Recency")
    .mark_bar(color="maroon")
    .encode(
        alt.X("Recency", bin=alt.Bin(step=20), title="Number of Days"),
        alt.Y("count(Customer ID)"),
    )
    .add_selection(pts)
    .transform_filter(pts)
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
)

# Customer by Orders
g_orders = (
    alt.Chart(df_group_3, title="Customer by Orders")
    .mark_bar(color="maroon")
    .encode(
        alt.X("Quantity", title="Number of Purchase", bin=alt.Bin(step=2)),
        alt.Y("count(Customer ID)"),
    )
    .add_selection(pts)
    .transform_filter(pts)
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
)

alt.vconcat(segment, g_mon | g_orders, center=True)
