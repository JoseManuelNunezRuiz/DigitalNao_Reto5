import matplotlib.pyplot as plt
import pandas as pd
import mysql.connector
from adjustText import adjust_text
import plotly.express as px

# Conexión a la base de datos
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='my_pass',
    database='tweets_sentimientos'
)

# Consulta sql para obtener los datos de sentimientos
query_sentimientos = '''
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
df_sentimientos = pd.read_sql(query_sentimientos, conn)

# Consulta sql para obtener los datos de frecuencia total
query_bubble = '''
SELECT
    p.palabra,
    COUNT(*) AS conteo_total
FROM tweets t
JOIN palabras_mas_repetidas p ON t.texto LIKE CONCAT('%', p.palabra, '%')
GROUP BY p.palabra
ORDER BY conteo_total DESC;
'''
df_bubble = pd.read_sql(query_bubble, conn)
conn.close()

# Filtrar datos por sentimiento
df_positivo = df_sentimientos[df_sentimientos['tipo_sentimiento'] == 'positivo']
df_negativo = df_sentimientos[df_sentimientos['tipo_sentimiento'] == 'negativo']
df_neutral = df_sentimientos[df_sentimientos['tipo_sentimiento'] == 'neutral']

# Crear layout con todas las gráficas
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 16))

# Gráficas de barras horizontales
df_positivo.plot(kind='barh', x='palabra', y='conteo', ax=axes[0, 0], color='green', legend=False)
axes[0, 0].set_title('Positivo')
axes[0, 0].set_xlabel('Frecuencia')

df_negativo.plot(kind='barh', x='palabra', y='conteo', ax=axes[0, 1], color='red', legend=False)
axes[0, 1].set_title('Negativo')
axes[0, 1].set_xlabel('Frecuencia')

df_neutral.plot(kind='barh', x='palabra', y='conteo', ax=axes[0, 2], color='blue', legend=False)
axes[0, 2].set_title('Neutral')
axes[0, 2].set_xlabel('Frecuencia')

# Gráfico de burbujas empacadas
bubble_fig = px.scatter(df_bubble, x='palabra', y=df_bubble.index, size='conteo_total', color='conteo_total',
                        hover_name='palabra', size_max=50, title='Packed Bubble Chart de Frecuencia de Palabras')
bubble_fig.update_layout(showlegend=False)
bubble_fig.show()

# Scatterplot de frecuencias positivas vs. negativas
plt.sca(axes[1, 0])  # Seleccionar el subplot para el scatterplot
scatter = axes[1, 0].scatter(df_positivo['conteo'], df_negativo['conteo'], c='blue', alpha=0.5)

axes[1, 0].set_xlabel('Frecuencias Positivas')
axes[1, 0].set_ylabel('Frecuencias Negativas')
axes[1, 0].set_title('Scatterplot de Frecuencias Positivas vs. Frecuencias Negativas')

# Etiquetar puntos del scatter
texts = [axes[1, 0].text(df_positivo['conteo'].iloc[i], df_negativo['conteo'].iloc[i],
                         df_positivo['palabra'].iloc[i], fontsize=9)
         for i in range(len(df_positivo))]
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='red'))

# Ajustar el diseño para el subplot vacío
axes[1, 1].axis('off')
axes[1, 2].axis('off')

plt.tight_layout()
plt.show()
