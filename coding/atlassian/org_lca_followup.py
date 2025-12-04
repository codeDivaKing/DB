from collections import deque, defaultdict

class Group:
    def __init__(self, groupid: str):
        self.id = groupid
        self.members = set()
        self.parents = set()
        self.children = set()
    
class companyArchive:
    def __init__(self):
        self.root = Group("root")
        self.groups = {"root": self.root}
        self.members = defaultdict(set)

    def addMember(self, memberid: str, groupid: str, parentid: str):
        if groupid in self.groups:
            group = self.groups[groupid]
            group.members.add(memberid)
            self.members[memberid].add(groupid)
        else:
            if parentid not in self.groups:
                raise ValueError("Parent group not found")
            parent_group = self.groups[parentid]
            new_group = Group(groupid)
            self.groups[groupid] = new_group
            new_group.members.add(memberid)
            parent_group.children.add(new_group)
            new_group.parents.add(parent_group)
            self.members[memberid].add(groupid)

    def addGroup(self, groupid: str, parentid: str):
        if groupid not in self.groups:
            new_group = Group(groupid)
            self.groups[groupid] = new_group
            if parentid not in self.groups:
                raise ValueError("Parent group not found")
            parent_group = self.groups[parentid]
            parent_group.children.add(new_group)
            new_group.parents.add(parent_group)
            

    def findLCA(self, member_group_ids: list[str]):
        queue = deque()
        visited = defaultdict(dict)

        # Initialize BFS from each employee's group
        for idx, groupid in enumerate(member_group_ids):
            group = self.groups[groupid]       # Convert id → Group object
            queue.append((group, idx, 0))
            visited[group][idx] = 0            # Must use Group object as key

        # Multi-source upward BFS
        while queue:
            group, idx, depth = queue.popleft()

            # If this group has been reached from all employees → LCA
            if len(visited[group]) == len(member_group_ids):
                return group

            # Traverse upward
            for parent in group.parents:
                if idx not in visited[parent] or depth + 1 < visited[parent][idx]:
                    visited[parent][idx] = depth + 1
                    queue.append((parent, idx, depth + 1))

        return None

            
        

            

        
        

    


companyarchive = companyArchive()
companyarchive.addMember("member1", "group1", "root")
companyarchive.addMember("member2", "group2", "root")
companyarchive.addMember("member3", "group3", "group1")
companyarchive.addMember("member4", "group4", "group2")
# give me 20 addMember calls
companyarchive.addMember("member5", "group4", "group3")
companyarchive.addMember("member6", "group5", "group4")
companyarchive.addMember("member7", "group6", "group5")
companyarchive.addMember("member8", "group7", "group6")
companyarchive.addMember("member5", "group4", "group3")
companyarchive.addMember("member6", "group5", "group4")

print(companyarchive.findLCA(["group4", "group7"]).id)


            


