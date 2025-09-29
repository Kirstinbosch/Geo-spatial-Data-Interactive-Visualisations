Spanish Wildfires Dashboard (2013–2023)

This repository contains an interactive dashboard that visualizes wildfires across Spain between 2013 and 2023.
The dashboard is built with Python, Plotly Dash, and GeoPandas, and it integrates multiple geo-spatial and statistical visualizations to provide insights into wildfire patterns, causes, and regional impacts over the decade.

🌍 *Purpose*

This project was created to explore the spatial and temporal distribution of wildfires in Spain and to illustrate how interactive geo-spatial dashboards can support storytelling and analysis of environmental data.

📂 *Data*

The dashboard uses two main datasets:

(1)fires-all 2.csv – aggregated wildfire data by autonomous communities.
(2)fires-all-more.csv – detailed fire event records with latitude/longitude and causes.
Additionally, a GeoJSON file (georef-spain-comunidad-autonoma.geojson) is required to display regional boundaries.
___________________________________________________________________


▶️ *Running the Dashboard*

Installation & Setup

To run this dashboard locally, follow these steps:

1. Clone the repository

git clone https://github.com/kirstincathlin/spanish-wildfires-dashboard.git
cd spanish-wildfires-dashboard


Create a virtual environment (optional but recommended)

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate


Install the required dependencies

pip install -r requirements.txt


Run the Dash app

python dash_board.py


Open the dashboard in your browser
Once the app is running, open http://127.0.0.1:8050/
to explore the interactive visualizations.


👉 Open that URL in your browser to interact with the dashboard.

