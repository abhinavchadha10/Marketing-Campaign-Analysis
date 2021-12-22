
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
# import dash_table
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import date
import numpy as np
import plotly.graph_objects as go
from itertools import compress
import dash_table as dt



#FIGURES FOR DASHBOARD
# **************************************************************************************************************
data = pd.read_excel('clean_data.xlsx', index_col = 0)
data.columns = ['ID', 'Year_Birth', 'Age', 'Education', 'Marital_Status', 'Income',
       'Kidhome', 'Teenhome', 'Dt_Customer', 'Recency', 'WINE',
       'FRUIT', 'MEAT', 'FISH', 'SWEETS',
       'GOLD', 'DEAL PURCHASES', 'WEB PURCHASES',
       'CATALOG PURCHASES', 'STORE PURCHASES', 'NumWebVisitsMonth',
       'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5', 'AcceptedCmp1',
       'AcceptedCmp2', 'Response', 'Complain', 'Country']
       
data['total_sales'] = data['WINE'] + data['FRUIT'] + data['MEAT'] + data['FISH'] + data['SWEETS'] + data['GOLD']

total_sales = data['total_sales'].sum()



#Country - Bubble Chart
groupby_country = data.groupby(['Country'])['total_sales'].sum().reset_index()
groupby_country['Sales Percent']=round(100*groupby_country['total_sales']/sum(groupby_country['total_sales']),2)
country_count = groupby_country['Country'].value_counts()
country_count = country_count.reset_index().rename(columns={'index':'Country', 'Country':'Count'})
country_list = groupby_country.Country


new_bubble_chart_fig = px.scatter_geo(groupby_country, 
                    locations='Country',
                    color='Country',
                    locationmode='country names', 
                    size='Sales Percent',
                    size_max=50,
                    color_discrete_map={'Spain':'DarkGreen', 'USA':'DarkSeaGreen', 'India':'wheat', 'Saudi Arabia':'crimson', 'Canada':'goldenrod', 'Germany':'Tomato', 'Australia':'lightslategray', 'Mexico':'saddlebrown'},
                    hover_name = 'Country')
new_bubble_chart_fig.update_layout(
        title_text = 'Total Product Sales by Country (in %)',
        title_x=0.45,
        showlegend = True)
new_bubble_chart_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
new_bubble_chart_fig.update_layout(
    font=dict(
        size=20,
        color="DarkGreen"
    )
)

#Demographics
data['no_dependents_count'] = data['Kidhome'] + data['Teenhome']

data['no_dependents'] = data['no_dependents_count'].map({0:'Zero',1:'One',2:'More than One',3:'More than One'})

data['Education_level'] = data['Education'].map({'PhD': 'Above Graduation', 
                                                  'Master': 'Above Graduation',
                                                  'Graduation': 'Graduation',
                                                  '2n Cycle':'Below Graduation',
                                                  'Basic':'Below Graduation'})

conditions = [
    (data['Income'] <= 40000),
    (data['Income'] > 40000) & (data['Income'] <= 60000),
    (data['Income'] > 60000)
    ]

values = ['Low Income', 'Middle Income', 'High Income']

data['Income_level'] = np.select(conditions, values)

bins = [1939, 1965, 1980, 1996]
name = ['Boomers', 'Gen x', 'Millennials']
data['Age_level'] = pd.cut(data['Year_Birth'], bins, labels=name)

data['Marital_status'] = data['Marital_Status'].map(
    {
        'Together':'Together',
        'Married':'Married',
        'Divorced':'Single',
        'Single':'Single',
        'Widow':'Single'
    }
)

#Table
df = pd.DataFrame(columns = ["Country","Total Sales","Sales Percentage"], index = range(0,9))

for i in df.index:

    if i == 0:
        df.loc[i,"Country"] = "WORLD"
        df.loc[i,"Total Sales"] = total_sales
        df.loc[i,"Sales Percentage"] = 100.00
    else:
        df.loc[i,"Country"] = groupby_country.loc[i-1,"Country"]
        df.loc[i,"Total Sales"] = groupby_country.loc[i-1,"total_sales"]
        df.loc[i,"Sales Percentage"] = round(groupby_country.loc[i-1,"Sales Percent"])

df.sort_values(["Total Sales"], ascending = False, inplace = True)
df= df.reset_index(drop = True)



