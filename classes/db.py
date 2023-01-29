import sqlite3
import re
import logging
import os
import getpass
from datetime import datetime, date
from constants.enums import SortType, TaskState



class Db():

    def __init__(self):
        try:
            path = os.getcwd()+'/'+os.path.join("db", "helper.db")
            detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
            self.conn = sqlite3.connect(path, detect_types=detect_types)
        except Exception as e:
            raise sqlite3.OperationalError(e)
        self.cursor = self.conn.cursor()
        self.check_db_exists()
        self.motherchat = 0


    def check_db_exists(self):
        check_db_exist = "SELECT name FROM sqlite_master WHERE type='table' AND name='usr'"
        self.cursor.execute(check_db_exist)
        table_exists = self.cursor.fetchall()
        if table_exists:
            return
        with open("createdb.sql", "r") as f:
            #Creating new tables if DB is empty
            sql = f.read()
            self.cursor.executescript(sql)
            self.conn.commit()


    def where_chain(self, where_dict, operator='and'):
        where = []
        for el in where_dict.keys():
            where.append(f'{el}={where_dict[el]}')
        operator = f' {operator} '
        return operator.join(where)


    def get_table_size(self, table, filtr = {}, join=''):
        s = f'select count(1) from {table}'
        if join:
            s+= f' {join}'
        if filtr:
            s+= f" where {self.where_chain(filtr, 'and')}"
        self.cursor.execute(s)
        return self.cursor.fetchall()[0][0]


    def sorted_headers(self, uid, limit, offset, sort) -> list:
        args = ['tasks.task_id', 'header', 'deadline', 'state']
        cmd = f"select {','.join(args)} from tasks"
        if sort == SortType.COMMON:
            cmd += f' where  common = 1'
        elif sort == SortType.DEADLINE:
            join=f" join logger_table on logger_table.task_id=tasks.task_id"\
                    f" where logger_table.tg_id={uid}"
            cmd += join
        elif sort == SortType.SETTER:
            cmd += f" where creator = {uid}"
        cmd += f" order by createdtime desc"
        if limit:
            cmd += f' limit {limit} offset {limit*offset}'
        self.cursor.execute(cmd)
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            ans = {}
            for i in range(len(args)):
                if '.' in args[i]:
                    args[i] = args[i].split('.')[1]
                ans[args[i]] = row[i]
            result.append(ans)
        return result


    def insert(self, table: str, column_values: dict):
        columns = ', '.join(column_values.keys())
        values = tuple(column_values.values())
        placeholders =','.join('?'*len(column_values.keys()))
        s = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(s, values)
        self.conn.commit()
        return self.cursor.lastrowid


    def update(self, table: str, column_values: dict, filtr: dict = {}):
        cols = []
        for key in column_values.keys():
            cols.append(f'{key}=?')
        columns = ', '.join(cols)
        cols = []
        if filtr:
            where = self.where_chain(filtr, 'and')
        values = tuple(column_values.values())
        s = f'update {table} set {columns} where {where}'
        self.cursor.execute(s, values)
        self.conn.commit()


    def delete(self, table, where):
        s = f'delete from {table} where {where[0]}={where[1]}'
        self.cursor.execute(s)
        self.conn.commit()


    def select_request(self, table: str, columns: list, filtr: dict = {}, offset=0, limit=0):
        s = f"select {','.join(columns)} from {table}"
        if filtr:
            where = self.where_chain(filtr, 'and')
            s+= f" where {where}"
        if limit:
            s += f" limit {limit} offset {offset}"
        self.cursor.execute(s)
        raw = self.cursor.fetchall()
        return raw


    def get_table_column(self, table: str, column: str, filtr: dict = {}, offset=0, limit=0):
        raw = self.select_request(table, [column], filtr, offset, limit)
        response = []
        for elem in raw:
            response.append(elem[0])
        return response


    def get_table_row(self, table: str, columns: list, filtr: dict = {}, offset=0, limit=0):
        raw = self.select_request(table, columns, filtr, offset, limit)
        response = {}
        if columns[0] != '*':
            for i in range(0, len(columns)):
                response[columns[i]] = raw[0][i]
        else:
            return raw[0]
        return response


    def get_table_rows(self, table: str, columns: list, filtr: dict = {}, offset=0, limit=0):
        raw = self.select_request(table, columns, filtr, offset, limit)
        response = []
        if columns[0] != '*':
            for j in range(0, len(raw)):
                res_dict = {}
                for i in range(0, len(columns)):
                    res_dict[columns[i]] = raw[j][i]
                response.append(res_dict)
        else:
            return raw[0]
        return response


    def username_to_id(self, username: str = '', user_list: list = []):
        s = 'select id from usr where '
        if not username and not user_list:
            raise ValueError("At least one of the parameters must be set")
        elif username:
            end = f"username = '{username}'"
        else:
            phrase_list = []
            for u in user_list:
                phrase_list.append(f"username = '{u}'")
            end = ' or '.join(phrase_list)
        s += end
        self.cursor.execute(s)
        if username:
            return self.cursor.fetchone()[0]
        else:
            response = {}
            ans = self.cursor.fetchall()
            for i in range(0, len(user_list)):
                response[user_list[i]] = ans[i][0]
            return response


    def id_to_username(self, uid: str = '', uid_list: list = []):
        s = 'select username from usr where '
        if not uid and not uid_list:
            raise ValueError("At least one of the parameters must be set")
        elif uid:
            end = f"id = '{uid}'"
        else:
            phrase_list = []
            for u in uid_list:
                phrase_list.append(f"id = '{u}'")
            end = ' or '.join(phrase_list)
        s += end
        self.cursor.execute(s)
        if uid:
            return self.cursor.fetchone()[0]
        else:
            response = []
            ans = self.cursor.fetchall()
            for i in ans:
                response.append(i[0])
            return response


    def user_stats(self, where='', uid = ''):
        cmd = f"select count(1) from tasks"
        join=f"join logger_table on logger_table.task_id=tasks.task_id where logger_table.tg_id={uid}"
        if uid and where:
            s = f'{cmd} {join} and {where}'
        elif uid and not where:
            s = f'{cmd} {join}'
        elif where and not uid:
            s = f'{cmd} where {where}'
        else:
            s = f'{cmd}'
        self.cursor.execute(s)
        ans = self.cursor.fetchone()
        return ans[0]


    def count_active(self, uid='', order=SortType.CREATION):
        a_s = TaskState.AWAITING_START.value
        i_p = TaskState.IN_PROCESS.value
        if order != SortType.SETTER:
            where = f'(tasks.state = {a_s} or tasks.state = {i_p})'
        else:
            where = f'creator = {uid}'
            uid = ''
        return self.user_stats(where, uid)

    def count_inproc(self, uid='', order=SortType.CREATION):
        i_p = TaskState.IN_PROCESS.value
        where = f'tasks.state = {i_p}'
        if order == SortType.SETTER:
            where += f' and creator="{uid}"'
        return self.user_stats(where, uid)


    def count_done(self, uid='', order=SortType.CREATION):
        d = TaskState.DONE.value
        where = f'tasks.state = {d}'
        if order == SortType.SETTER:
            where += f' and creator = {uid}'
        return self.user_stats(where, uid)


    def list_admins(self):
        s = 'select id, username, admin from usr where blacklist = 0'
        self.cursor.execute(s)
        response = self.cursor.fetchall()
        ans = []
        for row in response:
            ans.append({'id':row[0], 'username':row[1], 'admin':row[2]})
        return ans

    def blacklist(self):
        return self.get_table_column('usr', 'tg_id', {'blacklist': 1})

