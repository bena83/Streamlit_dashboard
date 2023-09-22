import streamlit as st
import json
import pandas as pd
import numpy as np
from millify import millify
from streamlit_echarts import Map
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Dashboard", layout ="wide")

@st.cache
def load_csv():
    df = pd.read_excel('Sample - Superstore.xls')
    df['Order Date']= pd.to_datetime(df['Order Date']).dt.strftime('%d-%b-%Y')
    df['year']= pd.to_datetime(df['Order Date']).dt.strftime('%Y')
    df['month']= pd.to_datetime(df['Order Date']).dt.strftime('%b')
    return df 

df = load_csv()

# SideBar
st.sidebar.header("Choose your filter:")
region=st.sidebar.multiselect("pick your Region",df["Region"].unique())
if not region:
    df2=df.copy()
else:
    df2=df[df["Region"].isin(region)]

#state
state=st.sidebar.multiselect("pick the state",df2["State"].unique())
if not state:
    df3=df2.copy()
else:
    df3=df2[df2["State"].isin(state)]

#City
city=st.sidebar.multiselect("pick the City",df3["City"].unique())

#filter the data based on region , state and city
if not region and not state and not city:
    filtered_df=df
elif not state and not city:
    filtered_df=df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df=df[df["State"].isin(state)]
elif state and city:
    filtered_df=df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df=df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df=df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df=df3[df3["City"].isin(city)]
else:
    filtered_df=df3[df3["Region"].isin(region)&df3["State"].isin(state) & df3["City"].isin(city)]



df_selection = df3.query('Region==@region & State==@state')

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.image("1.png", width=60)
    st.metric("Sales", millify(df_selection.Sales.sum(), precision=2))
with col2:
    st.image("2.png", width=60)
    st.metric("Orders", millify(df_selection['Order ID'].nunique(), precision=2))
with col3:
    st.image("3.png", width=60)
    st.metric("Profit", millify(df_selection['Profit'].sum(), precision=2))
with col4:
    st.image("4.png", width=60)
    st.metric("Products", millify(df_selection['Product ID'].nunique(), precision=2))

cols1,cols2= st.columns([2,2])
with cols1:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    df_selection['month'] = pd.Categorical(df_selection['month'], categories=months, ordered=True)
    a = df_selection.groupby(['year','month'])['Order ID'].nunique().unstack()

    lines = []
    line = {}


    for i in a.index:
        line["name"] = i
        line["type"] = 'line'
        line["smooth"] = 'True'
        line["data"] = a.loc[i, :].values.tolist()
        lines.append(line.copy())
        
    option = {
        'title': {
        'text': 'Orders per month'
    },
    'tooltip': {
        'trigger': 'axis'
    },
    'legend': {
        'data': a.index.tolist(),
        'orient': 'vertical',
        'right': '3%',
        'top':'10%'
    },
    'grid': {
        'left': '0%',
        'right': '15%',
        'bottom': '3%',
        'containLabel': True
    },
        "xAxis": {
        "type": 'category',
        "data": ['Jan', 'Feb', 'Mar', 'May', 'Apr', 'Jun', 'Jul','Aug','Sep','Oct','Nov','Dec']
        },
        "yAxis": {
        "type": 'value'
        },
        "series": lines
        }
    st_echarts(options=option, key="chart")

with cols2:
    df_selection['month'] = pd.Categorical(df_selection['month'], categories=months, ordered=True)
    a = df_selection.groupby(['year','month'])['Profit'].sum().unstack()

    lines = []
    line = {}

    for i in a.index:
        line["name"] = i
        line["type"] = 'bar'
        line["stack"] = 'total'
        line["data"] = a.loc[i, :].values.tolist()
        lines.append(line.copy())
    
    option = {
    'title': {
    'text': 'Profit per month'
    },
  'tooltip': {
    'trigger': 'axis'
  },
  'legend': {
    'data': a.index.tolist(),
    'orient': 'vertical',
        'right': '3%',
        'top':'10%'
  },
  'grid': {
    'left': '0%',
    'right': '15%',
    'bottom': '3%',
    'containLabel': True
  },
    "xAxis": {
    "type": 'category',
    "data": ['Jan', 'Feb', 'Mar', 'May', 'Apr', 'Jun', 'Jul','Aug','Sep','Oct','Nov','Dec']
    },
    "yAxis": {
    "type": 'value'
    },
    "series": lines
    }
    st_echarts(options=option,key="chart1")   

