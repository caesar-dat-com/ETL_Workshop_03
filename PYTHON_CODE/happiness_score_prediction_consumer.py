from kafka import KafkaConsumer
import json

# Configurar el consumidor de Kafka
consumer = KafkaConsumer(
    'happiness_predictions',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',  # para comenzar a leer desde el último offset no consumido
    enable_auto_commit=True,  # para confirmar los offsets automáticamente
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Procesar mensajes recibidos
for message in consumer:
    data = message.value
    features = data['features']
    predicted_score = data['predicted_happiness_score']
    
    # Aquí podrías agregar lógica para almacenar los datos en una base de datos o realizar análisis adicional
    print(f"Received prediction: {predicted_score} for features: {features}")

# Cierra el consumidor correctamente cuando termines de procesarlo
consumer.close()
