import psycopg2

# Конфігурація підключення до бази даних
db_config = {
    "dbname": "postgres_db",
    "user": "postgres_user",
    "password": "postgres_password",
    "host": "localhost",
    "port": "5433"
}

# SQL-запити для створення таблиць
create_tables_commands = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        fullname VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS status (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        status_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (status_id) REFERENCES status (id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """
]

def create_tables():
    conn = None
    try:
        # Підключення до бази даних
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Створення таблиць
        for command in create_tables_commands:
            cur.execute(command)

        # Завершення транзакції
        conn.commit()
        print("Таблиці успішно створено.")
        # Закриття курсору і підключення
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()
