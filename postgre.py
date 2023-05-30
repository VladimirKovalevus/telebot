
import config

import psycopg2
import psycopg2.extras

class PostgeHelper:
    cursor = None
    connection = None
    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            host=config.host,
            user =config.user,
            password=config.passowrd

          )
        self.cursor = self.connection.cursor()

        self.create_user_table()
        self.create_sheet_table()

    def __del__(self):
        self.cursor.close()
        self.connection.close()
        
    def create_user_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            chat_id TEXT  unique
          );""");
    def create_sheet_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS sheets (
            id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            name TEXT  unique,
            user_id uuid,
            status double precision
          );""");
    def insert_sheet(self,name,chat_id):
        self.cursor.execute("select * from users where chat_id = %s ",(str(chat_id),))
        user_id = self.cursor.fetchone();
        if user_id is None:
            self.insert_user(chat_id)
            self.cursor.execute("select id from users where chat_id = %s ",(str(chat_id),))
            user_id = self.cursor.fetchone()[0];
        else:
            user_id= user_id[0];

        self.cursor.execute("""insert into sheets values (default,%s,%s) on conflict do nothing;""",(name,user_id,));
    
    def insert_user(self,chat_id):
        self.cursor.execute("""insert into users values (default,%s) on conflict do nothing;""",(str(chat_id),));

    def get_all_sheets_by_name(self,chat_id):
        self.cursor.execute("""select sh.name from sheets  sh
        left join users us on us.id = sh.user_id
        where us.chat_id = %s""",(str(chat_id),))

        return self.cursor.fetchall()
    
    def get_all_sheets(self):
        self.cursor.execute("""select sh.name from sheets  sh
        left join users us on us.id = sh.user_id
        """)

        return self.cursor.fetchall()

    def update_statistic_by_name(self,status,name):
        self.cursor.execute("""update sheets
        set status = %s
        where name = %s""",(status,name,))
    def get_all_sheess(self,chat_id):
        self.cursor.execute("""select sh.name, sh.status from sheets  sh
        left join users us on us.id = sh.user_id
        where us.chat_id = %s""",(str(chat_id),))
        return self.cursor.fetchall()

