class DeluserRow:
    def __init__(self):
        self.row = {}
        self.repr = {}

    def add(self, uid, username):
        no_at = username.replace('@', '')
        if uid in self.row.keys():
            if no_at in self.row[uid]:
                self.row[uid].remove(no_at)
                self.repr[uid].remove(username)
            else:
                self.row[uid].append(no_at)
                self.repr[uid].append(username)
        else:
            self.row[uid] = [no_at]
            self.repr[uid] = [username]
        return self.repr[uid]

    def pop(self, uid):
        deleted_row =  self.row.pop(uid, None)
        return deleted_row

    def get(self, uid):
        if uid in self.row.keys():
            return self.row[uid]
        return []