# **************************************************************************************************************

# HTML Styles: https://www.w3schools.com/html/html_styles.asp
# Source: https://github.com/PacktPublishing/Interactive-Dashboards-and-Data-Apps-with-Plotly-and-Dash 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
                                html.Div(children=[
                                                    #Title
                                                    html.H1(children="Demographic Analysis for Grocery Sales",
                                                            style={'textAlign': 'center','color': 'DarkGreen', 'fontSize': '100px'}, 
                                                            className="header-title"), 
                                                    #Heading 2
                                                    html.H2(children="How does my Demographics impact the Sales of a Product?",
                                                            className="header-description", style={'textAlign': 'center','color': 'DarkSeaGreen', 'fontSize': '50px'}),
                                                  ],
                                        className="header",style={'background':'whitesmoke'},
                                        ),
                                
                                html.Div(children = [
                                                html.H2("Country Wise Sales Distribution",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"30px", 'color': "goldenrod", 'fontSize': '40px', 'width': '100%', 'display': 'inline-block'}),
                                                html.Hr(style = {'width':'39.6%','margin-left':'0px'}),
                                ]),
                                html.Div(children=[
                                                html.H2("   ",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"30px", 'color': "DarkGreen", 'fontSize': '25px', 'width': '100%', 'display': 'inline-block'}),
                                                dbc.Container([
                                                                dt.DataTable(
                                                                    id='tbl', data=df.to_dict('records'),
                                                                    columns=[{"name": i, "id": i} for i in df.columns],
                                                                    style_cell={'textAlign': 'right','padding': '5px','font_size': '30px'},
                                                                    style_cell_conditional=[
                                                                        {
                                                                            'if': {'column_id': 'Country'},
                                                                            'textAlign': 'left'
                                                                        }],
                                                                    style_as_list_view=True,
                                                                    style_header={
                                                                        'backgroundColor': 'whitesmoke',
                                                                        'fontWeight': 'bold',
                                                                        'color': 'DarkSeaGreen',
                                                                    },
                                                                    style_data={
                                                                        'backgroundColor': 'whitesmoke',
                                                                        'color': 'DarkGreen',
                                                                    },
                                                                ),
                                                                dbc.Alert(id='tbl_out'),
                                                            ])
                                        ],style={'width':'40%','display': 'inline-block','vertical-align': 'top'}),

                                        html.Div(children = [
                                            dcc.Graph(id = 'country_sales', style={'display': 'inline-block','vertical-align': 'top', 'height':'40vh','width':'100%'})
                                            ], style={'width':'60%','display': 'inline-block','vertical-align': 'top'}),
                    
                                #Row 4: Product wise Sales
                                html.Div(children=[
                                                html.H2("Product Wise Sales Distribution",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"30px", 'color': "goldenrod", 'fontSize': '40px', 'width': '20%', 'display': 'inline-block'}),
                                                html.H2("  (Absolute and Percentage)",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"10px", 'color': "goldenrod", 'fontSize': '25px', 'width': '30%', 'display': 'inline-block'}),
                                                html.Hr(style = {'width':'39.6%','margin-left':'0px'}),
                                                html.Div(children=[
                                                    #CARD #1
                                                    html.Div(children=[
                                                        html.H3( "Total Sales in WINE", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                                                        html.Div(id ='wine_card', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'}),
                                                        html.Div(id ='wine_card_perc', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'})
                                                    ],style={'width':'15.7%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                                                            'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                                                            'margin-bottom':'15px','margin-top':'30px','margin-left':'15px', 'height':'70%'}),

                                                    #CARD #2
                                                    html.Div(children=[
                                                        html.H3( "Total Sales in MEAT", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                                                        html.Div(id ='meat_card', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'}),
                                                        html.Div(id ='meat_card_perc', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'})
                                                    ],style={'width':'15.7%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                                                            'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                                                            'margin-bottom':'15px','margin-top':'30px','margin-left':'15px', 'height':'70%'}),
                                                    #CARD #3
                                                    html.Div(children=[
                                                        html.H3("Total Sales in FRUITS", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                                                        html.Div(id ='fruit_card', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'}),
                                                        html.Div(id ='fruit_card_perc', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'})
                                                    ],style={'width':'15.7%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                                                            'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                                                            'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
                                                    #CARD #4
                                                    html.Div(children=[
                                                        html.H3("Total Sales in FISH", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                                                        html.Div(id ='fish_card', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'}),
                                                        html.Div(id ='fish_card_perc', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'})
                                                    ],style={'width':'15.7%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                                                            'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                                                            'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
                                                    #CARD #5
                                                    html.Div(children=[
                                                        html.H3("Total Sales in SWEETS", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                                                        html.Div(id ='sweets_card', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'}),
                                                        html.Div(id ='sweets_card_perc', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'})
                                                    ],style={'width':'15.7%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                                                            'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                                                            'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),                                                                                    
                                                    #CARD #6
                                                    html.Div(children=[
                                                        html.H3("Total Sales in GOLD", style={'textAlign':'center', "margin-bottom":"0px", 'color': "goldenrod", 'fontSize': '30px', 'width': '100%', 'display': 'inline-block'}),
                                                        html.Div(id ='gold_card', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'}),
                                                        html.Div(id ='gold_card_perc', style={'textAlign':'center', "margin-bottom":"0px", "margin-top":"8px", 'color': "darkseagreen", 'fontSize': '45px', 'width': '50%','display': 'inline-block'})
                                                    ],style={'width':'15.7%','display': 'inline-block','background': 'wheat','textAlign':'center', 
                                                            'border-style':'solid','border-color':'wheat', 'border-radius':'20px','border-width':'5px',
                                                            'margin-bottom':'15px','margin-top':'15px','margin-left':'15px', 'height':'70%'}),
                                                ],style={'width':'100%','display': 'inline-block','background': 'whitesmoke', 'height':'200px'}),
                                        ],style={'width':'100%','display': 'inline-block','vertical-align': 'top'}),
                                
                                html.Div(children=[
                                                    html.Div(children= [
                                                                        
                                                                        html.Div(children = [
                                                                        html.H2("Affect of",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"30px", 'color': "goldenrod", 'fontSize': '40px', 'width': '8%', 'display': 'inline-block'}),
                                                                        html.Div(dcc.Dropdown(id = 'demog_drop',
                                                                                     options = [
                                                                                         {'label': 'Income Level', 'value': 'Income_level'},
                                                                                         {'label': 'Age Segment', 'value': 'Age_level'},
                                                                                         {'label': 'Education Level', 'value': 'Education_level'},
                                                                                         {'label': 'Marital Status', 'value': 'Marital_status'},
                                                                                         {'label': '# of Dependents', 'value': 'no_dependents'},

                                                                                     ],
                                                                                     value= 'Income_level',
                                                                                     style={"margin-left":"0px",'width': '100%', 'display': 'inline-block'}
                                                                        ),style={"margin-left":"0px",'width': '20%', 'display': 'inline-block'}),
                                                                        html.H2(" on Product Sales",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"5px", 'color': "goldenrod", 'fontSize': '40px', 'width': '38%', 'display': 'inline-block'}),
                                                                        ],style={'width':'100%','display': 'inline-block','background': 'whitesmoke'}),
                                                                        html.Hr(style = {'width':'60%','margin-left':'0px'}),
                                                                        dcc.Graph(id = 'demog_chart',style={'width': '90%',"margin-left":"10px", 'display': 'inline-block'}),
                                                                        html.Div(children = [
                                                                        html.H2("Channel Performance by each ",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"30px", 'color': "goldenrod", 'fontSize': '40px', 'width': '28%', 'display': 'inline-block'}),
                                                                        html.H2(id = 'which_demog',style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"0px", 'color': "goldenrod", 'fontSize': '40px', 'width': '20%', 'display': 'inline-block'}),
                                                                        ]),
                                                                        html.Hr(style = {'width':'60%','margin-left':'0px'}),
                                                                        dcc.Graph(id = 'channel_demog',style={'width': '90%',"margin-left":"10px", 'display': 'inline-block'})
                                                    ],style={'width': '66%', 'display': 'inline-block'}),
                                                    html.Div(children= [
                                                                        html.H2("Funnel Chart",style={'textAlign':'left', "margin-bottom":"0px", "margin-left":"30px", 'color': "goldenrod", 'fontSize': '40px', 'width': '100%','display': 'inline-block'}),
                                                                        html.Hr(style = {'width':'60%','margin-left':'0px'}),
                                                                        dcc.Graph(id = 'funnel',style={'width': '100%', 'height':'66.5vh','display': 'inline-block'})
                                                    ],style={'width': '33%','display': 'inline-block'}),
                                                    
                                                  ])


                                

], style={'background':'whitesmoke'})
    
@app.callback(
            #   Output('test_1','children'),
              Output('country_sales', 'figure'),
              Output('wine_card', 'children'),
              Output('wine_card_perc', 'children'),
              Output('fruit_card', 'children'),
              Output('fruit_card_perc', 'children'),
              Output('meat_card', 'children'),
              Output('meat_card_perc', 'children'),
              Output('fish_card', 'children'),
              Output('fish_card_perc', 'children'),
              Output('sweets_card', 'children'),
              Output('sweets_card_perc', 'children'),
              Output('gold_card', 'children'),
              Output('gold_card_perc', 'children'),
              Output('demog_chart','figure'),
              Output('which_demog','children'),
              Output('channel_demog','figure'),
              Output('funnel','figure'),
              Input('tbl', 'active_cell'),
              Input('demog_drop','value'))

def country_select(active_cell,demog):
    if active_cell:
        index = active_cell['row']
        if index == 0:
            selected_country = country_list
        else:
            selected_country = [df.loc[index,"Country"]]    
    else:
        selected_country = country_list
    
    data_selected = data[data.Country.isin(selected_country)]
    wine_sales = data_selected.WINE.sum()
    fruit_sales = data_selected.FRUIT.sum()
    meat_sales = data_selected.MEAT.sum()
    fish_sales = data_selected.FISH.sum()
    sweets_sales = data_selected.SWEETS.sum()
    gold_sales = data_selected.GOLD.sum()
    total_product_sales = wine_sales + fruit_sales + meat_sales + fish_sales + sweets_sales + gold_sales
    wine_sales_perc = round(wine_sales/total_product_sales*100,2)
    fruit_sales_perc = round(fruit_sales/total_product_sales*100,2)
    meat_sales_perc = round(meat_sales/total_product_sales*100,2)
    fish_sales_perc = round(fish_sales/total_product_sales*100,2)
    sweets_sales_perc = round(sweets_sales/total_product_sales*100,2)
    gold_sales_perc = round(gold_sales/total_product_sales*100,2)

    wine_demog = pd.DataFrame(data_selected.groupby(demog).WINE.sum())
    fruit_demog = pd.DataFrame(data_selected.groupby(demog).FRUIT.sum())
    meat_demog = pd.DataFrame(data_selected.groupby(demog).MEAT.sum())
    fish_demog = pd.DataFrame(data_selected.groupby(demog).FISH.sum())
    sweets_demog = pd.DataFrame(data_selected.groupby(demog).SWEETS.sum())
    gold_demog = pd.DataFrame(data_selected.groupby(demog).GOLD.sum())

    sorter = ['Low Income', 'Middle Income', 'High Income','Zero','One','More than One','Together','Married','Single','Above Graduation','Graduation','Below Graduation','Boomers', 'Gen x', 'Millennials']

    merged_data=wine_demog.merge(fruit_demog, on=demog,how='left') \
        .merge(meat_demog, on=demog,how='left') \
        .merge(fish_demog, on=demog,how='left')\
        .merge(sweets_demog, on=demog,how='left')\
        .merge(gold_demog, on=demog,how='left')
    merged_data[demog]=merged_data.index

    long=merged_data.melt( 
            id_vars=[demog],
            value_vars= ['WINE','FRUIT','MEAT','FISH','SWEETS','GOLD'],
            var_name='Products',
            value_name='Sales')
    
    long[demog] = long[demog].astype("category")
    long[demog].cat.set_categories(sorter, inplace=True)

    long['Total_Sales'] = long['Products'].map(
        {
            'WINE':wine_sales,
            'FRUIT':fruit_sales,
            'MEAT': meat_sales,
            'FISH':fish_sales,
            'SWEETS':sweets_sales,
            'GOLD': gold_sales
        })
    
    long.sort_values(['Total_Sales'], inplace= True, ascending = False)
    list_cat = long[demog].unique()

    if len(list_cat) == 3:
        sales_demog_fig = px.bar(long, x="Products", y="Sales", color=demog, barmode="group",color_discrete_map={list_cat[0]:'DarkGreen', list_cat[1]:'wheat', list_cat[2]:'DarkSeaGreen'})
    elif len(list_cat) == 2:
        sales_demog_fig = px.bar(long, x="Products", y="Sales", color=demog, barmode="group",color_discrete_map={list_cat[0]:'DarkGreen', list_cat[1]:'wheat'})
    elif len(list_cat) == 1:
        sales_demog_fig = px.bar(long, x="Products", y="Sales", color=demog, barmode="group",color_discrete_map={list_cat[0]:'DarkGreen'})
    
    sales_demog_fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = list(range(len(long.Products.unique()))),
            ticktext = long.Products.unique()
        )
    )
    sales_demog_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    sales_demog_fig.update_layout(
        font=dict(
            size=20,
            color="goldenrod"
        )
    )
    sales_demog_fig.update_layout(
        font=dict(
            size=20,
            color="DarkGreen"
        )
    )

    if demog == 'Income_level':
        demog_text = 'Income Level'
    elif demog == 'Age_level':
        demog_text = 'Age Segment'
    elif demog == 'Education_level':
        demog_text = 'Education Level'
    elif demog == 'Marital_status':
        demog_text = 'Marital Status'
    else:
        demog_text = '# of Dependents'

    sales_demog_fig.update_layout(legend_title_text=demog_text)


    demog_channel = pd.DataFrame(data_selected.groupby(demog)[['DEAL PURCHASES', 'WEB PURCHASES','CATALOG PURCHASES', 'STORE PURCHASES']].sum())
    demog_channel[demog]=demog_channel.index

    tidydf_gen = demog_channel.melt( 
                id_vars = [demog],
                value_vars = ['DEAL PURCHASES', 'WEB PURCHASES','CATALOG PURCHASES', 'STORE PURCHASES'],
                var_name = 'Channel', 
                value_name = 'Sum of Total Purchases') 
    
    tidydf_gen[demog] = tidydf_gen[demog].astype("category")
    tidydf_gen[demog].cat.set_categories(sorter, inplace=True)
    
    sort_df = tidydf_gen.groupby('Channel')['Sum of Total Purchases'].sum()  
    tidydf_gen['Total_Sales'] = tidydf_gen.Channel.map(sort_df.to_dict())
    tidydf_gen = tidydf_gen.sort_values('Total_Sales', ascending= False)
    tidydf_gen = tidydf_gen.reset_index(drop = True)


    if len(list_cat) == 3:
        channel_demog_fig = px.bar(tidydf_gen, x="Channel", y="Sum of Total Purchases", color=demog, barmode="group",color_discrete_map={list_cat[0]:'DarkGreen', list_cat[1]:'wheat', list_cat[2]:'DarkSeaGreen'})
    elif len(list_cat) == 2:
        channel_demog_fig = px.bar(tidydf_gen, x="Channel", y="Sum of Total Purchases", color=demog, barmode="group",color_discrete_map={list_cat[0]:'DarkGreen', list_cat[1]:'wheat'})
    elif len(list_cat) == 1:
        channel_demog_fig = px.bar(tidydf_gen, x="Channel", y="Sum of Total Purchases", color=demog, barmode="group",color_discrete_map={list_cat[0]:'DarkGreen'})

    channel_demog_fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = list(range(len(tidydf_gen.Channel.unique()))),
            ticktext = tidydf_gen.Channel.unique()
        )
    )
    channel_demog_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    channel_demog_fig.update_layout(
        font=dict(
            size=20,
            color="goldenrod"
        )
    )
    channel_demog_fig.update_layout(
        font=dict(
            size=20,
            color="DarkGreen"
        )
    )
    channel_demog_fig.update_layout(legend_title_text=demog_text)



    if len(selected_country) == 1:
        Country = selected_country[0]
        Country_val = df.loc[index,"Total Sales"]
    else:
        Country = "World Sales"
        Country_val = total_sales

    

    income_level = pd.DataFrame(data_selected.groupby('Income_level')['total_sales'].sum())
    income_level['Income_level'] = income_level.index
    Income_level_max = income_level[income_level.total_sales == income_level.total_sales.max()].index[0]
    Income_level_max_val = income_level.max().total_sales

    data_funnel_lev2 = data_selected[data_selected.Income_level == Income_level_max]
    age_level = pd.DataFrame(data_funnel_lev2.groupby('Age_level')['total_sales'].sum())
    age_level['Age_level'] = age_level.index
    Age_level_max = age_level[age_level.total_sales == age_level.total_sales.max()].index[0]
    Age_level_max_val = age_level.max().total_sales

    data_funnel_lev3 = data_funnel_lev2[data_funnel_lev2.Age_level == Age_level_max]
    dependent_level = pd.DataFrame(data_funnel_lev3.groupby('no_dependents')['total_sales'].sum())
    dependent_level['Dependents'] = dependent_level.index
    if Country == 'Mexico':
        dependent_val_max = dependent_level.loc['One','total_sales']    
    else:
        dependent_val_max = dependent_level.loc['One','total_sales'] + dependent_level.loc['Zero','total_sales'] 
    

    data_funnel_lev4 = data_funnel_lev3[data_funnel_lev3.no_dependents.isin(['One','Zero'])]
    marital_level = pd.DataFrame(data_funnel_lev4.groupby('Marital_status')['total_sales'].sum())
    marital_level['Marital_status'] = marital_level.index
    Marital_status_max = marital_level.max().Marital_status
    Marital_status_max_val = marital_level.max().total_sales

    data_funnel_lev5 = data_funnel_lev4[data_funnel_lev4.Marital_status == Marital_status_max]
    wine_meat_val = data_funnel_lev5.WINE.sum() + data_funnel_lev5.MEAT.sum()

    funnel_fig = go.Figure(go.Funnel(
    y = [Country, Income_level_max, Age_level_max, "0 or 1 Dependents", Marital_status_max, "Wine & Meat Sales"],
    x = [int(Country_val), Income_level_max_val, Age_level_max_val, dependent_val_max, Marital_status_max_val, wine_meat_val], textposition = 'inside', textinfo = 'percent initial',
    marker = {"color": ['#8fbc8f', '#a0c295','#b1c79b', '#c2cda1', '#dbd5aa','#f5deb3']}))

    funnel_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    funnel_fig.update_layout(
        font=dict(
            size=20,
            color="goldenrod"
        )
    )
    funnel_fig.update_layout(
        font=dict(
            size=20,
            color="DarkGreen"
        )
    )

    new_bubble_chart_fig = px.scatter_geo(groupby_country[groupby_country['Country'].isin(selected_country)], 
                    locations='Country',
                    color='Country',
                    locationmode='country names', 
                    size='Sales Percent',
                    size_max=50,
                    color_discrete_map={'Spain':'DarkGreen', 'USA':'DarkSeaGreen', 'India':'wheat', 'Saudi Arabia':'crimson', 'Canada':'goldenrod', 'Germany':'Tomato', 'Australia':'lightslategray', 'Mexico':'saddlebrown'},
                    hover_name = 'Country')
    new_bubble_chart_fig.update_layout(
            title_text = 'Total Product Sales by Country (in %)',
            title_x=0.45,
            showlegend = True)
    new_bubble_chart_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    new_bubble_chart_fig.update_layout(
        font=dict(
            size=20,
            color="DarkGreen"
        )
    )


    #return str(restyleData),total_sales,spain_sales,can_sales, sa_sales, ger_sales, aus_sales, ind_sales, usa_sales, mex_sales, 100,spain_sales_perc,can_sales_perc, sa_sales_perc, ger_sales_perc, aus_sales_perc, ind_sales_perc, usa_sales_perc, mex_sales_perc, wine_sales,wine_sales_perc, fruit_sales, fruit_sales_perc, meat_sales,meat_sales_perc, fish_sales, fish_sales_perc, sweets_sales, sweets_sales_perc, gold_sales,gold_sales_perc,sales_demog_fig,demog_text,channel_demog_fig,funnel_fig        
    return new_bubble_chart_fig, wine_sales,wine_sales_perc, fruit_sales, fruit_sales_perc, meat_sales,meat_sales_perc, fish_sales, fish_sales_perc, sweets_sales, sweets_sales_perc, gold_sales,gold_sales_perc,sales_demog_fig,demog_text,channel_demog_fig, funnel_fig                
        
        

    

                

if __name__ == '__main__':
    app.run_server(debug=True)


# #############################################################################