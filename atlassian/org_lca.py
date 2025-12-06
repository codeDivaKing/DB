class Group:
    def __init__(self, groupid: str):
        self.id = groupid
        self.members = set()
        self.parent = None
        self.children = set()
    
class companyArchive:
    def __init__(self):
        self.root = Group("root")
        self.groups = {"root": self.root}
        self.members = {}

    def addMember(self, memberid: str, groupid: str, parentid: str):
        if groupid in self.groups:
            group = self.groups[groupid]
            group.members.add(memberid)
            self.members[memberid] = group
        else:
            if parentid not in self.groups:
                raise ValueError("Parent group not found")
            parent_group = self.groups[parentid]
            new_group = Group(groupid)
            new_group.parent = parent_group
            new_group.members.add(memberid)
            parent_group.children.add(new_group)
            self.groups[groupid] = new_group
            self.members[memberid] = new_group
        

    def findMemberLCA(self, member1: str, member2: str):
        group1 = self.members[member1]
        group2 = self.members[member2]
        return self.findLCA(group1, group2)
    
    def findLCA(self, group1: str, group2: str):

        visited_groups = set([group1, group2])
        while group1 or group2:
            if group1:
                if group1 in visited_groups:
                    return group1
                visited_groups.add(group1)
                group1 = group1.parent

            if group2:
                if group2 in visited_groups:
                    return group2
                visited_groups.add(group2)
                group2 = group2.parent
                
        return self.root
    
    def findlca(self, members: list[str]):
        groups = [self.members[m] for m in members]

        curr = groups[0]
        for group in groups[1:]:
            curr = self.findLCA(curr, group)
            if curr is None:
                return None

        return curr
            

companyarchive = companyArchive()
# companyarchive.addMember("member1", "group1", "root")
# companyarchive.addMember("member2", "group2", "root")
# companyarchive.addMember("member3", "group3", "group1")
# companyarchive.addMember("member4", "group4", "group2")
# # give me 20 addMember calls
# companyarchive.addMember("member5", "group4", "group3")
# companyarchive.addMember("member6", "group5", "group4")
# companyarchive.addMember("member7", "group6", "group5")
# companyarchive.addMember("member8", "group7", "group6")
# companyarchive.addMember("member5", "group4", "group3")
# companyarchive.addMember("member6", "group5", "group4")

company = Group("Company")
eng = Group("Engineering")
backend = Group("Backend")
frontend = Group("Frontend")

company.children = [eng]
eng.parent = company
eng.children = [backend, frontend]
backend.parent = eng
frontend.parent = eng

companyarchive.members = {
    "Alice": backend,
    "Bob": frontend,
    "Carol": backend,
}

print(companyarchive.findMemberLCA("Alice", "Bob").id)


            


