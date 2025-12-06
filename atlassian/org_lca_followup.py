from collections import deque, defaultdict
import threading


# ─────────────────────────────────────────
# Group Node
# ─────────────────────────────────────────

class Group:
    def __init__(self, groupid: str):
        self.id = groupid
        self.members = set()
        self.parents = set()     # DAG support: multiple parents allowed
        self.children = set()

    def __repr__(self):
        return f"Group({self.id})"


# ─────────────────────────────────────────
# Org Snapshot (Immutable)
# ─────────────────────────────────────────

class OrgState:
    def __init__(self, version: int, groups, member_to_groups):
        self.version = version
        self.groups = groups                      # groupid -> Group object
        self.member_to_groups = member_to_groups  # member -> set[groupid]


# ─────────────────────────────────────────
# Company Archive (Main System)
# Snapshot-based, concurrency-safe
# ─────────────────────────────────────────

class CompanyArchive:
    def __init__(self):
        root = Group("root")

        # Initial snapshot
        self.current = OrgState(
            version=1,
            groups={"root": root},
            member_to_groups=defaultdict(set)
        )

        # Writers serialize; reads don't lock
        self.write_lock = threading.Lock()


    # ─────────────────────────────────────────
    # Snapshot deep-copy (copy-on-write)
    # ─────────────────────────────────────────
    def _copy_state(self):
        old_groups = self.current.groups

        # 1. Create new Group objects
        new_groups = {}
        for gid, g in old_groups.items():
            ng = Group(gid)
            ng.members = set(g.members)
            new_groups[gid] = ng

        # 2. Reconnect parent/child DAG pointers
        for gid, old_g in old_groups.items():
            new_g = new_groups[gid]
            new_g.parents = {new_groups[p.id] for p in old_g.parents}
            new_g.children = {new_groups[c.id] for c in old_g.children}

        # 3. Copy member -> groups mapping (shallow, safe since groupids don’t change)
        new_member_to_groups = defaultdict(set)
        for member, group_ids in self.current.member_to_groups.items():
            new_member_to_groups[member] = set(group_ids)

        return new_groups, new_member_to_groups


    # ─────────────────────────────────────────
    # Add Group
    # ─────────────────────────────────────────
    def add_group(self, groupid: str, parentid: str):
        with self.write_lock:
            groups, mem_map = self._copy_state()

            if groupid not in groups:
                new_g = Group(groupid)
                groups[groupid] = new_g
            else:
                new_g = groups[groupid]

            parent = groups.get(parentid)
            if not parent:
                raise ValueError(f"Parent group {parentid} not found")

            parent.children.add(new_g)
            new_g.parents.add(parent)

            # Publish new snapshot
            self.current = OrgState(self.current.version + 1, groups, mem_map)


    # ─────────────────────────────────────────
    # Add Member to a Group
    # (Creates group if not exist)
    # ─────────────────────────────────────────
    def add_member(self, memberid: str, groupid: str, parentid: str = None):
        with self.write_lock:
            groups, mem_map = self._copy_state()

            # Ensure group exists
            if groupid not in groups:
                g = Group(groupid)
                groups[groupid] = g

                if parentid is None or parentid not in groups:
                    raise ValueError("Must specify valid parent for new group")

                parent = groups[parentid]
                parent.children.add(g)
                g.parents.add(parent)
            else:
                g = groups[groupid]

            # Add member
            g.members.add(memberid)
            mem_map[memberid].add(groupid)

            # Publish new snapshot
            self.current = OrgState(self.current.version + 1, groups, mem_map)


    # ─────────────────────────────────────────
    # Multi-source BFS LCA for DAG
    # ─────────────────────────────────────────
    def find_lca_groups(self, groupids):
        state = self.current
        groups = state.groups

        # Convert ids → objects
        start_nodes = [groups[gid] for gid in groupids]

        queue = deque()
        visited = defaultdict(dict)

        # Initialize BFS sources
        for idx, node in enumerate(start_nodes):
            queue.append((node, idx, 0))
            visited[node][idx] = 0

        n = len(start_nodes)

        # Multi-source upward BFS
        while queue:
            node, idx, dist = queue.popleft()

            # First node reached by all sources = closest common ancestor
            if len(visited[node]) == n:
                return node, state.version

            for parent in node.parents:
                if idx not in visited[parent] or dist + 1 < visited[parent][idx]:
                    visited[parent][idx] = dist + 1
                    queue.append((parent, idx, dist + 1))

        return None, state.version


    # ─────────────────────────────────────────
    # LCA for multiple members (each may belong to multiple groups)
    # ─────────────────────────────────────────
    def find_lca_for_members(self, member_ids):
        state = self.current
        groupids = []

        for m in member_ids:
            if m not in state.member_to_groups:
                raise ValueError(f"Unknown member {m}")
            groupids.extend(state.member_to_groups[m])

        return self.find_lca_groups(groupids)


    # ─────────────────────────────────────────
    # Flat-org optimization (part d)
    # ─────────────────────────────────────────
    def find_lca_flat(self, member_ids):
        state = self.current
        groups = [list(state.member_to_groups[m])[0] for m in member_ids]

        if len(set(groups)) == 1:
            return state.groups[groups[0]], state.version

        return state.groups["root"], state.version


archive = CompanyArchive()

archive.add_group("Engineering", "root")
archive.add_group("Backend", "Engineering")
archive.add_group("Frontend", "Engineering")
archive.add_group("Platform", "Backend")

archive.add_member("Alice", "Backend")
archive.add_member("Bob", "Frontend")
archive.add_member("Carol", "Platform")

lca, version = archive.find_lca_for_members(["Alice", "Bob"])
print(lca.id, version)     # → Engineering, version number

lca2, v2 = archive.find_lca_groups(["Platform", "Backend"])
print(lca2.id, v2)         # → Backend
