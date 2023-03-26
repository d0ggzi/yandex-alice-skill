import psycopg2
from dbconfig import HOST, PORT, dbname, user, password



class DataBase:
    def __init__(self):
        try:
            conn = psycopg2.connect(
                host=HOST,
                port=PORT,
                sslmode="require",
                dbname=dbname,
                user=user,
                password=password,
                target_session_attrs="read-write"
            )
            conn.autocommit = True

            self.conn = conn
        except Exception as exception:
            print(exception)


    def create_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE answers(
                id VARCHAR(80) PRIMARY KEY,
                text VARCHAR(1024)
                );"""
            )

        print("TABLE CREATED")


    def insert(self, id, text):
        with self.conn.cursor() as cursor:
            cursor.execute(f"""
            INSERT INTO answers(id, text) VALUES ('{id}', '{text}');
            """)

            print("INSERTED")

    def update_answer(self, id, text):
        with self.conn.cursor() as cursor:
            cursor.execute(f"""
            UPDATE answers SET text = '{text}' WHERE id = '{id}';
            """)

    def get_answer(self, id): 
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT text FROM answers WHERE id = '{id}';")

                return cursor.fetchone()[0]
        except:
            return ""
        

    def delete_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("DROP TABLE answers")

            print("DETETED")


    def close_conn(self):
        self.conn.close()

if __name__ == "__main__":
    db = DataBase()
    # db.create_table()
    # db.insert("C68B87AAC79F91ABD8984C20696B0FD59B4E7DB92FBE6A4A7E010603B7F4F3E4", "Привет!!!")
    db.update_answer("C68B87AAC79F91ABD8984C20696B0FD59B4E7DB92FBE6A4A7E010603B7F4F3E4", "Hello!!!")
    print(db.get_answer("C68B87AAC79F91ABD8984C20696B0FD59B4E7DB92FBE6A4A7E010603B7F4F3E4"))

