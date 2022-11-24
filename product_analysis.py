#import library
import pandas as pd
import datetime
import altair as alt
import requests

#get dataset
df = pd.read_csv("https://raw.githubusercontent.com/puspitamelati/3K-Analysis/main/3K_Data.csv?token=GHSAT0AAAAAAB3TEWTV6654JYPIQAJHIUQWY37QDRA")

#cleaning data
df.drop('Unnamed: 0', axis=1, inplace=True)
df = output_df.dropna()
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.to_period('Y').astype(str)
df['Quantity'] = df['Quantity'].astype(int)
df['Price'] = df['Price'].astype(float)
df['Customer ID'] = df['Customer ID'].astype(str)
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
df['Date'] = pd.to_datetime(df['Date'])
df['Sales'] = (df['Price'])*(df['Quantity'])
df = df[df['Quantity']>=0]

#make dataframe that grouped by Date, Year, and Item Name
df_group_1 = df.groupby(['Date','Item Name','Year']
            ).agg({'Price' : 'mean', 'Quantity' : 'sum', 'Sales' : 'sum'}
            ).reset_index()

#Product Analysis

#add bin and selection
ad_bin = alt.binding_select(options=['2016', '2017', '2018', '2020', '2021'], name='Year')
ad_selec = alt.selection_single(fields=['Year'], bind=ad_bin)

#Total Sales across months
g_1 = alt.Chart(df_group_1).mark_bar(color='maroon').encode(
    alt.X('yearmonth(Date):T',
          axis = alt.Axis(title = 'Year', tickCount=5)),
    alt.Y('sum(Sales):Q',
         axis = alt.Axis(title = 'Total Sales', labelColor='maroon', titleColor='maroon')),
    tooltip = ('yearmonth(Date):T', 'sum(Sales)'))


#Total sales across months
g_2 = alt.Chart(df_group_1).mark_line(color='black', interpolate='monotone').encode(
    alt.X('yearmonth(Date):T',
        axis = alt.Axis(title = 'Date', tickCount=5)),
    alt.Y('sum(Quantity):Q',
        axis = alt.Axis(title = 'Total Items Purchased', labelColor='black', titleColor='black')),
    tooltip = ('yearmonth(Date):T', 'sum(Quantity):Q', 'sum(Sales)'))

point_1 = g_2.mark_circle(color='goldenrod').encode(
    opacity = alt.value(1))


#combine Total Sales and total Items Purchased 
sales_purch = alt.layer(g_1, g_2+point_1).resolve_scale(
    y = 'independent' 
).properties(
    title = "Total Sales and Total Items Purchased Across Months"
).add_selection(ad_selec
).transform_filter(
    ad_selec)

#total items purchased across month
g_3 = alt.Chart(df_group_1).mark_bar(color='maroon').encode(
    alt.X('yearmonth(Date):T',
        axis = alt.Axis(title = 'Date')),
    alt.Y('sum(Quantity):Q',
        axis = alt.Axis(title = 'Total Items Purchased', labelColor='maroon', titleColor='maroon')),
    tooltip = ('yearmonth(Date):T', 'sum(Quantity):Q', 'average(Price):Q'))

#average product price across months
g_4 = alt.Chart(df_group_1).mark_line(color='black', interpolate='monotone', ).encode(
    alt.X('yearmonth(Date):T',
        axis = alt.Axis(title = 'Date')),
    alt.Y('average(Price):Q',
        axis = alt.Axis(title = 'Price',  labelColor='black', titleColor='black')),
     tooltip = ('yearmonth(Date):T', 'sum(Quantity):Q', 'average(Price):Q'))

point_2 = g_4.mark_circle(color='goldenrod').encode(
    opacity = alt.value(1))


#combine number of purchases and Average price across months
purch_price = alt.layer(g_3, g_4 + point_2).resolve_scale(
    y = 'independent' 
).properties(
    title = "Total Items Purchased and Average Price  Across Months").interactive(
).add_selection(ad_selec
).transform_filter(
    ad_selec)

#how many kind of product/items purchased across months
g_5 = alt.Chart(df_group_1).mark_bar(color='maroon').encode(
    alt.X('yearmonth(Date):T',
         axis = alt.Axis(title = 'Date')),
    alt.Y('distinct(Item Name):O',
        axis = alt.Axis(title = 'Product Purchased', labelColor='maroon', titleColor='maroon')),
    tooltip = ('yearmonth(Date):T', 'distinct(Item Name):N', 'sum(Quantity):Q')
).properties(title='Total Customer and Quantity Purchases Accros Month ')

#combine Product and Average price across months
prod_price = alt.layer(g_5, g_4 + point_2).resolve_scale(
    y = 'independent',
).properties(
    title = "Product Purchased and Average Price Across Months").interactive(
).add_selection(ad_selec
).transform_filter(
    ad_selec)

alt.vconcat(sales_purch|purch_price|prod_price )

