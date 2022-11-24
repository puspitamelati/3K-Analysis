#import library
import pandas as pd
import datetime
import altair as alt
from pyodide.http import open_url

#get dataset
url = "https://raw.githubusercontent.com/puspitamelati/3K-Analysis/main/3K_Data.csv?token=GHSAT0AAAAAAB3TEWTV6654JYPIQAJHIUQWY37QDRA"
df = pd.read_csv(open_url(url),parse_dates=["Date"])


#cleaning data
df.drop('Unnamed: 0', axis=1, inplace=True)
df = df.dropna()
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.to_period('Y').astype(str)
df['Quantity'] = df['Quantity'].astype(int)
df['Price'] = df['Price'].astype(float)
df['Customer ID'] = df['Customer ID'].astype(str)
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
df['Date'] = pd.to_datetime(df['Date'])
df['Sales'] = (df['Price'])*(df['Quantity'])
df = df[df['Quantity']>=0]

#make dataframe groupby year and item name
group_1 = df.groupby(['Year','Item Name']).agg({'Quantity' : 'sum', 'Sales' : 'sum'}).reset_index()

#ranked the quantity each year
group_1['Rank']=group_1.groupby(['Year'])['Quantity'].rank(ascending=False)

#add bin and selection
ad_bin = alt.binding_select(options=['2016', '2017', '2018', '2020', '2021'], name='Year')
ad_selec = alt.selection_single(fields=['Year'], bind=ad_bin)

#Purchased Product
prod = alt.Chart(group_1).mark_bar(color='maroon').encode(
    alt.X('sum(Quantity):Q',
         axis = alt.Axis(title = 'Date')),
    alt.Y('Item Name:O',
        axis = alt.Axis(title = 'Product Name', titleColor='maroon')),
    alt.Color('Item Name:O'),
).add_selection(ad_selec
).transform_filter(
    ad_selec)

#Best Selling product
best = alt.Chart(group_1).mark_bar(color='maroon').encode(
    alt.X('sum(Quantity):Q',
         axis = alt.Axis(title = 'Date')),
    alt.Y('Item Name:O',
        axis = alt.Axis(title = 'Product Name', titleColor='maroon')),
    alt.Color('Item Name:O'),
).add_selection(ad_selec
).transform_filter(
    ad_selec
).transform_filter(
    alt.FieldRangePredicate(field='Rank', range=[1,5]))

prod|best

