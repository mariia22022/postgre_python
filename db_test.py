import psycopg2
def create_db(conn):
    with conn.cursor() as curs:
        curs.execute(""" 
                DROP TABLE phone;""")

        curs.execute(""" 
                DROP TABLE client;""")

        curs.execute("""CREATE TABLE IF NOT EXISTS client(
                            client_id SERIAL PRIMARY KEY,
                            first_name VARCHAR(30) NOT NULL,
                            last_name VARCHAR (30) NOT NULL,
                            email VARCHAR(50) NOT NULL UNIQUE                           
                              ); """)
        curs.execute("""CREATE TABLE IF NOT EXISTS phone(
                            phone_id SERIAL PRIMARY KEY,
                            phone_number VARCHAR(30) UNIQUE,
                            client_id INTEGER REFERENCES client(client_id) ON DELETE CASCADE); """)

        conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as curs:
        try:
            curs.execute("""INSERT INTO client (first_name,last_name,email) VALUES (%s,%s,%s) RETURNING client_id; """, (first_name, last_name, email))
            client_id = curs.fetchone()
            if phones != None and client_id:
                for ph in phones:
                    try:
                        curs.execute(""" INSERT INTO phone (phone_number,client_id) VALUES (%s,%s); """, (ph,client_id[0]))
                    except  psycopg2.errors.UniqueViolation:
                        print(f"{ph}-Такой номер телефона уже есть в базе данныx")
        except psycopg2.errors.UniqueViolation:
            print(f"{email} - Адрес электронной почты уже существует")
        conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as curs:
        try:
            curs.execute(""" INSERT INTO phone (client_id,phone_number) VALUES (%s,%s); """, (client_id,phone))

        except  psycopg2.errors.UniqueViolation:
            print('Такой номер телефона уже есть в базе данных')
        except psycopg2.errors.ForeignKeyViolation:
            print('Клиента с таким id не существует')
    conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as curs:
        if phones != None:
            for ph in phones:
                curs.execute(""" UPDATE phone SET phone_number =%s WHERE client_id = %s; """, (ph, client_id))
        if first_name != None:
            curs.execute(""" UPDATE client SET first_name = %s WHERE client_id = %s; """, (first_name, client_id))
        if last_name != None:
            curs.execute(""" UPDATE client SET last_name = %s WHERE client_id = %s; """, (last_name, client_id))
        if email != None:
            curs.execute(""" UPDATE client SET email = %s WHERE client_id = %s; """, (email, client_id))
        curs.execute(""" SELECT *  FROM client ;""")
        print(curs.fetchall())
        curs.execute(""" SELECT *  FROM phone ;""")
        print(curs.fetchall())

def delete_phone(conn, client_id, phone):
    with conn.cursor() as curs:
        curs.execute(""" DELETE FROM phone WHERE client_id = %s AND phone_number = %s; """, (client_id, phone))
        curs.execute(""" SELECT *  FROM phone  ;""")
        print(curs.fetchall())

def delete_client(conn, client_id):
    with conn.cursor() as curs:
        curs.execute(""" DELETE FROM client WHERE client_id = %s; """, (client_id,))
        curs.execute(""" SELECT *  FROM client ;""")
        print(curs.fetchall())

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as curs:
        if phone != None:
            curs.execute(""" SELECT c.client_id,first_name, last_name, email, phone_number FROM client AS c LEFT JOIN phone AS p ON
             c.client_id = p.client_id WHERE phone_number = %s ; """,
            (phone,))
            result = curs.fetchall()
        if first_name != None:
            curs.execute(""" SELECT c.client_id,first_name, last_name, email, phone_number FROM client AS c LEFT JOIN phone AS p ON c.client_id = p.client_id WHERE first_name = %s; """, (first_name,))
            result = curs.fetchall()

        if last_name != None:
            curs.execute(""" SELECT c.client_id,first_name, last_name,email, phone_number FROM client AS c LEFT JOIN phone AS p ON c.client_id = p.client_id WHERE last_name = %s; """,(last_name,))
            result = curs.fetchall()

        if email != None:
            curs.execute(""" SELECT c.client_id,first_name, last_name, email, phone_number FROM client AS c LEFT JOIN phone AS p ON c.client_id = p.client_id WHERE email = %s; """,(email,))

            result = curs.fetchall()

    if result :
        print(result)
    else:
        print('Данные не найдены')

with psycopg2.connect(database = 'netology_db', user= 'postgres', password = 'patata2') as conn:
    create_db(conn)
    add_client(conn,first_name='Ivan', last_name='Ivanov', email='ivanovivan@mail.ru')
    add_client(conn, first_name='Peter', last_name='Petrov',email= 'petrovpetr@mail.ru',phones =['111111111','222222222'])
    add_client(conn, first_name='Harry', last_name='Potter', email='harrypotter@mail.ru',phones = ['444444444'])
    add_client(conn, first_name='Sergey',last_name='H', email= 'sh@mail.ru',phones= ['444444444'])
    add_client(conn, first_name='Sergey',last_name='Ivanov', email='harrypotter@mail.ru', phones=['444444444'])
    add_client(conn, first_name='Sergey', last_name='Ivanov', email='sergivanov@mail.ru', phones=['555555555'])
    # print('Добавление телефонного номера')
    # add_phone(conn, int(input('id клиента: ')),input('Номер телефона: '))
    delete_phone(conn, 2, '222222222')
    delete_client(conn, 5)
    # delete_client(conn, 2)
    find_client(conn, last_name = 'Petrov')
    find_client(conn, first_name='Harry')
    find_client(conn, email='Harry')
    find_client(conn, email='ivanovivan@mail.ru')
    find_client(conn, phone='444444444')
    find_client(conn, phone='666666666')
    change_client(conn,2,first_name='Sandra',last_name='Bullok',phones=['999999999'])
conn.close()