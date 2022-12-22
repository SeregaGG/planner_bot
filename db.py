import sqlite3
import re
import logging
import os
import getpass
import sql_queries as query

class Db():
    def __init__(self):
        try:
            self.conn = sqlite3.connect(os.getcwd()+'/'+os.path.join("db", "helper.db"))
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


    def fetch_tasks(self, uid='') -> list:
        if not uid:
            cmd = query.fetch_new_all
        elif uid == 'common':
            cmd = query.fetch_new_common
        else:
            cmd = query.fetch_new_by_uid(uid)
        self.cursor.execute(cmd)
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            ans ={
                'common': row[2],
                'done': row[1],
                'mes': row[0]
            }
            result.append(ans)
        return result


    def insert(self, table: str, column_values: dict):
        logging.info(column_values)
        columns = ', '.join(column_values.keys())
        values = tuple(column_values.values())
        placeholders =','.join('?'*len(column_values.keys()))
        s = query.insert_general(table, columns, placeholders)
        self.cursor.execute(s, values)
        self.conn.commit()
        return self.cursor.lastrowid


    def find_id_by_nick(self, nickname):
        self.cursor.execute(query.get_id_by_nick(nickname))
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
        logging.info(result)
        return result


    def list_ids(self):
        self.cursor.execute(query.list_uids)
        result = []
        for elem in self.cursor.fetchall():
            result.append(elem[0])
        logging.info(result)
        return result


    def list_usernames(self):
        self.cursor.execute(query.list_usernames)
        result = []
        for elem in self.cursor.fetchall():
            result.append(elem[0])
        return result


    def register_unauthorized(self, values: dict):
        self.insert("unauthorized_access", values)


    def get_usr_task_counter(self, user_id):
        s = query.get_usr_task_counter(user_id)
        logging.info(s)
        self.cursor.execute(s)
        return self.cursor.fetchone()[0]


    def set_usr_task_counter(self, user_id, counter):
        s = f'update usr set task_counter={counter} where tg_id = {user_id}'
        self.cursor.execute(s)
        self.conn.commit()


    def get_tid_from_tuid(self, uid, tuid):
        s = query.get_tid(uid)
        self.cursor.execute(s)
        ans = self.cursor.fetchall()
        logging.info(ans)
        if ans and (len(ans)-int(tuid)) >= 0:
            return ans[int(tuid)-1][0]
        else:
            return None


    def set_done(self, tid):
        s = f'update task set done = True  where task_id={tid}'
        self.cursor.execute(s)
        self.cursor.execute(s)
        logging.info(f"Just ticket out task {tid}")
        self.conn.commit()

    def is_admin(self, uid):
        s = f'select is_admin from usr where tg_id={uid}'
        self.cursor.execute(s)
        ans = self.cursor.fetchone()
        if ans:
            return ans[0]
        else:
            return None


    def get_tid_from_tnum(self, uid, task_num):
        s = query.tid_from_tnum(uid)
        self.cursor.execute(s)
        ans = self.cursor.fetchone()
        if ans:
            return ans[0]
        else:
            return None


    def make_oldcount_dict(self, tid_list):
        '''This loop creates a dict of users (keys) and the increment of
            usr.old_task_counter (value) which is returned as ans'''
        ans = {}

        for tid in tid_list:
            self.cursor.execute(query.get_uid_from_tid(tid))
            uid_l = self.cursor.fetchall()
            logging.info(f'task {tid} contains users: {uid_l}')
            self.cursor.execute(query.set_old_true(tid))
            for el in uid_l:
                if el[0] in ans.keys():
                    ans[el[0]] += 1
                else:
                    ans[el[0]] = 1
        self.conn.commit()
        logging.info(ans)
        return ans



    def make_evrth_old(self):
        self.cursor.execute('select task_id from task where old=false')
        l = self.cursor.fetchall()
        tid_list = []
        for el in l:
            tid_list.append(el[0])
        self.cursor.execute('update task set old=true')
        self.conn.commit()
        return self.make_oldcount_dict(tid_list)


    def make_old(self, virt_list):
        tid_list = []

        '''This loop transforms a list of task numbers that user sees
            into a list of corresponding task_ids in the database'''

        logging.info(f'virtual nums are {virt_list}')
        for virt in virt_list:
            self.cursor.execute(query.get_tid_from_new(virt))
            tid = self.cursor.fetchall()[0][0]
            tid_list.append(tid)
        logging.info(f'task_ids are {tid_list}')
        return self.make_oldcount_dict(tid_list)


    def count_all_tasks(self):
        self.cursor.execute('select count(task_id) from task where old=false')
        return self.cursor.fetchone()[0]

    def count_usr_tasks(self, uid):
        self.cursor.execute(query.count_usr_tasks(uid))
        return self.cursor.fetchone()[0]

    def increase_old_counter(self, uids_dict):
        uids = uids_dict.keys()
        for uid in uids:
            logging.info(f'uid = {uid}')
            self.cursor.execute(query.fetch_oldc(uid))
            res = self.cursor.fetchone()
            oldc = res[0]
            s = query.increase_oldc(oldc, uids_dict[uid], uid)
            self.cursor.execute(s)
            self.conn.commit()
        return 1


    def set_admin_up(self, uid):
        logging.info(uid)
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

    def get_task(self, tuid):
        self.cursor.execute(f'select task_name from task where task_id={tuid}')
        return self.cursor.fetchone()[0]

    def is_done(self, tid):
        self.cursor.execute(f'select done from task where task_id={tid}')
        return self.cursor.fetchone()[0]
