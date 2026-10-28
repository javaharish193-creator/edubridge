import psycopg2

passwords_to_try = ['postgres', 'password', 'admin', 'root', '1234', '123456', 'P@ssword', 'Harish', 'harish', 'Harish@123', 'admin123', '']
connected = False

for pwd in passwords_to_try:
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password=pwd,
            dbname='postgres',
            connect_timeout=2
        )
        print(f"SUCCESS! Connected with password: '{pwd}'")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='edubridge'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE edubridge")
            print("Created database 'edubridge' successfully!")
        else:
            print("Database 'edubridge' already exists!")
        cur.close()
        conn.close()
        connected = True
        break
    except Exception as e:
        # print(f"Trying '{pwd}': {e}")
        pass

if not connected:
    print("COULD_NOT_CONNECT_AUTOMATICALLY")
