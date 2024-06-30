import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import mysql.connector
from adjustText import adjust_text

# 1.- CREAR GRÁFICO DE CONTEO DE SENTIMIENTOS POR PALABRA MÁS REPETIDA (ASPECTO)

# Conexión a la base de datos
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='my_pass',
    database='tweets_sentimientos'
)

# Consulta SQL para obtener los datos
query = '''
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
JOIN palabras_mas_repetidas p ON t.texto LIKE CONCAT('%', p.palabra, '%')
GROUP BY p.palabra, tipo_sentimiento
ORDER BY p.palabra, tipo_sentimiento;
'''

# Leer los datos en un DataFrame de pandas
df = pd.read_sql(query, conn)

# Cerrar la conexión
conn.close()

# Filtrar datos por sentimiento
df_positivo = df[df['tipo_sentimiento'] == 'positivo']
df_negativo = df[df['tipo_sentimiento'] == 'negativo']
df_neutral = df[df['tipo_sentimiento'] == 'neutral']

# Crear gráficas de barras horizontales
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 8))

df_positivo.plot(kind='barh', x='palabra', y='conteo', ax=axes[0], color='green', legend=False)
axes[0].set_title('Positivo')
axes[0].set_xlabel('Frecuencia')

df_negativo.plot(kind='barh', x='palabra', y='conteo', ax=axes[1], color='red', legend=False)
axes[1].set_title('Negativo')
axes[1].set_xlabel('Frecuencia')

df_neutral.plot(kind='barh', x='palabra', y='conteo', ax=axes[2], color='blue', legend=False)
axes[2].set_title('Neutral')
axes[2].set_xlabel('Frecuencia')

plt.tight_layout()
plt.show()

# 2.- GRÁFICA DE NUBE DE PALABRAS CIRCULAR

# Conexión a la base de datos
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='my_pass',
    database='tweets_sentimientos'
)

# Query para obtener los datos
query = '''
SELECT
    p.palabra,
    COUNT(*) AS conteo_total
FROM tweets t
JOIN palabras_mas_repetidas p ON t.texto LIKE CONCAT('%', p.palabra, '%')
GROUP BY p.palabra
ORDER BY conteo_total DESC;
'''

# Leer datos en un dataframe de pandas
df = pd.read_sql(query, conn)

# Cerrar la conexión
conn.close()

# Crear un gráfico de burbujas empacadas conteo general con Plotly
fig = px.scatter(df, x='palabra', y=df.index, size='conteo_total', color='conteo_total',
                 hover_name='palabra', size_max=50, title='Packed Bubble Chart de Frecuencia de Palabras')
fig.update_layout(showlegend=False)
fig.show()

# 3.- SCATTERPLOT PALABRAS/SENTIMIENTO

# Crear un scatterplot con colores diferentes para cada punto
plt.figure(figsize=(12, 8))
colors = range(len(df_positivo))  # Generar una lista de colores para cada punto
scatter = plt.scatter(df_positivo['conteo'], df_negativo['conteo'], c=colors, cmap='viridis')

# Configurar ejes y etiquetas
plt.xlabel('Frecuencia Positiva')
plt.ylabel('Frecuencia Negativa')
plt.title('Scatterplot de Frecuencias Positivas vs. Frecuencias Negativas')

# Etiquetar puntos con palabra correspondiente sin superposición
texts = [plt.text(df_positivo['conteo'].iloc[i], df_negativo['conteo'].iloc[i], word, fontsize=9) for i, word in enumerate(df_positivo['palabra'])]

# Ajustar las etiquetas para evitar superposiciones
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='red'))

plt.tight_layout()
plt.show()
