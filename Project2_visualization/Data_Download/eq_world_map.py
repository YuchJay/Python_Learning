import plotly.express as px
from eq_explore_data import lons, lats, titles, mags
import pandas as pd

data = pd.DataFrame(
    data=zip(lons, lats, titles, mags), columns=['Longitude', 'Latitude', 'Location', 'Magnitude']
)
data.head()

fig = px.scatter(
    data,
    x='Longitude',
    y='Latitude',
    range_x=[-200, 200],
    range_y=[-90, 90],
    width=800,
    height=800,
    title='Global Earthquakes',
    size='Magnitude',
    size_max=10,
    color='Magnitude',
    hover_name='Location',
)
fig.write_html('Data_Download/eq_world_map.html')
