import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# ------------------------
# Load aggregated wildfire data
# ------------------------
df_region = pd.read_csv('fires-all 2.csv', sep=';', skiprows=1)
df_region['Date'] = pd.to_datetime(df_region['Date'], errors='coerce')
df_region['Year'] = df_region['Date'].dt.year
df_region['superficie'] = pd.to_numeric(df_region['superficie'], errors='coerce')

id_mapping = {
    1: "Andalucía", 2: "Aragón", 3: "Principado de Asturias", 4: "Illes Balears",
    5: "Canarias", 6: "Cantabria", 7: "Castilla y León", 8: "Castilla-La Mancha",
    9: "Cataluña", 10: "Comunitat Valenciana", 11: "Extremadura", 12: "Galicia",
    13: "Comunidad de Madrid", 14: "Región de Murcia", 15: "Comunidad Foral de Navarra",
    16: "País Vasco", 17: "La Rioja", 18: "Ciudad Autónoma de Ceuta", 19: "Ciudad Autónoma de Melilla",
}
df_region['region_name'] = df_region['idcomunidad'].map(id_mapping)

# ------------------------
# Load individual fires data
# ------------------------
df_fires = pd.read_csv('fires-all-more.csv', sep=';')
df_fires['fecha'] = pd.to_datetime(df_fires['fecha'], errors='coerce')
df_fires['Year'] = df_fires['fecha'].dt.year

cause_map = {
    1: "Lightning",
    2: "Accident or Negligence",
    3: "Accident or Negligence",
    4: "Intentional Fire",
    5: "Unknown",
    6: "Reproduced Fire"
}
df_fires['cause_desc'] = df_fires['causa'].map(cause_map)
df_fires = df_fires.dropna(subset=['lat','lng','superficie'])
df_fires['size_scaled'] = df_fires['superficie'].apply(lambda x: x**0.5)

# ------------------------
# Load Spain GeoJSON
# ------------------------
spain_geo = gpd.read_file('georef-spain-comunidad-autonoma.geojson')

# ------------------------
# Initialize Dash App
# ------------------------
app = Dash(__name__)
app.title = "Spanish Wildfires Dashboard"

years = sorted(df_region['Year'].dropna().unique())
causes = df_fires['cause_desc'].dropna().unique()

