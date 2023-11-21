from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()


def db_connect():
    connection = sqlite3.connect('GameUsers.db')
    return connection, connection.cursor()


def db_disconnect(connection):
    connection.commit()
    connection.close()


def create_table():
    connection, cursor = db_connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        userclass INTEGER NULL,
        userlevel TEXT NULL
    )
    ''')

    db_disconnect(connection)


def insert_user(name, email, userclass, userlevel):
    connection, cursor = db_connect()

    cursor.execute('INSERT INTO Users(username,email,userclass,userlevel) VALUES(?,?,?,?)',
                   (name, email, userclass, userlevel))

    db_disconnect(connection)


def select_all_users():
    connection, cursor = db_connect()

    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()

    connection.close()
    return users


def select_user_by_name(name):
    connection, cursor = db_connect()

    cursor.execute('SELECT * FROM Users WHERE username = ?', (name,))
    results = cursor.fetchall()

    connection.close()
    return results


def select_user_by_email(email):
    connection, cursor = db_connect()

    cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
    results = cursor.fetchall()

    connection.close()
    return results


def update_email_by_name(name, new_email):
    connection, cursor = db_connect()

    cursor.execute('UPDATE Users SET email = ? WHERE username = ?', (new_email, name))

    db_disconnect(connection)


def update_userclass_by_name(name, new_userclass):
    connection, cursor = db_connect()

    cursor.execute('UPDATE Users SET userclass = ? WHERE username = ?', (new_userclass, name))

    db_disconnect(connection)


def update_userlevel_by_name(name, new_userlevel):
    connection, cursor = db_connect()

    cursor.execute('UPDATE Users SET userlevel = ? WHERE username = ?', (new_userlevel, name))

    db_disconnect(connection)


def delete_user_by_name(name):
    connection, cursor = db_connect()

    cursor.execute('DELETE FROM Users WHERE username = ?', (name,))

    db_disconnect(connection)


def main():
    create_table()

    while True:
        print('''
        Выберите действие
        1. Добавить нового пользователя
        2. Посмотреть всех пользователей
        3. Поиск пользователя по имени
        4. Обновить E-Mail пользователя
        5. Обновить уровень пользователя
        6. Удалить пользователя
        0. Выйти
        ''')

        choice = int(input('Введите номер действия: '))
        if choice == 1:
            name = input('Введите имя пользователя: ')
            email = input('Введите почту пользователя: ')
            userclass = input('Введите класс пользователя: ')
            insert_user(name, email, userclass, 1)
            print('Пользователь добавлен')
        elif choice == 2:
            print('Список всех пользователей:')
            for user in select_all_users():
                print(user)
        elif choice == 3:
            name = input('Введите имя пользователя: ')
            for user in select_user_by_name(name):
                print(user)
        elif choice == 4:
            name = input('Введите имя пользователя: ')
            email = input('Введите E-Mail пользователя: ')
            update_email_by_name(name, email)
            print('E-Mail пользователя обновлён')
        elif choice == 5:
            name = input('Введите имя пользователя: ')
            userlevel = input('Введите уровень пользователя: ')
            update_userlevel_by_name(name, userlevel)
            print('Уровень пользователя обновлён')
        elif choice == 6:
            name = input('Введите имя пользователя:')
            delete_user_by_name(name)
            print('Пользователь удалён')
        elif choice == 0:
            print('Выход')
            break
        else:
            print('Некорректный выбор, попробуйте ещё раз')


class UserCreate(BaseModel):
    name: str
    email: str
    userclass: str = None
    userlevel: str = None


@app.post('/users/', response_model=UserCreate)
async def create_user(user: UserCreate):
    insert_user(user.name, user.email, user.userclass, user.userlevel)
    return user


@app.get('/users/')
async def read_users():
    users = select_all_users()
    return {'user': users}


@app.get('/users/{name}')
async def read_user_by_name(name: str):
    user = select_user_by_name(name)

    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    return {'user': user}


if __name__ == '__main__':
    main()
