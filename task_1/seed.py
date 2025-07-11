from faker import Faker
import psycopg2
import random

# Налаштування Faker
fake = Faker()

# Конфігурація підключення до бази даних
db_config = {
    "dbname": "postgres_db",
    "user": "postgres_user",
    "password": "postgres_password",
    "host": "localhost",
    "port": "5433"
}

# Функції для генерації даних
def generate_users(n=10):
    """ Генерує випадкові дані для таблиці користувачів """
    users = [(fake.name(), fake.unique.email()) for _ in range(n)]
    return users

def generate_statuses():
    """ Генерує фіксовані статуси для таблиці статусів """
    return [('new',), ('in progress',), ('completed',)]

def generate_tasks(n=30, num_users=10, num_statuses=3):
    """ Генерує випадкові дані для таблиці завдань """
    tasks = []
    for _ in range(n):
        title = fake.sentence(nb_words=6)
        description = fake.text(max_nb_chars=200)
        status_id = random.randint(1, num_statuses)
        user_id = random.randint(1, num_users)
        tasks.append((title, description, status_id, user_id))
    return tasks

# Функція для заповнення бази даних
def populate_database():
    conn = None
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Вставка статусів
        statuses = generate_statuses()
        cur.executemany("INSERT INTO status (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", statuses)
        print("Статуси додано.")

        # Вставка користувачів
        users = generate_users()
        cur.executemany("INSERT INTO users (fullname, email) VALUES (%s, %s) ON CONFLICT (email) DO NOTHING;", users)
        print("Користувачів додано.")

        # Отримання id користувачів та статусів для створення завдань
        cur.execute("SELECT id FROM users;")
        user_ids = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT id FROM status;")
        status_ids = [row[0] for row in cur.fetchall()]

        if not user_ids or not status_ids:
            print("Не вдалося отримати id користувачів або статусів. Заповнення завдань неможливе.")
            return

        # Вставка завдань
        tasks = []
        for _ in range(30):
            tasks.append((
                fake.sentence(nb_words=5),
                fake.text(max_nb_chars=150),
                random.choice(status_ids),
                random.choice(user_ids)
            ))
        cur.executemany("INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s);", tasks)
        print("Завдання додано.")

        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Помилка: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    populate_database()
