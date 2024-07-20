from kafka import KafkaProducer
import json
import tweepy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
import threading

# Configuración API
consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
access_token = 'access_token'
access_token_secret = 'access_token_secret'

# Configuración Kafka
kafka_topic = 'tweets_topic'
kafka_bootstrap_servers = 'localhost:9092'

# Configurar productor Kafka
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Configurar cliente Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        tweet = {
            'id': status.id_str,
            'text': status.text,
            'created_at': status.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        producer.send(kafka_topic, tweet)
        print(f"Tweet enviado a Kafka: {tweet}")

def start_twitter_stream():
    stream_listener = MyStreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=['python', 'data'], is_async=True)

def process_tweets():
    env = StreamExecutionEnvironment.get_execution_environment()

    # Configuración consumidor Kafka
    kafka_props = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'flink_consumer_group'
    }

    kafka_consumer = FlinkKafkaConsumer(
        topics='tweets_topic',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )

    # Leer mensajes Kafka
    stream = env.add_source(kafka_consumer)

    # Procesar tweets
    stream.map(lambda tweet: f"Procesando tweet: {tweet}") \
          .print()

    env.execute("Procesamiento de Tweets en Tiempo Real")

if __name__ == '__main__':
    # Iniciar el stream de Twitter en un hilo separado
    twitter_stream_thread = threading.Thread(target=start_twitter_stream)
    twitter_stream_thread.start()

    # Procesar tweets en tiempo real con Flink y Kafka
    process_tweets()
