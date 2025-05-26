import json
import urllib.request

def lambda_handler(event, context):
    try:
        # 1. Obtener datos desde Open Charge Map
        api_key = "fcdd45f6-c8b0-4a7a-b99d-3dac4e7eb813"
        url = f"https://api.openchargemap.io/v3/poi/?output=json&countrycode=ES&maxresults=10&compact=true&verbose=false&key={api_key}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        # 2. Preparar los puntos como datos JS embebidos
        station_js_array = ""
        for station in data:
            info = station.get("AddressInfo", {})
            lat = info.get("Latitude")
            lon = info.get("Longitude")
            title = info.get("Title", "Sin título")
            town = info.get("Town", "Desconocido")
            if lat and lon:
                # Escape de comillas dobles por seguridad
                title = title.replace('"', '\\"')
                town = town.replace('"', '\\"')
                station_js_array += f'{{ lat: {lat}, lon: {lon}, title: "{title}", town: "{town}" }},\n'

        # 3. HTML con Leaflet y los puntos directamente incrustados
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Estaciones de carga</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <style>
                #map {{
                    height: 500px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <h1>Estaciones de carga</h1>
            <div id="map"></div>
            <ul id="stations"></ul>

            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                const stations = [{station_js_array}];

                const map = L.map('map').setView([40.4168, -3.7038], 6); // Centro: Madrid

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap contributors'
                }}).addTo(map);

                const list = document.getElementById("stations");

                stations.forEach(station => {{
                    const marker = L.marker([station.lat, station.lon])
                        .addTo(map)
                        .bindPopup(`<strong>${{station.title}}</strong><br>${{station.town}}`);

                    const item = document.createElement("li");
                    item.textContent = `${{station.title}} - ${{station.town}}`;
                    list.appendChild(item);
                }});
            </script>
        </body>
        </html>
        """

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': html
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
