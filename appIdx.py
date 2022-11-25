import dash
import dash_html_components as html
import dash_core_components as dcc

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import datetime

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('qill_MMR_clean.csv', parse_dates=True)
orderM = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
df['month'] = pd.Categorical(df['month'], categories=orderM, ordered=True)
df.sort_values(by='month')

col1 = 'Distance (km)'
col2 = 'Avg Pace (min/km)'

layout = go.Layout(
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(x=0, y=1.1, traceorder='normal', font=dict(size=8,))
    )

# First graph --------------------------------------------------------------
fig1 = go.Figure(layout=layout)
x_y = df.groupby(['month']).sum()[col1]
lab = "Avg. pace:"+df.groupby(['month']).mean()[col2].round(2).astype(str)+"<br>(min/km)"
fig1.add_trace(go.Bar( x=x_y.keys(), y=x_y.values, marker_color='blue',
                     name="Total distance (km)",
                     text=lab.values, #textposition="outside",
                     ))
x_y = df.groupby(['month']).mean()['Calories Burned (kCal)']
fig1.add_trace(go.Scatter(x=x_y.keys(), y=x_y.values,
                    mode='lines+markers', name='Avg. Calories Burned (kCal)'
                    ))
x_y = df.groupby(['month']).count()['Date Submitted'].cumsum()
fig1.add_trace(go.Scatter(x=x_y.keys(), y=x_y.values,
                    mode='lines+markers', name='Accumulate total run'))

# Second graph --------------------------------------------------------------
def find_PB(ranDist_min,ranDist_max,col1,col2):
  df_Xk = df[df[col1].between(ranDist_min, ranDist_max)]
  df_Xk = df_Xk[df_Xk['Workout Time (seconds)']>0]
  Xk_avg = [round(df_Xk[col1].mean(),2),
               str(datetime.timedelta(seconds=int(df_Xk['Workout Time (seconds)'].mean()))),
               round(df_Xk[col2].mean(),2)]
  rowPB_Xk = df_Xk[df_Xk['Workout Time (seconds)'] == df_Xk['Workout Time (seconds)'].min()]
  rowPB_Xk_time = rowPB_Xk['Workout Time (seconds)'].values[0]
  rowPB_Xk_time = str(datetime.timedelta(seconds=float(rowPB_Xk_time)))
  rowPB_Xk_day = pd.to_datetime(rowPB_Xk['Workout Date'].values[0])  
  return [rowPB_Xk_time, Xk_avg[1], (round(rowPB_Xk[col2].values[0],2),Xk_avg[2])]
list_avg = []; list_best = []; list_pace = []
tmp_list = find_PB(5.0,5.2,col1,col2);list_best.append(tmp_list[0]); list_avg.append(tmp_list[1]); list_pace.append(tmp_list[2])
tmp_list = find_PB(10.0,10.2,col1,col2);list_best.append(tmp_list[0]); list_avg.append(tmp_list[1]); list_pace.append(tmp_list[2])
tmp_list = find_PB(21.0,21.2,col1,col2);list_best.append(tmp_list[0]); list_avg.append(tmp_list[1]); list_pace.append(tmp_list[2])
tmp_list = find_PB(30.0,31.0,col1,col2);list_best.append(tmp_list[0]); list_avg.append(tmp_list[1]); list_pace.append(tmp_list[2])
tmp_list = find_PB(35.0,40.0,col1,col2);list_best.append(tmp_list[0]); list_avg.append(tmp_list[1]); list_pace.append(tmp_list[2])
tmp_list = find_PB(40.0,44.0,col1,col2);list_best.append(tmp_list[0]); list_avg.append(tmp_list[1]); list_pace.append(tmp_list[2])
list_avg_fin = []
for i in list_avg:
  a = datetime.datetime.strptime(i, "%H:%M:%S")
  sec = (a - datetime.datetime(1900, 1, 1)).total_seconds()
  list_avg_fin.append((i, sec, list_pace[list_avg.index(i)][1]))
