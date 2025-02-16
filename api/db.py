import sqlite3
import re
DB_ROOT = "./dbs"

_db_connections = {}

class DbConnection():
    def __init__(self, username, connection):
        self.username = username
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.init_tables()

    def init_tables(self):
        tables_script: str = '''
        BEGIN;
        '''

        tables_script += '''
        CREATE TABLE IF NOT EXISTS user_info (
                username TEXT NOT NULL,
                password_hash TEXT NOT Null,
                role text NOT NULL,
                icon_file TEXT NOT NULL,
                date_added TEXT NOT NULL
                );
        '''

        tables_script += '''
        CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                title text NOT NULL,
                date_added TEXT NOT NULL
                );
        '''

        tables_script += '''
        CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                chat_id INTEGER NOT NULL,
                message_content text NOT NULL,
                sender text NOT NULL,
                date_added TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
                );
        '''

        tables_script += '''
        create index if not exists idx_chat_id on messages (chat_id);
        '''

        tables_script += '''
        COMMIT;
        '''
        self.cursor.executescript(tables_script)

    def close(self):
        global _db_connections

        del _db_connections[self.username]
        self.connection.close()

def GetUserDb(username):
    username = re.sub(r'[^a-zA-Z0-9_-]', '_', username)
    global _db_connections

    if username not in _db_connections:
        _db_connections[username] = DbConnection(username, sqlite3.connect(f"{DB_ROOT}/{username}.sqlite"))

    return _db_connections[username]


# mental illness
#class Db(object):
#    def __new__(cls):
#        if not hasattr(cls, 'instance'):
#            cls.instance = super(Db, cls).__new__(cls)
#        return cls.instance
#
#    def __init__(self):
#        self.connection = sqlite3.connect(DB_ROOT + "/main.sqlite")
#        self.cursor = self.connection.cursor()
#        self.init_tables() 
#
#    def attach_user(self,username):
#        user_path = Path(DB_ROOT + f"/{username}.sqlite")
#        if user_path.is_file():
#            self.create_user_db(user_path)
#
#        query: str = '''
#        ATTACH DATABASE ? AS ?
#        '''
#        self.cursor.execute(query, (str(user_path), username))
#
#        query = '''
#            CREATE TABLE IF NOT EXISTS test_user.staff (
#                    staff_id INTEGER PRIMARY KEY NOT NULL,
#                    username TEXT NOT NULL,
#                    role TEXT NOT NULL,
#                    password_hash TEXT NOT NULL,
#                    date_added TEXT NOT NULL
#                    ) 
#        '''
#        self.cursor.execute(query)
#
#    def create_user_db(self, user_path) -> None:
#        with user_path.open('w') as file:
#            file.write('')
#
#    def init_tables(self):
#        query: str ='''
#            CREATE TABLE IF NOT EXISTS staff (
#                    staff_id INTEGER PRIMARY KEY NOT NULL,
#                    username TEXT NOT NULL,
#                    role TEXT NOT NULL,
#                    password_hash TEXT NOT NULL,
#                    date_added TEXT NOT NULL
#                    ) 
#        '''
