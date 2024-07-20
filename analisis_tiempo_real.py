from kafka import KafkaProducer
import json
import tweepy

# Configuración de Twitter API
consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
access_token = 'access_token'
access_token_secret = 'access_token_secret'

# Configuración de Kafka
kafka_topic = 'tweets_topic'
kafka_bootstrap_servers = 'localhost:9092'

# Productor de Kafka
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Cliente de Twitter
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

# Stream de Twitter
stream_listener = MyStreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=['python', 'data'])
