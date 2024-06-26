-- Revisar si los tweets guardados desde Python corresponden en cantidad
SELECT COUNT(*) AS total_registros
FROM tweets

-- Revisar (manualmente) si los tweets guardados están correctos en data por columna
SELECT * FROM tweets;

-- Y sentimientos
SELECT * FROM sentimientos;

-- Seleccionar algunos tweets aleatoriamente para checar concordancia manualmente
SELECT texto, sentimiento 
FROM tweets 
JOIN sentimientos ON tweets.id_tweet = sentimientos.id_tweet 
ORDER BY RAND() 
LIMIT 10;
