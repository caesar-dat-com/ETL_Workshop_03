from kafka import KafkaProducer
import json
from CSV_BAR import file_path, model_filename

# Configurar el productor de Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Enviar el 30% de las predicciones una a una a Kafka
for i in range(int(0.3 * len(X_test_poly))):
    data = {
        'features': X_test_poly[i].tolist(),
        'predicted_happiness_score': y_pred_poly[i]
    }
    producer.send('happiness_predictions', value=data)

producer.flush()
print("El 30% de las predicciones han sido enviadas a Kafka.")
