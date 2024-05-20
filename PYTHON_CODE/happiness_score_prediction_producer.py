import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import randint
from kafka import KafkaProducer
import json
import pickle
from CSV_BAR import file_path, model_filename

# Cargar los datos
data = pd.read_csv(file_path)

# Eliminar columnas con muchos valores faltantes y baja correlación con 'score'
columns_to_drop = [
    'dystopia_residual', 'family', 'lower_confidence_interval', 'upper_confidence_interval',
    'whiskerhigh', 'whiskerlow', 'standard_error', 'region', 'social_support'
]
data_cleaned = data.drop(columns=columns_to_drop)

# Manejar valores faltantes para 'government_corruption' rellenando con la mediana
median_value = data_cleaned['government_corruption'].median()
data_cleaned['government_corruption'] = data_cleaned['government_corruption'].fillna(median_value)

# Definir las características y la variable objetivo
X = data_cleaned.drop(['score', 'country', 'rank'], axis=1)
y = data_cleaned['score']

# Crear características polinómicas
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

# Dividir los datos en conjuntos de entrenamiento y prueba (70% entrenamiento, 30% prueba)
X_train_poly, X_test_poly, y_train, y_test = train_test_split(X_poly, y, test_size=0.30, random_state=42)

# Aquí se ajusta el modelo con el 70% de los datos
random_search = RandomizedSearchCV(
    RandomForestRegressor(random_state=42), 
    param_distributions={
        'n_estimators': randint(100, 200),
        'max_features': ['sqrt', 'log2'],
        'max_depth': randint(3, 20),
        'min_samples_split': randint(2, 11),
        'min_samples_leaf': randint(1, 11),
        'bootstrap': [True, False]
    }, 
    n_iter=200, cv=10, verbose=2, random_state=42, n_jobs=-1
)
random_search.fit(X_train_poly, y_train)

# Mejor modelo encontrado
best_model = random_search.best_estimator_

# Guardar el modelo entrenado como un archivo .pkl
with open(model_filename, 'wb') as file:
    pickle.dump(best_model, file)

# Predecir los puntajes de felicidad en el conjunto de prueba con características polinómicas
y_pred_poly = best_model.predict(X_test_poly)

# Calcular el MSE y R^2 optimizados con características polinómicas
mse_poly = mean_squared_error(y_test, y_pred_poly)
r2_poly = r2_score(y_test, y_pred_poly)

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
print("Polynomial Features Optimized MSE:", mse_poly)
print("Polynomial Features Optimized R^2:", r2_poly)
