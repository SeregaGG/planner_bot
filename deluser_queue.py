import logging
class DeluserRow:
    def __init__(self):
        self.row = {}

    def add(self, uid, username):
        if uid in self.row.keys():
            if username in self.row[uid]:
                self.row[uid].remove(username)
            else:
                self.row[uid].append(username)
        else:
            self.row[uid] = [username]
        return self.row[uid]

    def pop(self, uid):
        deleted_row =  self.row.pop(uid, None)
        return deleted_row

    def get(self, uid):
        if uid in self.row.keys():
            return self.row[uid]
        return []
