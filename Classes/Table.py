class FloatTable(object):
    floats = []

    def __init__(self, floats):
        self.floats = floats

    def Add(self, flt):
        self.floats.append(flt)

    def RemoveAt(self, index):
        self.floats.pop(index)

    def StringList(self):
        lst = []
        for flt in self.floats:
            lst.append(str(flt))
        return lst

    def Insert(self, index, flt):
        self.floats.insert(index, flt)