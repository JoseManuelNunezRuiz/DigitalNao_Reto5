import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import string

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

# Estadísticas desciptivas
print('Estadísticas descriptivas del DF:')
print(df.describe(include='all'))

# Eliminar duplicados basados en el contenido de texto
df = df.drop_duplicates(subset='texto')

# Revisar algunas filas del principio
print('Primeros 5 registros del DF:')
print(df.head())

# Revisar algunas filas del final
print('Últimos 5 registros del DF:')
print(df.tail())

#OBTENER LAS PALABRAS CLAVE QUE SERVIRÁN COMO
# KEY ASPECTS EN EL REPORTE FINAL DEL ANÁLISIS:

# Se especifica el lenguaje
stop_words = set(stopwords.words('spanish'))
stemmer = SnowballStemmer('spanish')

#Se crea una función  para preprocesar tokens en español
def preprocess_text_spanish(text):
    # Tokenización
    tokens = word_tokenize(text.lower())
    # Eliminación de stopwords y signos de puntuación
    tokens = [token for token in tokens if token not in stop_words and token not in string.punctuation]
    # Stemming
    tokens = [stemmer.stem(token) for token in tokens]
    return tokens

df['tokens'] = df['texto'].apply(preprocess_text_spanish)

#Se crea una comprensión de listas partiendo de que df['tokens'] 
# contiene la lista de tokens preprocesados de los tweets
all_words = [word for tokens in df['tokens'] for word in tokens]
word_freq = Counter(all_words)

# Obtener las palabras más comunes
most_common_words = word_freq.most_common(20)

# Convertir a DataFrame de Pandas y ordenar
df_most_common = pd.DataFrame(most_common_words, columns=['Palabra', 'Frecuencia'])
df_most_common = df_most_common.sort_values(by='Frecuencia', ascending=False)

#Se imprime el DataFrame df_most_common
print(df_most_common)
