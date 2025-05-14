# services/web/seed_data.py

import sys
import random
import string
from sqlalchemy import text
from project import app, db


def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_hello_messages():
    return [
        "Hello", "Hola", "Bonjour", "Hallo", "Ciao", "Ola", "Privet", "Ni hao", "Konnichiwa", "Annyeonghaseyo",
        "Salam", "Namaste", "Merhaba", "Hej", "Hei", "Ahoj", "Szervusz", "Szia", "Geia sou", "Shalom"
    ]


def generate_unique_usernames(n):
    usernames = set()
    while len(usernames) < n:
        usernames.add(f"user_{random_string(6)}")
    return list(usernames)


def insert_users(n):
    usernames = generate_unique_usernames(n)
    print(f"Inserting {n} users...")
    for username in usernames:
        password = random_string(12)
        age = random.randint(18, 70)
        db.session.execute(
            text("INSERT INTO users (username, password, age) VALUES (:u, :p, :a)"),
            {"u": username, "p": password, "a": age}
        )
    db.session.commit()

    # Return the inserted user_ids (assumes autoincrement PKs in order)
    result = db.session.execute(text("SELECT user_id FROM users ORDER BY user_id DESC LIMIT :n"), {"n": n})
    return [row.user_id for row in result]


def insert_messages(n, user_ids):
    print(f"Inserting {n} messages...")
    greetings = get_hello_messages()
    for _ in range(n):
        user_id = random.choice(user_ids)
        msg = random.choice(greetings)
        db.session.execute(
            text("INSERT INTO messages (user_id, message) VALUES (:uid, :msg)"),
            {"uid": user_id, "msg": msg}
        )


def insert_transactions(n, user_ids):
    print(f"Inserting {n} transactions...")
    for _ in range(n):
        user_id = random.choice(user_ids)
        amount = random.randint(10, 10000)
        db.session.execute(
            text("INSERT INTO transactions (amount, user_id) VALUES (:amt, :uid)"),
            {"amt": amount, "uid": user_id}
        )


def main(n_rows):
    with app.app_context():
        user_ids = insert_users(n_rows)
        insert_messages(n_rows * 10, user_ids)  # 10× more messages
        insert_transactions(n_rows, user_ids)
        db.session.commit()
        print("✅ Done seeding.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python seed_data.py <number_of_rows>")
        sys.exit(1)
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Please enter a valid integer.")
        sys.exit(1)
    main(n)
