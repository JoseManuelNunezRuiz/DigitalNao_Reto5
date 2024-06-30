import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import mysql.connector

# Conexión a la base de datos
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='my_pass',
    database='tweets_sentimientos'
)

# Consulta SQL para obtener los datos de frecuencias por sentimiento
query_barras = '''
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

df_barras = pd.read_sql(query_barras, conn)

# Consulta SQL para obtener los datos de frecuencia total por palabra
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

# Consulta SQL para obtener los datos de frecuencias positivas y negativas por palabra
query_scatter = '''
SELECT
    p.palabra,
    SUM(CASE WHEN s.sentimiento > 0 THEN 1 ELSE 0 END) AS frec_positivas,
    SUM(CASE WHEN s.sentimiento < 0 THEN 1 ELSE 0 END) AS frec_negativas
FROM tweets t
JOIN sentimientos s ON t.id_tweet = s.id_tweet
JOIN palabras_mas_repetidas p ON t.texto LIKE CONCAT('%', p.palabra, '%')
GROUP BY p.palabra
ORDER BY p.palabra;
'''

df_scatter = pd.read_sql(query_scatter, conn)
conn.close()

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Diseño del dashboard
app.layout = html.Div([
    html.H1('Dashboard de Análisis de Sentimientos en Tweets'),

    # Gráficas de barras horizontales
    html.Div([
        html.Div([
            dcc.Graph(
                id='grafico-barras-positivo',
                figure={
                    'data': [
                        {'y': df_barras[df_barras['tipo_sentimiento'] == 'positivo']['palabra'],
                         'x': df_barras[df_barras['tipo_sentimiento'] == 'positivo']['conteo'],
                         'type': 'bar', 'name': 'Positivo', 'orientation': 'h', 'marker': {'color': 'green'}},
                    ],
                    'layout': {
                        'title': 'Palabras Positivas',
                        'yaxis': {'title': 'Palabra'},
                        'xaxis': {'title': 'Frecuencia'}
                    }
                }
            )
        ], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(
                id='grafico-barras-negativo',
                figure={
                    'data': [
                        {'y': df_barras[df_barras['tipo_sentimiento'] == 'negativo']['palabra'],
                         'x': df_barras[df_barras['tipo_sentimiento'] == 'negativo']['conteo'],
                         'type': 'bar', 'name': 'Negativo', 'orientation': 'h', 'marker': {'color': 'red'}},
                    ],
                    'layout': {
                        'title': 'Palabras Negativas',
                        'yaxis': {'title': 'Palabra'},
                        'xaxis': {'title': 'Frecuencia'}
                    }
                }
            )
        ], style={'width': '33%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(
                id='grafico-barras-neutral',
                figure={
                    'data': [
                        {'y': df_barras[df_barras['tipo_sentimiento'] == 'neutral']['palabra'],
                         'x': df_barras[df_barras['tipo_sentimiento'] == 'neutral']['conteo'],
                         'type': 'bar', 'name': 'Neutral', 'orientation': 'h', 'marker': {'color': 'blue'}},
                    ],
                    'layout': {
                        'title': 'Palabras Neutrales',
                        'yaxis': {'title': 'Palabra'},
                        'xaxis': {'title': 'Frecuencia'}
                    }
                }
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
    ]),

    # Gráfico de burbujas empacadas y scatterplot
    html.Div([
        html.Div([
            dcc.Graph(
                id='grafico-bubble',
                figure=px.scatter(df_bubble, x='palabra', y=df_bubble.index, size='conteo_total', color='conteo_total',
                                  hover_name='palabra', size_max=50, title='Frecuencia de Palabras')
            )
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(
                id='scatterplot',
                figure={
                    'data': [
                        {'x': df_scatter['frec_positivas'], 'y': df_scatter['frec_negativas'], 'mode': 'markers+text',
                         'text': df_scatter['palabra'], 'textposition': 'top center',
                         'marker': {'size': 10, 'color': 'blue', 'opacity': 0.5}}
                    ],
                    'layout': {
                        'title': 'Frecuencias Positivas vs Negativas',
                        'xaxis': {'title': 'Frecuencias Positivas'},
                        'yaxis': {'title': 'Frecuencias Negativas'}
                    }
                }
            )
        ], style={'width': '50%', 'display': 'inline-block'}),
    ])
])

# Ejecutar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=True)
