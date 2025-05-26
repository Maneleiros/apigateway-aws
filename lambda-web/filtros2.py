import json
import urllib.request
import math

def lambda_handler(event, context):
    try:
        # Lista de capitales de provincia con coordenadas (puedes ampliar)
        capitals = [
            {"name": "Madrid", "lat": 40.4168, "lon": -3.7038},
            {"name": "Barcelona", "lat": 41.3874, "lon": 2.1686},
            {"name": "Valencia", "lat": 39.4699, "lon": -0.3763},
            {"name": "Sevilla", "lat": 37.3891, "lon": -5.9845},
            {"name": "Zaragoza", "lat": 41.6488, "lon": -0.8891},
            {"name": "Bilbao", "lat": 43.2630, "lon": -2.9350},
            {"name": "Málaga", "lat": 36.7213, "lon": -4.4214},
            {"name": "A Coruña", "lat": 43.3623, "lon": -8.4115},
            {"name": "Granada", "lat": 37.1773, "lon": -3.5986}
        ]

        # Obtener datos de OpenChargeMap
        api_key = "fcdd45f6-c8b0-4a7a-b99d-3dac4e7eb813"
        url = f"https://api.openchargemap.io/v3/poi/?output=json&countrycode=ES&maxresults=100&compact=true&verbose=false&key={api_key}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        # Preparar estaciones
        station_js_array = ""
        types = set()

        for station in data:
            info = station.get("AddressInfo", {})
            connections = station.get("Connections", [])
            lat = info.get("Latitude")
            lon = info.get("Longitude")
            title = info.get("Title", "Sin título")
            town = info.get("Town", "Desconocido")
            conn_types = [conn.get("ConnectionType", {}).get("Title", "Desconocido") for conn in connections]

            if lat and lon:
                for ct in conn_types:
                    types.add(ct)

                # Escape strings
                title = title.replace('"', '\\"')
                town = town.replace('"', '\\"')
                conn_types_str = ', '.join(ct.replace('"', '\\"') for ct in conn_types)

                station_js_array += f'''{{ 
                    lat: {lat}, 
                    lon: {lon}, 
                    title: "{title}", 
                    town: "{town}", 
                    type: "{conn_types_str}" 
                }},\n'''

        type_options = ''.join(f'<option value="{t}">{t}</option>' for t in sorted(types))
        capital_options = ''.join(f'<option value="{c["name"]}">{c["name"]}</option>' for c in capitals)

        # HTML
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
            
            <label for="capitalFilter">Selecciona una capital:</label>
            <select id="capitalFilter">
                <option value="">-- Elegir capital --</option>
                {capital_options}
            </select>

            <label for="typeFilter">Filtrar por tipo de cargador:</label>
            <select id="typeFilter">
                <option value="">Todos</option>
                {type_options}
            </select>

            <div id="map"></div>
            <ul id="stations"></ul>

            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                const stations = [{station_js_array}];

                const capitals = {{
                    {", ".join(f'"{c["name"]}": {{ lat: {c["lat"]}, lon: {c["lon"]} }}' for c in capitals)}
                }};

                let map = L.map('map').setView([40.4168, -3.7038], 6);
                let markers = [];

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap contributors'
                }}).addTo(map);

                function haversine(lat1, lon1, lat2, lon2) {{
                    const R = 6371;
                    const dLat = (lat2 - lat1) * Math.PI / 180;
                    const dLon = (lon2 - lon1) * Math.PI / 180;
                    const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * 
                              Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
                    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                }}

                function clearMarkers() {{
                    markers.forEach(m => map.removeLayer(m));
                    markers = [];
                }}

                function renderStations(capitalName, typeFilter) {{
                    const ref = capitals[capitalName];
                    if (!ref) return;

                    const list = document.getElementById("stations");
                    list.innerHTML = "";
                    clearMarkers();

                    // Ordenar por distancia
                    const sorted = stations
                        .map(st => {{
                            return {{ ...st, distance: haversine(ref.lat, ref.lon, st.lat, st.lon) }};
                        }})
                        .sort((a, b) => a.distance - b.distance)
                        .filter(st => !typeFilter || st.type.includes(typeFilter))
                        .slice(0, 10);  // Mostrar solo las 10 más cercanas

                    map.setView([ref.lat, ref.lon], 9);

                    sorted.forEach(st => {{
                        const marker = L.marker([st.lat, st.lon])
                            .addTo(map)
                            .bindPopup(`<strong>${{st.title}}</strong><br>${{st.town}}<br><small>${{st.type}}</small>`);
                        markers.push(marker);

                        const item = document.createElement("li");
                        item.textContent = `${{st.title}} - ${{st.town}}`;
                        list.appendChild(item);
                    }});
                }}

                document.getElementById("capitalFilter").addEventListener("change", () => {{
                    const capital = document.getElementById("capitalFilter").value;
                    const type = document.getElementById("typeFilter").value;
                    renderStations(capital, type);
                }});

                document.getElementById("typeFilter").addEventListener("change", () => {{
                    const capital = document.getElementById("capitalFilter").value;
                    const type = document.getElementById("typeFilter").value;
                    if (capital) {{
                        renderStations(capital, type);
                    }}
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
            'body': json.dumps({'error': str(e)})
        }
