import os
import time
from datetime import datetime

# Configuración de la base de datos
db_host = 'localhost'
db_user = 'root'
db_password = 'my_pass'
db_name = 'tweets_sentimientos'

# Ruta donde se guardarán las copias de seguridad
backup_dir = './backup'

def backup_database():
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"{db_name}_backup_{current_time}.sql")
    
    command = f"mysqldump -h {db_host} -u {db_user} -p{db_password} {db_name} > {backup_file}"
    os.system(command)
    print(f"Copia de seguridad creada: {backup_file}")

# Realizar copias de seguridad cada día (86400 segundos)
backup_interval = 86400

while True:
    backup_database()
    time.sleep(backup_interval)
