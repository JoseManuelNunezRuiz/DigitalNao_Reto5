-- 1. OBTENER PALABRAS MÁS REPETIDAS

USE tweets_sentimientos;

-- Crear la tabla temporal
DROP TEMPORARY TABLE IF EXISTS temp_palabras;
CREATE TEMPORARY TABLE temp_palabras (palabra VARCHAR(255));

-- Insertar las palabras más repetidas excluyendo palabras vacías, stopwords y palabras específicas
INSERT INTO temp_palabras (palabra)
SELECT palabra
FROM (
    SELECT
        SUBSTRING_INDEX(SUBSTRING_INDEX(texto, ' ', n.n), ' ', -1) AS palabra
    FROM tweets
    JOIN (
        SELECT a.N + b.N * 10 + 1 AS n
        FROM (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a
        CROSS JOIN (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
    ) n
    WHERE n.n <= 1 + (LENGTH(texto) - LENGTH(REPLACE(texto, ' ', '')))
    AND CHAR_LENGTH(SUBSTRING_INDEX(SUBSTRING_INDEX(texto, ' ', n.n), ' ', -1)) <= 255
    AND SUBSTRING_INDEX(SUBSTRING_INDEX(texto, ' ', n.n), ' ', -1) NOT IN (SELECT palabra FROM stopwords)
    AND SUBSTRING_INDEX(SUBSTRING_INDEX(texto, ' ', n.n), ' ', -1) NOT IN ('', 'contra', 'desde', 'está', 'dos', 'entre', 'hay', '|', 'las', 'tiene', 'tras')
) palabras
GROUP BY palabra
ORDER BY COUNT(*) DESC
LIMIT 15;

-- Contar los tweets por sentimiento
SELECT
    p.palabra,
    CASE
        WHEN s.sentimiento > 0 THEN 'positivo'
        WHEN s.sentimiento < 0 THEN 'negativo'
        ELSE 'neutral'
    END AS tipo_sentimiento,
    COUNT(*) AS conteo
FROM tweets t
JOIN sentimientos s ON t.id_tweet = s.id_tweet
JOIN temp_palabras p ON t.texto LIKE CONCAT('%', p.palabra, '%')
GROUP BY p.palabra, tipo_sentimiento
ORDER BY p.palabra, tipo_sentimiento;

-- 2. OBTENER SENTIMIENTO CON MAYOR INTENSIDAD

SELECT
    CASE
        WHEN sentimiento > 0 THEN 'positivo'
        WHEN sentimiento < 0 THEN 'negativo'
        ELSE 'neutral'
    END AS tipo_sentimiento,
    COUNT(*) AS frecuencia,
    AVG(ABS(sentimiento)) AS intensidad_media
FROM sentimientos
GROUP BY tipo_sentimiento
ORDER BY intensidad_media DESC

-- 3. OBTENER OBJETIVIDAD DE LOS TWEETS

SELECT
    SUM(CASE WHEN ABS(s.sentimiento) < 0.1 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS porcentaje_neutral
FROM tweets t
JOIN sentimientos s ON t.id_tweet = s.id_tweet;

-- 4. OBTENER ESTIMACIÓN POSITIVIDAD DÍA SIGUIENTE

-- Encontrar fecha del último registro
SET @ultima_fecha = (SELECT MAX(fecha) FROM tweets);

-- Calcular sentimientos promedio, mínimo y máimo del último día disponible
SET @promedio_sentimiento_ultimo_dia = (
    SELECT AVG(s.sentimiento)
    FROM tweets t
    JOIN sentimientos s ON t.id_tweet = s.id_tweet
    WHERE DATE(t.fecha) = (SELECT MAX(DATE(fecha)) FROM tweets)
);

SET @minimo_sentimiento_ultimo_dia = (
    SELECT MIN(s.sentimiento)
    FROM tweets t
    JOIN sentimientos s ON t.id_tweet = s.id_tweet
    WHERE DATE(t.fecha) = (SELECT MAX(DATE(fecha)) FROM tweets)
);

SET @maximo_sentimiento_ultimo_dia = (
    SELECT MAX(s.sentimiento)
    FROM tweets t
    JOIN sentimientos s ON t.ide_tweet = s.id_tweet
    WHERE DATE(t.fecha) = (SELECT MAX(DATE(fecha)) FROM tweets)
);

-- Simulación para estimar positividad día siguiente

SELECT
    DATE_ADD(@ultima_fecha, INTERVAL 1 DAY) AS fecha_prediccion,
    @promedio_sentimiento_ultimo_dia AS sentimiento_predicho,
    @minimo_sentimiento_ultimo_dia AS sentimiento_minimo,
    @maximo_sentimiento_ultimo_dia AS sentimiento_maximo;