list_best_fin = []
for i in list_best:
  a = datetime.datetime.strptime(i, "%H:%M:%S")
  sec = (a - datetime.datetime(1900, 1, 1)).total_seconds()
  list_best_fin.append((i, sec, list_pace[list_best.index(i)][1]))
fig2 = go.Figure()
xAx = ['5km','10km','21km','30km','38km','40km']; yAx = []
for i in range(0,20000,2000):
  yAx.append(str(datetime.timedelta(seconds=float(i))))
fig2.add_trace(go.Scatter(x=xAx, y=[i[1] for i in list_best_fin], 
                         customdata=[str(i[0])+"<br>Min/Km: "+str(i[2]) for i in list_best_fin],
                         hovertemplate='<br>'.join([                              
                              'Distance: %{x}', 'Time: %{customdata}'
                          ]),name="Best Time", fill='tonexty'))
fig2.add_trace(go.Scatter(x=xAx, y=[i[1] for i in list_avg_fin], 
                         customdata=[str(i[0])+"<br>Min/Km: "+str(i[2]) for i in list_avg_fin],
                         hovertemplate='<br>'.join([                              
                              'Distance: %{x}', 'Time: %{customdata}'
                          ]),name="Avg Time", fill='tonexty'))
fig2.update_layout(
    yaxis = dict(tickmode = 'array', tickvals = [i for i in range(0,20000,2000)],
                 ticktext = yAx),
    hovermode="y"
) 


# Viz dashboard ------------------------------------------------------------

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([

  html.Div([
      dcc.Graph(id='stats-mon',
                figure=fig1
                .update_layout(title='Stats per months', title_x=0.5,
                               hovermode="closest", hoverlabel=dict(
                                     bgcolor="white", font_size=11, font_family="Rockwell"))
                .update_traces(hovertemplate = "%{x}<br>%{y:.2f}<extra></extra>",
                                  textfont_size=10)
                )                
  ], className='twelve columns'),
  
   html.Div([
      dcc.Graph(id='stats-best',
                figure=fig2
                .update_layout(title='Best performance', title_x=0.5,
                               hovermode="closest", hoverlabel=dict(
                                     bgcolor="white", font_size=11, font_family="Rockwell"))
                .update_traces(textfont_size=10)
                ),                
  ], className='twelve columns'),

  html.Div([
      dcc.Graph(id='dist-day',
                figure=go.Figure(data=[go.Pie(labels=df['day'].value_counts().index, 
                             values=df['day'].value_counts().values,
                             textinfo='label+percent', pull=[0.1]                             
                             )])
                .update_layout(title='Distance by day', title_x=0.5,
                               hovermode="closest", hoverlabel=dict(
                                    bgcolor="white", font_size=11, font_family="Rockwell"))
                .update_traces(hovertemplate = '%{label}<br>%{value:.2f} km',
                               marker=dict(line=dict(color='#eff542', width=2)),
                               showlegend=False)
                )                
  ], className='twelve columns'),

  html.Div([
      dcc.Graph(id='dist-year', 
                figure=px.sunburst(df, path=['year','season'], 
                                          values=col1, color='season')
                .update_layout(title='Distance by year and season', title_x=0.5,
                               hovermode="closest", hoverlabel=dict(
                                    bgcolor="white", font_size=11, font_family="Rockwell"))
                .update_traces(hovertemplate = '%{label}<br>%{value:.2f} km')
                )                
  ], className='twelve columns'),

  html.Div([
      dcc.Graph(id='dist-sea', 
                figure=px.sunburst(df, path=['season','month'], 
                                          values=col1, color='month')
                .update_layout(title='Distance by season and month', title_x=0.5,
                               hovermode="closest", hoverlabel=dict(
                                    bgcolor="white", font_size=11, font_family="Rockwell"))
                .update_traces(hovertemplate = '%{label}<br>%{value:.2f} km')
                )                
  ], className='twelve columns')

], className='row')

if __name__ == '__main__':
    app.run_server(debug=True)