import psycopg2


class pg_tools(object):
    host = '127.0.0.1'
    port = "54321"
    password = 'kimhom'
    database = "postgres"
    user = "postgres"
    cur = None

    def __init__(self):
        self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host,
                                     port=self.port)
        self.cur = self.conn.cursor()

    def select(self, sql):
        cur = self.cur
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def del_sql(self,sql):
        cur = self.cur
        cur.execute(sql)
        conn = self.conn
        conn.commit()
        print('delete successfully')

    def update(self, sql):
        cur = self.cur
        cur.execute(sql)
        conn = self.conn
        conn.commit()
        print("update successfully")

    def insert(self, sql):
        cur = self.cur
        try:
            cur.execute(sql)
            conn = self.conn
            conn.commit()
        except Exception as e:
            print(e)