cols1,cols2= st.columns([2,2])
with cols1:
    prf_state = df_selection.groupby(['State'])['Order ID'].nunique().reset_index()  
    prf_state.rename(columns = {'State':'name', 'Order ID':'value'}, inplace = True)          
    #st.bar_chart(prf_state)

    #fig = px.bar(prf_state, x='State', y='Profit',color='year',
    #            labels={'pop':'population of Canada'},width=900)
    #st.plotly_chart(fig)

    with open("./USA.json", "r") as f:
        map = Map(
            "USA",
            json.loads(f.read()),
            {
                "Alaska": {"left": -131, "top": 25, "width": 15},
                "Hawaii": {"left": -110, "top": 28, "width": 5},
                "Puerto Rico": {"left": -76, "top": 26, "width": 2},
            },
        )
    opt = {
    "title": {
      "text": 'Orders per State',
      "left": '5%'
    },
    "tooltip": {
      "trigger": 'item',
      "showDelay": 0,
      "transitionDuration": 0.2
    },
    "visualMap": {
      "left": 'right',
      "inRange": {
        "color": [
          '#313695',
          '#4575b4',
          '#74add1',
          '#abd9e9',
          '#e0f3f8',
          '#ffffbf',
          '#fee090',
          '#fdae61',
          '#f46d43',
          '#d73027',
          '#a50026'
        ]
      },
      "text": ['High', 'Low'],
      "calculable": True
    },
    "toolbox": {
      "show": True,
      "orient": 'horizontal',
      "right": 'right',
      "top": 'top',
      "feature": {
        "dataView": { "readOnly": False },
        "restore": {},
        "saveAsImage": {}
      }
    },
    "series": [
      {
        "name": 'USA PopEstimates',
        "type": 'map',
        "map": 'USA',
        "emphasis": {
          "label": {
            "show": True
          }
        },
    "data":prf_state.to_dict('records')}
     ],
    }
    st_echarts(options=opt,map=map,width="300",key="chart6")

with cols2:
    counts  = df_selection.groupby('Sub-Category')['Order ID'].nunique().reset_index()
    counts.rename(columns = {'Sub-Category':'name', 'Order ID':'value'}, inplace = True)

    option = {
    "title": {
      "text": 'Orders Per sub category',
      "left": '5%'
    },
    'grid': {'left':"25%", 'right':"10%"},
    'xAxis': {
        'type': 'category',
        'data':counts.name.tolist(),
        'axisLabel': {
        'show': True,
        'interval': 0,
        'rotate': 90
      }
     },
    'yAxis': {
        'type': 'value',
        "show" :False     
    },
    'series': [
    {
      'data': counts.value.to_list(),
      'type': 'bar',
       'label': {
        'position': 'top',
        'show': True
      },
      'showBackground': True,
      'backgroundStyle': {
        'color': 'rgba(180, 180, 180, 0.2)'
      }
    }
    ]
    }
    st_echarts(options=option,key="chart7")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css?family=Open+Sans');
div[data-testid="metric-container"] {
  margin: 0px auto;
  max-width: 300px;
  border-radius: 10px;
  border-width: 1px;
  border-style: solid;
  border-color="#777";
  overflow: hidden;
  background-clip: padding-box;
  padding: 15px 5px 15px 40%;
  text-align: left;
  font-weight: 400 !important;
  font-family: Open sans;
  color: #black;
  
}


}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
    font-family: Open sans;
    font-size:calc(1.2875rem + 0.45vw);
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: red;
}
.css-1gj6jmv{
  background-clip: padding-box;
  padding: 30px 15px;
  border-radius: 10px;
    background-color: #fff;
}

.css-1adrfps{
    width: 17rem;
    background-color: #fff;
    border-radius: 0.5rem;
}
.css-1siy2j7{
    width: 17rem;
    background-color: #fff;
    border-radius: 0.5rem;
}
.css-18e3th9 {
    background-color: #f5f5f9;
    padding-left: 1rem;
    padding-right: 1rem;
    padding: 3rem 1rem 3rem;
}
.e8zbici2{
    top: -50px;
}

.css-1kyxreq {
  padding-left: 50PX;
}

.css-1adrfps{
    padding-top: 50PX;
}

.css-1gx893w{
    top:-45px;
}

.css-6awftf ~ .css-1kyxreq {  position: absolute;
    top: 35px;
    left: -35px;}

</style>
"""
, unsafe_allow_html=True)
