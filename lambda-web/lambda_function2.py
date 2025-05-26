def lambda_handler(event, context):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Estaciones de carga</title>
    </head>
    <body>
        <h1> Estaciones de carga </h1>
        <ul id="stations"></ul>
        <script>
            fetch("https://k4i0atfjxj.execute-api.us-east-1.amazonaws.com/prod/stations")
                .then(res => res.json())
                .then(data => {
                    const list = document.getElementById("stations");
                    data.forEach(station => {
                        const item = document.createElement("li");
                        item.textContent = station.AddressInfo.Title + " - " + station.AddressInfo.Town;
                        list.appendChild(item);
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
