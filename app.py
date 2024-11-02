from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/datos', methods=['POST'])
def recibir_datos():
    # Recibir y decodificar el JSON de la solicitud
    data = request.json
    
    # Validar que se recibieron los datos correctos
    if not data:
        return jsonify({"status": "error", "message": "No se recibieron datos"}), 400

    # Extraer los datos del JSON
    device_id = data.get("device_id")
    velocidad = data.get("velocidad")
    temperatura = data.get("temperatura")
    presion = data.get("presion")
    combustible = data.get("combustible")
    
    # Imprimir los datos en la consola (puedes procesarlos según tus necesidades)
    print(f"Dispositivo ID: {device_id}")
    print(f"Velocidad: {velocidad} km/h")
    print(f"Temperatura: {temperatura} °C")
    print(f"Presión de Llantas: {presion} PSI")
    print(f"Combustible: {combustible} %")
    print("-------------------------------")
    
    # Responder al ESP32 que los datos se recibieron correctamente
    return jsonify({"status": "success", "message": "Datos recibidos exitosamente"})

if __name__ == '__main__':
    # Iniciar el servidor en el puerto 5000 (ajusta el puerto según sea necesario)
    app.run(host='0.0.0.0', port=5000)
