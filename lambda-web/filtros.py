import json
import urllib.request

def lambda_handler(event, context):
    try:
        # 1. Obtener datos desde Open Charge Map
        api_key = "fcdd45f6-c8b0-4a7a-b99d-3dac4e7eb813"
        url = f"https://api.openchargemap.io/v3/poi/?output=json&countrycode=ES&maxresults=100&compact=true&verbose=false&key={api_key}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        # 2. Preparar datos JS y sets para los filtros
        station_js_array = ""
        towns = set()
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
                towns.add(town)
                for ct in conn_types:
                    types.add(ct)

                # Escapar strings
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

        # Opciones para los selects
        town_options = ''.join(f'<option value="{t}">{t}</option>' for t in sorted(towns))
        type_options = ''.join(f'<option value="{t}">{t}</option>' for t in sorted(types))

        # 3. HTML completo con filtros
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
            
            <label for="townFilter">Filtrar por ciudad:</label>
            <select id="townFilter">
                <option value="">Todas</option>
                {town_options}
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
                let map = L.map('map').setView([40.4168, -3.7038], 6);
                let markers = [];

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap contributors'
                }}).addTo(map);

                function clearMarkers() {{
                    markers.forEach(m => map.removeLayer(m));
                    markers = [];
                }}

                function renderStations(filterTown = "", filterType = "") {{
                    const list = document.getElementById("stations");
                    list.innerHTML = "";
                    clearMarkers();

                    stations.forEach(station => {{
                        const matchesTown = !filterTown || station.town === filterTown;
                        const matchesType = !filterType || station.type.includes(filterType);

                        if (matchesTown && matchesType) {{
                            const marker = L.marker([station.lat, station.lon])
                                .addTo(map)
                                .bindPopup(`<strong>${{station.title}}</strong><br>${{station.town}}`);
                            markers.push(marker);

                            const item = document.createElement("li");
                            item.textContent = `${{station.title}} - ${{station.town}}`;
                            list.appendChild(item);
                        }}
                    }});
                }}

                // Inicial
                renderStations();

                // Filtros
                document.getElementById("townFilter").addEventListener("change", (e) => {{
                    const selectedTown = e.target.value;
                    const selectedType = document.getElementById("typeFilter").value;
                    renderStations(selectedTown, selectedType);
                }});

                document.getElementById("typeFilter").addEventListener("change", (e) => {{
                    const selectedType = e.target.value;
                    const selectedTown = document.getElementById("townFilter").value;
                    renderStations(selectedTown, selectedType);
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
