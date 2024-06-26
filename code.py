import mysql.connector
import json
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging
import time

# Configuración de conexión a la base de datos
db_config = {
    'user': 'root',
    'password': 'timeseason',
    'host': 'localhost',
    'database': 'tweets_sentimientos'
}

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para conectar a la base de datos
def conectar_base_datos():
    return mysql.connector.connect(
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        database=db_config['database']
    )

# Función para insertar un tweet en la base de datos
def insertar_tweet(cursor, tweet):
    try:
        sql = """
        INSERT INTO tweets (id_tweet, texto, usuario, hashtags, fecha, retweets, favoritos)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        hashtags = ', '.join(tweet['hashtags']) if isinstance(tweet['hashtags'], list) else tweet['hashtags']
        cursor.execute(sql, (
            tweet['id'], tweet['texto'], tweet['usuario'], hashtags, tweet['fecha'], tweet['retweets'], tweet['favoritos']
        ))
        cursor.execute("COMMIT")  # Realizar commit (cambios permanentes)
    except mysql.connector.Error as err:
        logger.error(f"Error al insertar el tweet: {err}")
        cursor.execute("ROLLBACK")  # Realizar rollback (deshacer cambios) en caso de error

# Función para insertar el análisis de sentimiento en la base de datos
def insertar_sentimiento(cursor, id_tweet, sentimiento):
    try:
        sql = """
        INSERT INTO sentimientos (id_tweet, sentimiento)
        VALUES (%s, %s)
        """
        cursor.execute(sql, (id_tweet, sentimiento))
        cursor.execute("COMMIT")  # Realizar commit
    except mysql.connector.Error as err:
        logger.error(f"Error al insertar el sentimiento: {err}")
        cursor.execute("ROLLBACK")  # Realizar rollback en caso de error

try:
    # Conectar a la base de datos
    db_conn = conectar_base_datos()
    cursor = db_conn.cursor(buffered=True)

    # Cargar el archivo JSON
    archivo_json = 'tweets_extraction.json'
    with open(archivo_json, 'r', encoding='utf-8') as file:
        tweets = json.load(file)

    # Convertir los datos a un DataFrame de pandas
    df = pd.json_normalize(tweets)

    # Convertir la columna 'fecha' a datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Eliminar duplicados
    df = df.drop_duplicates(subset='texto')

    # Descargar recursos necesarios de NLTK
    nltk.download('vader_lexicon')

    # Configurar el analizador de sentimientos
    sia = SentimentIntensityAnalyzer()

    # Procesar y almacenar tweets y análisis de sentimiento
    for _, row in df.iterrows():
        id_tweet = row['id']
        texto = row['texto']
        sentimiento = sia.polarity_scores(texto)['compound']
        
        tweet_data = {
            'id': id_tweet,
            'texto': texto,
            'usuario': row['usuario'],
            'hashtags': row.get('hashtags', ''),  # Si hashtags no existe, se asigna una cadena vacía
            'fecha': row['fecha'],
            'retweets': row.get('retweets', 0),  # Si retweets no existe, se asigna 0
            'favoritos': row.get('favoritos', 0)  # Si favoritos no existe, se asigna 0
        }
        
        insertar_tweet(cursor, tweet_data)
        insertar_sentimiento(cursor, id_tweet, sentimiento)

    # Cerrar cursor y conexión
    cursor.close()
    db_conn.close()
    logger.info("Conexión a la base de datos cerrada.")

except mysql.connector.Error as err:
    logger.error(f"Error al conectar con la base de datos: {err}")
    # Intentar reconectar después de esperar un breve período
    logger.info("Intentando reconectar en 5 segundos...")
    time.sleep(5)
    db_conn = conectar_base_datos()
    cursor = db_conn.cursor(buffered=True)

logger.info("Proceso completado.")

