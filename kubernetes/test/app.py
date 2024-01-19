from flask import Flask
import redis
from prometheus_flask_exporter import PrometheusMetrics
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# MySQL Configuration for RDS
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'thesis-1.cx2cmy4wc806.ap-northeast-2.rds.amazonaws.com')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'goorm')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'goorm1415')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'thesis')

# Redis Configuration
app.config['REDIS_URL'] = os.getenv('REDIS_URL', "redis://:thesis@redis-master:6379/0")
redis_client = redis.StrictRedis.from_url(app.config['REDIS_URL'])

# MySQL Connection
def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        return conn
    except mysql.connector.Error as err:
        app.logger.error("Error connecting to MySQL: {}".format(err))
        return None

@app.route('/')
def hello_world():
    count = redis_client.incr('hits')

    # Record Timestamp in MySQL
    conn = get_mysql_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO access_log (timestamp) VALUES (%s)", (datetime.now(),))
        conn.commit()
        cursor.close()
        conn.close()
        message = 'Hello, World! I have been seen {} times.'.format(count)
    else:
        message = 'Hello, World! Unable to connect to MySQL to update count.'

    return message

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
