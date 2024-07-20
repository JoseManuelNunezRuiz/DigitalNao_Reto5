import os
import time
from datetime import datetime
import mysql.connector

# Configuración de la base de datos
db_host = 'localhost'
db_user = 'root'
db_password = 'my_pass'
db_name = 'tweets_sentimientos'

# Ruta de las copias de seguridad
backup_dir = './backup'

# Función para realizar la copia de seguridad
def backup_database():
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"{db_name}_backup_{current_time}.sql")
    
    command = f"mysqldump -h {db_host} -u {db_user} -p{db_password} {db_name} > {backup_file}"
    os.system(command)
    print(f"Copia de seguridad creada: {backup_file}")

# Función para eliminar filas duplicadas
def clean_duplicate_data():
    # Conexión a la base de datos
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    # Crear un cursor
    cursor = conn.cursor()

    # Eliminar filas duplicadas
    delete_duplicates_query = '''
    DELETE t1 FROM tweets t1
    INNER JOIN tweets t2 
    WHERE 
        t1.id_tweet < t2.id_tweet AND 
        t1.texto = t2.texto;
    '''

    cursor.execute(delete_duplicates_query)
    conn.commit()

    # Cerrar la conexión
    cursor.close()
    conn.close()

    print("Datos duplicados eliminados")

# Intervalo para realizar las copias de seguridad en segundos
backup_interval = 86400

# Bucle para realizar el mantenimiento
while True:
    backup_database()
    clean_duplicate_data()
    time.sleep(backup_interval)
