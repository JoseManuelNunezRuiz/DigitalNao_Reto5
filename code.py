import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

# Cargar el archivo JSON
archivo_json = 'tweets_extraction.json'
with open(archivo_json, 'r', encoding='utf-8') as file:
    tweets = json.load(file)

# Convertir los datos a un DataFrame de pandas
df = pd.json_normalize(tweets)

# Checar tipos de datos
print('Tipos de datos de columnas:')
print(df.dtypes)

# Verificar estructura de datos
print('Info del DF:')
print(df.info())

# Verificar valores nulos:
print('Valores nulos por columna:')
print(df.isnull().sum())

# Revisar agunas filas del principio
print('Primeros 5 registros del DF:')
print(df.head())

# Revisar algunas filas del final
print('Últimos 5 registros del DF:')
print(df.head())

# Estadísticas desciptivas
print('Estadísticas descriptivas del DF:')
print(df.describe(include='all'))

#ANÁLISIS GRAL SENTIMIENTOS

# Eliminar duplicados
df = df.drop_duplicates(subset='id')

# Rellenar NAN
df['texto'].fillna('', inplace=True)

# Se crea una función para obtener sentimientos y se aplica una nueva columna al DF
def obtener_sentimiento(texto):
    blob = TextBlob(texto)
    return blob.sentiment.polarity
df['sentimiento'] = df['texto'].apply(obtener_sentimiento)

# Se checa la estructura del nuevo campo
df['sentimiento'].info()

# Est. desc. sentimiento
sentimiento_descriptivo = df['sentimiento'].describe()
print(sentimiento_descriptivo)

# Histograma frecuencias sentimiento
sns.set(style='whitegrid')
plt.figure(figsize=(10,6))
sns.histplot(df['sentimiento'], bins = 30, kde = True)
plt.title('Dist. sentimientos de los tweets')
plt.xlabel('Sentimiento')
plt.ylabel('Frec')
plt.show()

