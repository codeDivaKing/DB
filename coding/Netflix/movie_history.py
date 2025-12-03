from sortedcontainers import SortedDict

class MovieHistory:
    def __init__(self):
        self.history = SortedDict()

    def add(self, movie_id, timestamp):
        if timestamp not in self.history:
            self.history[timestamp] = []
        self.history[timestamp].append(movie_id)

    def get_history(self):
        res = []
        for time in self.history.keys():
            for name in self.history[time]:
                res.append(name)
        return res

    def clear(self):
        self.history.clear()


# unit test
history = MovieHistory()
history.add("a", 1)
history.add("b", 2)
history.add("c", 3)
history.add("d", 4)
history.add("e", 5)
history.add("f", 6)
history.add("g", 7)
history.add("h", 8)
history.add("i", 9)
history.add("j", 10)
history.add("k", 11)
history.add("l", 12)
history.add("m", 13)
history.add("n", 14)
history.add("o", 15)
history.add("p", 16)
history.add("q", 17)
history.add("r", 18)
history.add("s", 19)
history.add("t", 20)
history.add("u", 21)
history.add("v", 22)
history.add("w", 23)
history.add("x", 24)
history.add("y", 25)
history.add("z", 26)

print(history.get_history())
