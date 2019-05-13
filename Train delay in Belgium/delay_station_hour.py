
#import dependencies
from datetime import datetime, date, timedelta
import pandas as pd
import folium

#Dataframe with columns station, latitude, longitude
df_station_geo = pd.read_excel(r'C:\Users\Yves Vc\Desktop\NMBS Data\station_geo_update.xlsx')

#Dataframe with columns Expected time of expected arrival, true time of arrival, station of arrival 
df_station_delay = pd.read_excel(r'C:\Users\Yves Vc\Desktop\NMBS Data\stipt\20190508.xlsx')

#Create map with point-of-center Brussels
map = folium.Map(location=[50.8503, 4.3517],
                        zoom_start=8)


'''
Based on the df_station_geo and df_station_delay tables, 
the delay (true time of arrival - expected time of arrival) per station for a specified hour-interval is shown

Input: 
- Dataframe with columns station, latitude, longitude
- Dataframe with columns Expected time of expected arrival, true time of arrival, station of arrival
- Hour-interval

Output: Dataframe with delay (true time of arrival - expected time of arrival) per station for the specified hour-interval,
as well as a colour that indicates the severity of the delay
'''

def show_station_delay_per_hour(df_station_geo, df_station_delay, hour):
    df_station_geo_delay = pd.merge(df_station_geo,df_station_delay, how = 'inner', left_on = 'station', right_on = 'Naam van de halte')[['lat', 'len','Uur van geplande aankomst','Uur van reële aankomst', 'Naam van de halte' ]]
    df_station_geo_delay = df_station_geo_delay[df_station_geo_delay['Uur van geplande aankomst'].str.slice(start=0,stop=2) == str(hour)]
    df_station_geo_delay['Uur van geplande aankomst'] = pd.to_datetime(df_station_geo_delay['Uur van geplande aankomst'])
    df_station_geo_delay['Uur van reële aankomst'] = pd.to_datetime(df_station_geo_delay['Uur van reële aankomst'])
    df_station_geo_delay['difference time'] = df_station_geo_delay['Uur van reële aankomst'] - df_station_geo_delay['Uur van geplande aankomst']
    
    t = datetime.strptime("00:00:00","%H:%M:%S")
    delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    df_station_geo_delay = df_station_geo_delay[df_station_geo_delay['difference time'] > delta]
    df_station_geo_delay_hour = df_station_geo_delay.groupby(['Naam van de halte', 'lat', 'len'])['difference time'].sum()
    df_station_geo_delay_hour = df_station_geo_delay_hour.reset_index(level = ['Naam van de halte', 'lat', 'len'])
    df_station_geo_delay_hour['difference colour'] = df_station_geo_delay_hour['difference time'].map(lambda x: '#ff0000' if x.total_seconds() > 7200 else 
                                                         ('#ff4000' if x.total_seconds() > 5400 else
                                                          ('#ff8000' if x.total_seconds() > 3600 else 
                                                           ('#ffbf00' if x.total_seconds() > 1800 else
                                                             ('#ffff00' if x.total_seconds() > 900 else
                                                              ('#80ff00' if x.total_seconds() > 300 else '#40ff00'))))))
    return df_station_geo_delay_hour



'''
Visualization of the delay per station for a specified hour-interval on a map

Input: 
- Folium map
- Dataframe with delay (true time of arrival - expected time of arrival) per station for the specified hour-interval,
as well as a colour that indicates the severity of the delay
- Hour-interval

Output: Map showing the delay per station , represented by a colour from green to red, for a specified hour
'''

def viz_delay_on_map(map,df_station_geo_delay_hour, hour):
    df_station_geo_delay_hour = df_station_geo_delay_hour[['lat', 'len', 'difference colour', 'Naam van de halte']]
    for index,row in dataframe_lat_len.iterrows():
        folium.CircleMarker(location=[row[0], row[1]],fill=True, radius = 2, color = row[2], popup = row[3]).add_to(map)
    legend =   '''
                <div style="position: fixed; 
                            bottom: 65px; left: 50px; width: 100px; height: 180px; 
                            border:2px solid grey; z-index:9999; font-size:14px;
                            ">&nbsp; Delay (min) <br>
                              &nbsp; >120 &nbsp; <i class="fa fa-circle" style="color:#ff0000"></i><br>
                              &nbsp; >90 &nbsp &nbsp; <i class="fa fa-circle" style="color:#ff4000"></i><br>
                              &nbsp; >60 &nbsp &nbsp; <i class="fa fa-circle" style="color:#ff8000"></i><br>
                              &nbsp; >30 &nbsp &nbsp; <i class="fa fa-circle" style="color:#ffbf00"></i><br>
                              &nbsp; >15 &nbsp &nbsp; <i class="fa fa-circle" style="color:#ffff00"></i><br>
                              &nbsp; >5  &nbsp &nbsp &nbsp; <i class="fa fa-circle" style="color:#80ff00"></i><br>
                              &nbsp; <5  &nbsp &nbsp &nbsp; <i class="fa fa-circle" style="color:#40ff00"></i><br>
                </div>
                ''' 
    time =  '''
                <div style="position: fixed; 
                            top: 100px; left: 75px; width: 100px; height: 15px; 
                            z-index:9999; font-size:25px;
                            ">''' + hour + ''' 
                </div>
                ''' 
    map.get_root().html.add_child(folium.Element(legend))
    map.get_root().html.add_child(folium.Element(time))
    return map
