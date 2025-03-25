import sqlite3
import re
import datetime
import os.path
from .classes import UserInfo
from .error import UserNotInDbError
_db_connections = {}
DB_ROOT = "./dbs"

create_user_query: str = '''
insert into user_info values (?,?,?,?,?)
'''

class DbConnection():
    def __init__(self, username: str):
        self.username = username
        self.connection = sqlite3.connect(f"{DB_ROOT}/{username}.sqlite")
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

        if self.username in _db_connections:
            del _db_connections[self.username]
        self.connection.close()
        
    def get_info(self) -> UserInfo:
        user_info: UserInfo
        query: str = '''
        select * from user_info;
        '''
        res = self.cursor.execute(query).fetchone()
        user_info = UserInfo(
                username=res[0],
                password_hash=res[1],
                role=res[2],
                icon_file=res[3],
                date_added=res[4],
                )
        return user_info


def CheckBanned(username) -> bool:
    return re.search(r'[^a-zA-Z0-9_-]', username) != None

def GetUserDb(username) -> DbConnection | None:
    global _db_connections

    if username in _db_connections:
        return _db_connections[username]

    if os.path.isfile(f"{DB_ROOT}/{username}.sqlite"):
        return DbConnection(username)

    return None

def CreateUserDb(user_info: UserInfo) -> DbConnection:
    username = user_info.username
    password_hash = user_info.password_hash
    role = user_info.role
    icon_file = user_info.icon_file
    date_added = datetime.datetime.now().isoformat()

    global _db_connections, create_user_query
    _db_connections[username] = DbConnection(username)
    _db_connections[username].cursor.execute(create_user_query, (
        username,
        password_hash,
        role,
        icon_file,
        date_added
        ))
    _db_connections[username].connection.commit()
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
