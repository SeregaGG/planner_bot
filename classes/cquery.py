class Cquery:
    def __init__(self, values = {}, cmd = ''):
        self.command = cmd
        self.args = {
            'offset': 'o',
            'owneruid': 'u',
            'tid':'t',
            'btntid': 'n',
            'order':'r',
            'dir':'d',
            'btn_tid': 'b',
            'userid': 'i',
            'is_admin': 'a',
            'state': 's'
        }
        self.sgra = {
            'o': 'offset',
            'u': 'owneruid',
            't': 'current_tid',
            'r': 'order',
            'd': 'dir',
            'b': 'btn_tid',
            'i': 'userid',
            'a':'is_admin',
            'n': 'btntid',
            't': 'tid',
            's': 'state'
        }
        self.values = values

    def generatecq(self):
        s = self.command
        for arg in self.values.keys():
            s+=f'_{self.args[arg]}{self.values[arg]}'
        return s


    def decodecq(self, callback):
        args_list = callback.split('_')
        self.command = args_list.pop(0)
        for elem in args_list:
            self.values[self.sgra[elem[0]]] = int(elem[1:])
        return self.values
         

