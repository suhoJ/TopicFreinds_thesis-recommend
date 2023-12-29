from flask import Flask
import redis
from prometheus_flask_exporter import PrometheusMetrics
import mysql.connector
from datetime import datetime

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'thesis-mysql'  # Update with your MySQL host
app.config['MYSQL_USER'] = 'root'          # Update with your MySQL user
app.config['MYSQL_PASSWORD'] = 'a229jIGvb8'  # Update with your MySQL password
app.config['MYSQL_DB'] = 'timestamp'      # Update with your MySQL database

# Redis Configuration
app.config['REDIS_URL'] = "redis://:thesis@my-redis-master:6379/0"  
redis_client = redis.StrictRedis.from_url(app.config['REDIS_URL'])

# MySQL Connection
def get_mysql_connection():
    conn = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return conn

@app.route('/')
def hello_world():
    count = redis_client.incr('hits')

    # Record Timestamp in MySQL
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO access_log (timestamp) VALUES (%s)", (datetime.now(),))
    conn.commit()
    cursor.close()
    conn.close()

    return 'Hello, World! I have been seen {} times.'.format(count)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
