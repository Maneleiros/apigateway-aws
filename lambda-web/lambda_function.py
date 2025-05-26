import json
import urllib.request

def lambda_handler(event, context):
    try:
        # URL de la API que quieres consultar
        api_key = "fcdd45f6-c8b0-4a7a-b99d-3dac4e7eb813"
        url = f"https://api.openchargemap.io/v3/poi/?output=json&countrycode=ES&maxresults=5&compact=true&verbose=false&key={api_key}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise Exception(f"Error en la solicitud. Código de estado: {response.status}")
            data = json.loads(response.read().decode())
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # Permite solicitudes desde cualquier origen
                'Content-Type': 'application/json',
            },
            'body': json.dumps(data)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
