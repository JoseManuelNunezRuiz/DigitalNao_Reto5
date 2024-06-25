-- Crear la base de datos
CREATE DATABASE tweets_sentimientos;

-- Usar la base de datos recién creada
USE tweets_sentimientos;

-- Crear la tabla 'tweets'
CREATE TABLE tweets (
    id_tweet VARCHAR(255) PRIMARY KEY,
    texto TEXT,
    usuario VARCHAR(255),
    hashtags TEXT,
    fecha DATETIME,
    retweets INT,
    favoritos INT
);

-- Crear la tabla 'sentimientos'
CREATE TABLE sentimientos (
    id_sentimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_tweet VARCHAR(255),
    sentimiento FLOAT,
    FOREIGN KEY (id_tweet) REFERENCES tweets(id_tweet)
);
