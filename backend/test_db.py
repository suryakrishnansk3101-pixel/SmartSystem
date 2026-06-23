import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="smart_ai",
    user="postgres",
    password="sk2020"
)

print("Database Connected Successfully!")

conn.close()