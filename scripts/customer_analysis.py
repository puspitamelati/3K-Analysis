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

# make datafram grouped by year and Customer ID
df_group_2 = (
    df.groupby(["Date", "Customer ID", "Year"])
    .agg({"Price": "mean", "Quantity": "sum", "Sales": "sum"})
    .reset_index()
)

# add bin and selection
ad_bin = alt.binding_select(
    options=["2016", "2017", "2018", "2020", "2021"], name="Year"
)
ad_selec = alt.selection_single(fields=["Year"], bind=ad_bin)

# Top 5 Best Customer
group_2 = (
    df.groupby(["Year", "Customer ID"])
    .agg({"Quantity": "sum", "Sales": "sum"})
    .reset_index()
)
group_2["Rank"] = group_2.groupby(["Year"])["Quantity"].rank(
    ascending=False, method="first"
)

best = (
    alt.Chart(group_2)
    .mark_bar(color="maroon")
    .encode(
        alt.X("sum(Quantity):Q", axis=alt.Axis(title="Date")),
        alt.Y(
            "Customer ID:O",
            sort="-x",
            axis=alt.Axis(title="Customer ID", titleColor="maroon"),
        ),
    )
    .properties(title="Top 5 Best Customer", height=300, width=400)
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
    .transform_filter(alt.FieldRangePredicate(field="Rank", range=[1, 5]))
)

# total customer across time
g_1 = (
    alt.Chart(df_group_2)
    .mark_bar(color="maroon")
    .encode(
        alt.X("yearmonth(Date):T", axis=alt.Axis(title="Date")),
        alt.Y(
            "distinct(Customer ID):O",
            axis=alt.Axis(title="Total Customer", titleColor="maroon"),
        ),
        # alt.Color('Quantity:N',
        # legend = alt.Legend(title = 'Basket Size')),
        # bin = alt.Bin(step=5)), #using (N) to see how many item that purchases from each customer
        tooltip=("yearmonth(Date):T", "distinct(Customer ID):N"),
    )
    .properties(title="Total Customer Accros Month ", height=300, width=400)
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
)

# see new customer accros month
group_cust = df_group_2.drop_duplicates(
    subset=["Customer ID"], keep="first"
)  # new dataset that have not duplicatet customer id

g_2 = (
    alt.Chart(group_cust)
    .mark_bar(color="maroon", interpolate="monotone")
    .encode(
        alt.X("yearmonth(Date):T", axis=alt.Axis(title="Date")),
        alt.Y(
            "count(Customer ID):O",
            axis=alt.Axis(title="Total New Customer", titleColor="maroon"),
        ),
        tooltip=("yearmonth(Date):T", "count(Customer ID):N"),
    )
    .properties(title="New Customer Accros Month ", height=300, width=400)
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
)

# average curtomer basket size across months
g_3 = (
    alt.Chart(df_group_2)
    .transform_aggregate(monthly_count="count(Quantity):Q", groupby=["Date", "Year"])
    .mark_bar(color="maroon")
    .encode(
        alt.X("yearmonth(Date):T", axis=alt.Axis(title="Date")),
        alt.Y(
            "average(monthly_count):Q",
            axis=alt.Axis(
                title="Average Basket Size", format=".1f", titleColor="maroon"
            ),
        ),
        tooltip=("yearmonth(Date):T", "average(monthly_count):Q"),
    )
    .properties(
        title="Average Customer Basket Size Accros Month ", height=300, width=400
    )
    .add_selection(ad_selec)
    .transform_filter(ad_selec)
)

alt.vconcat(best & g_1 | g_2 & g_3)
