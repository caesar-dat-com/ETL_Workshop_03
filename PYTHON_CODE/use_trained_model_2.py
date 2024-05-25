import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle

# Ruta del modelo guardado
model_path = "/home/cesarreyes/Desktop/platzi/ETL_Workshop_03/DATA_PKL/happiness_score_model.pkl"

# Ruta del archivo CSV
file_path = "ruta/del/archivo.csv"  # Cambia esto por la ruta correcta de tu archivo CSV

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

# Cargar el modelo entrenado desde el archivo .pkl
with open(model_path, 'rb') as file:
    best_model = pickle.load(file)

# Predecir los puntajes de felicidad en el conjunto de prueba con características polinómicas
y_pred_poly = best_model.predict(X_test_poly)

# Calcular el MSE y R^2 optimizados con características polinómicas
mse_poly = mean_squared_error(y_test, y_pred_poly)
r2_poly = r2_score(y_test, y_pred_poly)

print("Polynomial Features Optimized MSE:", mse_poly)
print("Polynomial Features Optimized R^2:", r2_poly)

# Mostrar algunas predicciones
print("\nAlgunas predicciones de felicidad:")
for i in range(10):  # Mostrar las primeras 10 predicciones
    print(f"Predicción: {y_pred_poly[i]}, Real: {y_test.values[i]}")
