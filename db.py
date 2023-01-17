import sqlite3
import re
import logging
import os
import getpass
import sql_queries as query

class Db():
    def __init__(self):
        try:
            path = os.getcwd()+'/'+os.path.join("db", "helper.db")
            self.conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        except Exception as e:
            logging.error(os.getcwd()+'/'+os.path.join("db", "helper.db"))
            logging.error(os.path.join("db", "helper.db"))
            raise sqlite3.OperationalError(e) 
        self.cursor = self.conn.cursor()
        self.check_db_exists()
        logging.basicConfig(level=logging.INFO)


    def check_db_exists(self):
        self.cursor.execute(query.check_db_exist)
        table_exists = self.cursor.fetchall()
        if table_exists:
            return
        with open("createdb.sql", "r") as f:
            #Creating new tables if DB is empty
            sql = f.read()
            self.cursor.executescript(sql)
            self.conn.commit()


    def get_table_size(self, table):
        self.cursor.execute(f'select count(1) from {table}')
        return self.cursor.fetchall()[0][0]


    def fetch_headers(self, uid='', limit=0, offset=0, sort='created_datetime') -> list:
        cmd = ''
        if sort == 'deadline':
            cmd = query.fetch_all_sorted(sort, limit, offset, self.find_id_by_nick(uid))
        else:
            if not uid:
                cmd = query.fetch_all(limit, offset, sort)
            elif uid == 'common':
                cmd = query.fetch_common(limit, offset, sort)
            else:
                cmd = query.fetch_by_uid(self.find_id_by_nick(uid), limit, offset, sort)
        logging.info(cmd)
        self.cursor.execute(cmd)
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            ans ={
                'task_id': row[0],
                'header': row[1],
                'done': row[2],
                'deadline': row[3]
            }
            result.append(ans)
        return result


    def get_task_by_tid(self, tid):
        self.cursor.execute(query.get_task_by_tid(tid))
        res = self.cursor.fetchone()
        return res


    def insert(self, table: str, column_values: dict):
        columns = ', '.join(column_values.keys())
        values = tuple(column_values.values())
        placeholders =','.join('?'*len(column_values.keys()))
        s = query.insert_general(table, columns, placeholders)
        self.cursor.execute(s, values)
        self.conn.commit()
        return self.cursor.lastrowid


    def find_id_by_nick(self, nickname):
        self.cursor.execute(query.get_id_by_nick(nickname.replace("@", '').lower()))
        return self.cursor.fetchone()[0]


    def list_nicks(self):
        s = query.list_nicks
        try:
            self.cursor.execute(s)
        except Exception as e:
            logging.error(e)
        result = []
        for elem in self.cursor.fetchall():
            result.append(elem[0])
        return result


    def list_ids(self):
        self.cursor.execute(query.list_uids)
        result = []
        for elem in self.cursor.fetchall():
            result.append(elem[0])
        return result


    def list_usernames(self):
        self.cursor.execute(query.list_usernames)
        result = []
        for elem in self.cursor.fetchall():
            result.append(elem[0])
        return result


    def register_unauthorized(self, values: dict):
        self.insert("unauthorized_access", values)


    def set_done(self, tid):
        s = f'update tasks set done = True  where task_id={tid}'
        self.cursor.execute(s)
        self.conn.commit()


    def is_admin(self, uid):
        s = f'select is_admin from usr where tg_id={uid}'
        self.cursor.execute(s)
        ans = self.cursor.fetchone()
        if ans:
            return ans[0]
        else:
            return None


    def count_usr_tasks(self, uid):
        q = query.count_usr_tasks(uid).replace('@', '').lower()
        self.cursor.execute(q)
        return self.cursor.fetchone()[0]


    def count_common_tasks(self):
        q = 'select count(*) from tasks where common=1'
        self.cursor.execute(q)
        return self.cursor.fetchone()[0]


    def set_admin_up(self, uid):
        self.cursor.execute(query.make_admin(uid))
        self.conn.commit()


    def set_admin_down(self, uid):
        self.cursor.execute(query.remove_admin(uid))
        self.conn.commit()


    def list_admins(self):
        self.cursor.execute(query.list_admins)
        ans = []
        for el in self.cursor.fetchall():
            ans.append(el[0])
        return ans


    def is_done(self, tid):
        self.cursor.execute(f'select done from tasks where task_id={tid}')
        return self.cursor.fetchone()[0]

    def delete_tid_from_logger(self, tid):
        self.cursor.execute(f'delete from logger_table where task_id={tid}')
        self.conn.commit()


    def delete_tid_from_tasks(self, tid):
        self.cursor.execute(f'delete from tasks where task_id={tid}')
        self.conn.commit()

    def is_owner(self, uid, tid):
        self.cursor.execute(f'select * from logger_table where task_id={tid} and tg_id={uid}')
        ans = self.cursor.fetchall()
        if ans:
            return 1
        return 0
