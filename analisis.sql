-- Crear tabla temporal con longitud suficiente para la columna palabra
CREATE TEMPORARY TABLE temp_palabras (palabra VARCHAR(255));

-- Insertar palabras en la tabla temporal excluyendo stopwords y asegurando que no excedan la longitud máxima permitida
INSERT INTO temp_palabras (palabra)
SELECT LOWER(SUBSTRING_INDEX(SUBSTRING_INDEX(texto, ' ', n.n), ' ', -1)) AS palabra
FROM tweets
JOIN (
    SELECT a.N + b.N * 10 + 1 AS n
    FROM (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a
    CROSS JOIN (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
) n
WHERE n.n <= 1 + (LENGTH(texto) - LENGTH(REPLACE(texto, ' ', '')))
AND CHAR_LENGTH(SUBSTRING_INDEX(SUBSTRING_INDEX(texto, ' ', n.n), ' ', -1)) <= 255
AND LOWER(SUBSTRING_INDEX(SUBSTRING_INDEX(texto, ' ', n.n), ' ', -1)) NOT IN (SELECT palabra FROM stopwords);

-- Consultar las palabras más frecuentes excluyendo stopwords
SELECT palabra, COUNT(*) AS frecuencia
FROM temp_palabras
GROUP BY palabra
ORDER BY frecuencia DESC
LIMIT 15;

-- Eliminar la tabla temporal después del uso
DROP TEMPORARY TABLE temp_palabras;