# ------------------------
# Layout
# ------------------------
app.layout = html.Div([
    html.H1("Wildfires in Spain (2013-2023)", style={'textAlign':'center'}),
    
    html.Label("Select Year:"),
    dcc.Slider(
        id='year-slider',
        min=int(years[0]),
        max=int(years[-1]),
        step=1,
        value=int(years[-1]),
        marks={int(y): str(int(y)) for y in years},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    
    # First row: Map, Bar chart, Line chart
    html.Div([
        dcc.Graph(id='choropleth', style={'height':'600px'}),
        dcc.Graph(id='bar-chart', style={'height':'500px', 'marginTop':'40px'}),
        dcc.Graph(id='line-chart', style={'height':'400px', 'marginTop':'40px'})
    ], style={'display':'grid', 'gridTemplateColumns':'1fr 1fr', 'gridGap':'20px', 'padding':'20px'}),
    
    # Cause filter above scatter + stacked area
    html.Div([
        html.Label("Filter by Cause:"),
        dcc.Dropdown(
            id='cause-dropdown',
            options=[{'label': c, 'value': c} for c in causes],
            value=list(causes),
            multi=True
        )
    ], style={'width':'50%', 'margin':'auto', 'marginTop':'40px'}),
    
    # Scatter and stacked area chart
    html.Div([
        dcc.Graph(id='scatter-plot', style={'height':'500px'}),
        dcc.Graph(id='area-chart', style={'height':'500px', 'marginTop':'40px'})
    ], style={'display':'grid', 'gridTemplateColumns':'1fr 1fr', 'gridGap':'20px', 'padding':'20px'})
])

# ------------------------
# Callbacks
# ------------------------
@app.callback(
    Output('choropleth', 'figure'),
    Output('bar-chart', 'figure'),
    Output('line-chart', 'figure'),
    Output('scatter-plot', 'figure'),
    Output('area-chart', 'figure'),
    Input('year-slider', 'value'),
    Input('cause-dropdown', 'value')
)
def update_charts(selected_year, selected_causes):
    # -------- Choropleth --------
    df_cum = df_region[df_region['Year'] <= selected_year]
    df_cum = df_cum.groupby(['idcomunidad','region_name'])['superficie'].sum().reset_index()
    
    merge = spain_geo.merge(df_cum, left_on='acom_name', right_on='region_name', how='left')
    merge['superficie'] = merge['superficie'].fillna(0)
    merge['id'] = merge.index.astype(int)
    
    fig_map = px.choropleth_mapbox(
        merge,
        geojson=merge.set_index('id')['geometry'].__geo_interface__,
        locations='id',
        color='superficie',
        hover_name='region_name',
        color_continuous_scale='OrRd',
        mapbox_style='carto-darkmatter',
        center={"lat": 40, "lon": -4},
        zoom=4.5,
        title=f"Cumulative Burned Area up to {selected_year}"
    )
    fig_map.update_traces(hovertemplate="<b>%{hovertext}</b><br>Burned Area: %{z:,.0f} ha")
    fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, coloraxis_colorbar=dict(title="ha"))

    # -------- Bar Chart --------
    fig_bar = px.bar(
        df_cum.sort_values('superficie', ascending=False),
        x='region_name',
        y='superficie',
        color='superficie',
        color_continuous_scale='OrRd',
        title=f"Cumulative Burned Area by Region up to {selected_year}",
        labels={'region_name': 'Region', 'superficie': 'Burned Area (ha)'}
    )
    fig_bar.update_layout(xaxis_tickangle=-45, margin={"r":20,"t":40,"l":40,"b":150})
    fig_bar.update_traces(hovertemplate='Region: %{x}<br>Burned Area: %{y:,.0f} ha')

    # -------- Line Chart --------
    df_line = df_region.groupby('Year')['superficie'].sum().cumsum().reset_index()
    fig_line = px.line(df_line, x='Year', y='superficie', markers=True,
                       title="Cumulative Burned Area Over Time")
    fig_line.add_vline(x=selected_year, line_dash="dash", line_color="red")
    fig_line.update_layout(yaxis_title="Cumulative Burned Area (ha)", margin={"r":20,"t":40,"l":40,"b":40}, xaxis=dict(dtick=1))
    fig_line.update_traces(hovertemplate='Year: %{x}<br>Cumulative Burned Area: %{y:,.0f} ha')

    # -------- Scatter Plot --------
    df_scatter = df_fires[(df_fires['Year'] <= selected_year) & (df_fires['cause_desc'].isin(selected_causes))]
    fig_scatter = px.scatter_mapbox(
        df_scatter,
        lat='lat', lon='lng',
        color='cause_desc', size='size_scaled', size_max=15,
        hover_name='municipio',
        hover_data={'superficie': True, 'Year': True, 'cause_desc': True, 'size_scaled': False},
        mapbox_style='carto-darkmatter',
        zoom=4.5,
        title="Individual Wildfires",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_scatter.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, legend_title_text="Cause")
    
      # -------- Stacked Area Chart --------
    df_area = df_fires[(df_fires['Year'] <= selected_year) & (df_fires['cause_desc'].isin(selected_causes))]
    df_area_grouped = df_area.groupby(['Year', 'cause_desc'])['superficie'].sum().reset_index()

    fig_area = px.area(
        df_area_grouped,
        x='Year',
        y='superficie',
        color='cause_desc',
        title="Burned Area by Cause Over Time",
        labels={'superficie':'Burned Area (ha)', 'cause_desc':'Cause'}
    )
    fig_area.add_vline(x=selected_year, line_dash="dash", line_color="red")
    fig_area.update_layout(
        margin={"r":20,"t":50,"l":40,"b":40},
        xaxis=dict(dtick=1)
    )
    fig_area.update_traces(hovertemplate='Year: %{x}<br>Cause: %{legendgroup}<br>Burned Area: %{y:,.0f} ha')

    return fig_map, fig_bar, fig_line, fig_scatter, fig_area

if __name__ == '__main__':
    app.run(debug=True)


