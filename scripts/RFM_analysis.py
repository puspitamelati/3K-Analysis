#RFM Analysis

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

#make datafram grouped Customer ID
df_group_3 = df.copy()
df_group_3 ['Date_2'] = df_group_3['Date'].copy() #make two date, one for calculate recency and one for calculate frequency (number of purchase)
df_group_3 = df_group_3.groupby(['Customer ID', 'Year']).agg({'Date': lambda Date: (Date.max()-Date.min()).days,
'Date_2' : lambda num : len(num),'Quantity': lambda quant: quant.sum(),'Sales': lambda sales : sales.sum()}).reset_index()

#change group_3 column's name
df_group_3.columns = ['Customer ID','Year', 'Recency', 'Frequency', 'Quantity','Monetary Value']

#ranking customer
df_group_3['R_rank'] = df_group_3.groupby(['Year'])['Recency'].rank(method='first')
df_group_3['F_rank'] = df_group_3.groupby(['Year'])['Frequency'].rank(method='first')
df_group_3['M_rank'] = df_group_3.groupby(['Year'])['Monetary Value'].rank(method='first')

df_group_3["R"] = pd.cut(df_group_3["R_rank"], 4, labels=[4,3,2,1]) #If the customer bought in recent past, he gets higher points
df_group_3["F"] = pd.cut(df_group_3["F_rank"],4,labels=[1,2,3,4])
df_group_3["M"] = pd.cut(df_group_3["R_rank"],4,labels=[1,2,3,4])
df_group_3["RFM Score"] = df_group_3["R"].astype(str) +df_group_3["F"].astype(str) + df_group_3["M"].astype(str)

#categorize the customer based on RFM value
champions = ['444']
loyal_customers =['334', '342', '343', '344', '433', '434', '443']
potential_loyalist = ['332', '333', '341', '412', '413', '414', '431', '432', '441', '442', '421', '422', '423', '424']
recent_customers = ['411']
promising = ['311', '312', '313', '331']
needing_attention = ['212', '213', '214', '231', '232', '233', '241', '314', '321', '322', '323', '324']
about_to_sleep = ['211']
at_risk = ['112', '113', '114', '131', '132', '133', '142', '124', '123', '122', '121', '224', '223', '222', '221']
cant_lose = ['134', '143', '144', '234', '242', '243', '244']
hibernating = ['141']
lost = ['111']

def rfm_level(df):
    if ((df['RFM Score'] in champions )):
        return 'Champions'
    elif ((df['RFM Score'] in loyal_customers)):
        return 'Loyal Customers'
    elif ((df['RFM Score'] in potential_loyalist)):
        return 'Potential Loyalist'
    elif ((df['RFM Score'] in recent_customers)):
        return 'Recent Customers'
    elif ((df['RFM Score'] in promising)):
        return 'Promising'
    elif ((df['RFM Score'] in needing_attention)):
        return 'Needing Attention'
    elif ((df['RFM Score'] in about_to_sleep)):
        return 'About to Sleep'
    elif ((df['RFM Score'] in at_risk)):
        return 'At Risk'
    elif ((df['RFM Score'] in cant_lose)):
        return 'Cant Lose'
    elif ((df['RFM Score'] in hibernating)):
        return 'Hibernating'
    elif ((df['RFM Score'] in lost)):
        return 'Lost'

# Create a new variable RFM_Level
df_group_3['RFM Level'] = df_group_3.apply(rfm_level, axis=1)

#add bin and selection
pts = alt.selection_multi(encodings=['y'])
ad_bin = alt.binding_select(options=['2016', '2017', '2018', '2020', '2021'], name='Year')
ad_selec = alt.selection_single(fields=['Year'], bind=ad_bin)

segment = alt.Chart(df_group_3, title='Customer Segmentation by RFM Value').mark_bar(color='maroon').encode(
    alt.Y('RFM Level'),
    alt.X('distinct(Customer ID):Q'),
    color = alt.condition(pts, alt.Color('distinct(Customer ID):Q'), alt.value("grey")),
    tooltip=['RFM Level', 'count(Customer ID)']
).add_selection(pts
).add_selection(ad_selec
).transform_filter(ad_selec)

#Customer Monatary Value
g_mon = alt.Chart(df_group_3,  title='Customer Monatary Value').mark_bar(color='maroon').encode(
    alt.X('Monetary Value', bin=alt.Bin(maxbins=20)),
    alt.Y('distinct(Customer ID):Q')
).add_selection(pts
).transform_filter(pts
).add_selection(ad_selec
).transform_filter(ad_selec)

#Customer Recency
g_recen = alt.Chart(df_group_3, title='Customer Recency').mark_bar(color='maroon').encode(
    alt.X('Recency', bin=alt.Bin(step=20), title = 'Number of Days'),
    alt.Y('count(Customer ID)')
).add_selection(pts
).transform_filter(pts
).add_selection(ad_selec
).transform_filter(ad_selec)

#Customer by Orders
g_orders = alt.Chart(df_group_3, title='Customer by Orders').mark_bar(color='maroon').encode(
    alt.X('Quantity', title = 'Number of Purchase', bin=alt.Bin(step=2)),
    alt.Y('count(Customer ID)')
).add_selection(pts
).transform_filter(pts
).add_selection(ad_selec
).transform_filter(ad_selec)

alt.vconcat (segment, g_mon | g_orders, center=True)
