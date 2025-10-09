class SnapshotSet():
    def __init__(self, elements=None):
        self.history = {}
        self.version = 1

        if elements:
            for e in elements:
                self.history[e] = [('add', 1)]
        


    def add(self, e):
        if e not in self.history:
            self.history[e] = []
        
        if self.history[e] and self.history[e][-1][1] == self.version and self.history[e][-1][0] == 'remove':
            self.history[e].pop()
            return

        self.history[e].append(('add', self.version))
    
    def remove(self, e):
        if e not in self.history:
            return

        if self.history[e] and self.history[e][-1][1] == self.version and self.history[e][-1][0] == 'add':
            self.history[e].pop()
            return

        self.history[e].append(('remove', self.version))

    def contains(self, e):
        if e not in self.history or not self.history[e]:
            return False

        last_op, last_version = self.history[e][-1]
        return last_op == 'add' and last_version <= self.version
    
    def iterator(self):
        snapshot_version = self.verison
        self += 1
        return SnapshotIterator(self.history, snapshot_version)
    
class SnapshotIterator():
    def __init__(self, history, version):
        self.version = version
        self.history = history
        self.elements = self.get_elements()
        self.index

    def get_elements(self):
        res = []
        for k, ops in self.history.items():
            last_op = ""
            for op, ver in ops:
                if ver <= self.version:
                    last_op = op
                else:
                    break
            if last_op == 'add':
                res.append(k)
        return res
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.elements):
            ele = self.elements(self.index)
            self.index += 1
            return ele
        raise StopIteration
    
