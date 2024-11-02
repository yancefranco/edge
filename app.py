from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)

# Configuración de la base de datos MySQL en Railway
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:bFJBORbZWNCMBRdUkCQhPUshiFxeAuGm@autorack.proxy.rlwy.net:51546/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# URL del backend central
CENTRAL_BACKEND_URL = 'https://backendcentral.onrender.com/api/v1/recibir_datos'

# Definir el modelo de la base de datos para guardar los datos de los sensores
class SensorData(db.Model):
    __tablename__ = 'sensores'
    device_id = db.Column(db.String(50), primary_key=True)  # ID único del dispositivo
    velocidad = db.Column(db.Integer)
    temperatura = db.Column(db.Integer)
    presion = db.Column(db.Integer)
    combustible = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SensorData {self.device_id}>"

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

@app.route('/datos', methods=['POST'])
def recibir_datos():
    # Recibir y decodificar el JSON de la solicitud
    data = request.json

    # Validar que se recibieron los datos correctos
    if not data or "device_id" not in data:
        return jsonify({"status": "error", "message": "Datos inválidos o faltantes"}), 400

    # Extraer los datos del JSON
    device_id = data.get("device_id")
    velocidad = data.get("velocidad")
    temperatura = data.get("temperatura")
    presion = data.get("presion")
    combustible = data.get("combustible")

    # Buscar si ya existe un registro para este dispositivo
    sensor_data = SensorData.query.get(device_id)

    if sensor_data:
        # Actualizar los valores si el dispositivo ya existe
        sensor_data.velocidad = velocidad
        sensor_data.temperatura = temperatura
        sensor_data.presion = presion
        sensor_data.combustible = combustible
        sensor_data.timestamp = datetime.utcnow()
    else:
        # Crear un nuevo registro si el dispositivo no existe
        sensor_data = SensorData(
            device_id=device_id,
            velocidad=velocidad,
            temperatura=temperatura,
            presion=presion,
            combustible=combustible
        )
        db.session.add(sensor_data)

    # Guardar los cambios en la base de datos
    db.session.commit()

    # Reenviar los datos al backend central
    payload = {
        "device_id": device_id,
        "velocidad": velocidad,
        "temperatura": temperatura,
        "presion": presion,
        "combustible": combustible
    }
    
    try:
        response = requests.post(CENTRAL_BACKEND_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print("Datos enviados al backend central con éxito.")
        else:
            print(f"Error al enviar datos al backend central: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el backend central: {e}")

    # Responder al ESP32 que los datos se recibieron correctamente
    return jsonify({"status": "success", "message": "Datos recibidos y reenviados al backend central", "device_id": device_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

