

from collections import defaultdict

class AgentVote:
    def __init__(self):
        self.votes = {}
        self.votes_month = [defaultdict(str) for _ in range(12)]

    def vote(self, id: str, vote: int):
        if vote < 0 or vote > 5:
            raise ValueError("Vote must be between 0 and 5"
            )
        if id in self.votes:
            sum, count = self.votes[id]
            self.votes[id] = (sum * count  + vote, count + 1)
        else:
            self.votes[id] = (vote, 1)
    
    def addVotes(self, votes: list[list[str, int, str]]):
        for id, vote, month in votes:
            if id in self.votes_month[month]:
                sum, count = self.votes_month[month][id]
                self.votes_month[month][id] = (sum * count + vote, count + 1)
            else:
                self.votes_month[month][id] = (vote, 1)
        
    def get_avg_month(self) -> list[(str, float)]:
        res = []
        for month in range(12):
            for id, (sum, count) in self.votes_month[month].items():
                avg = sum/count
                res.append((id, avg, count))
        res.sort(key=lambda x: (-x[1], -x[2], x[0]))
        return res

    def get_avg(self) -> list[(str, float)]:
        res = []
        for id, (sum, count) in self.votes.items():
            avg = sum/count
            
            res.append((id, avg, count))
        res.sort(key=lambda x: (-x[1], -x[2], x[0]))
        return res

    def export_month_avg(self, month: str):
        if mont not in self.votes_month:
            return None

        export_data = {}
        for id, sum, count in self.votes_month[month].items():
            avg = sum/count
            export_data[id] = (avg, count)
        
        return json.dumps(export_data)

if __name__ == "__main__":
    agent = AgentVote()
    agent.vote("a", 1)
    agent.vote("a", 2)
    agent.vote("b", 2)
    agent.vote("b", 1)
    agent.vote("c", 3)
    agent.vote("c", 3)
    agent.vote("c", 3)
    agent.addVotes([("a", 2, 1), ("b", 2, 1), ("c", 3, 1)])

    
    print(agent.get_avg(), agent.get_avg_month())
