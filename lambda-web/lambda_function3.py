def lambda_handler(event, context):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Estaciones de carga</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            #map {
                height: 500px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>Estaciones de carga</h1>
        <div id="map"></div>
        <ul id="stations"></ul>

        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            // Inicializamos el mapa centrado en España
            const map = L.map('map').setView([40.4168, -3.7038], 6); // Coordenadas de Madrid

            // Añadimos una capa base de OpenStreetMap
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            // Obtener estaciones desde el endpoint
            fetch("https://k4i0atfjxj.execute-api.us-east-1.amazonaws.com/prod/stations")
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById("stations");

                    data.forEach(station => {
                        const info = station.AddressInfo;
                        
                        // Crear lista
                        const item = document.createElement("li");
                        item.textContent = info.Title + " - " + info.Town;
                        list.appendChild(item);

                        // Crear marcador en el mapa
                        if (info.Latitude && info.Longitude) {
                            L.marker([info.Latitude, info.Longitude])
                                .addTo(map)
                                .bindPopup(`<strong>${info.Title}</strong><br>${info.Town}`);
                        }
                    });
                })
                .catch(err => console.error("Error:", err));
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
