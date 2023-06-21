import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT, refs INT DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS ref (id INT, reffer INT)")
conn.commit()

def add_user(id):
    cursor.execute("INSERT INTO users (id) VALUES (?)", (id,))
    conn.commit()

def get_users() -> list:
    """Bu funksiya users tablesidagi foydalanuvchilarni qaytaradi"""
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    users = [user[0] for user in users]
    return users

def minus_balans(id, amount):
    cursor.execute(f"UPDATE users SET refs = refs - {amount} WHERE id = {id}")
    conn.commit()

def get_balans(id):
    cursor.execute("SELECT refs FROM users")
    balans = cursor.fetchall()
    balans = balans[0][0]
    return balans

def add_ref(id):
    """berilgan id egasini referallarsoni bittaga oshiriladi"""
    cursor.execute(f"UPDATE users SET refs = refs + 1 WHERE id = {id}")
    conn.commit()

def set_ref(id, reffer):
    """Bu refera, havola orqali tashrif buyurganlarni dbga saqlab turadi"""
    cursor.execute("INSERT INTO ref (id, reffer) VALUES (?,?)", (id, reffer))
    conn.commit()

def get_ref(id):
    cursor.execute("SELECT reffer from ref")
    reffer = cursor.fetchall()
    reffer = reffer[0][0]
    return reffer

def del_ref(id):
    cursor.execute(f"DELETE FROM ref WHERE id = {id}")
    conn.commit()