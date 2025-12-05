# Scale-up 1: Wildcards with Ordered Matching

# Extend the router to support wildcard path patterns, where * matches exactly one path segment.

# Examples:

# router.addRoute("/foo", "foo")
# router.addRoute("/bar/*/baz", "bar")

# router.callRoute("/bar/a/baz")   // returns "bar"


# Wildcard matches should be checked in the order routes were added. The first matching route wins.

class Node:
    def __init__(self):
        self.static = {}
        self.wildcard = None
        self.value = None

class Router:
    def __init__(self):
        self.root = Node()

    def addRoute(self, path: str, result: str):
        node = self.root
        segments = path.split("/")

        for seg in segments:
            if seg != '*':
                if seg not in node.static:
                    node.static[seg] = Node()
                node = node.static[seg]
            else:
                if not node.wildcard:
                    node.wildcard = Node()
                node = node.wildcard
        node.value = result
    
    def callRoute(self, path: str) -> str:
        node = self.root
        segments = path.split("/")
        return self.match(segments, 0, node)

    def match(self, segments: list[str], idx: int, node: Node) -> str:
        if len(segments) == idx:
            return node.value
        s = segments[idx]

        if s in node.static:
            node = node.static[s]
            res = self.match(segments, idx + 1, node)
            if res is not None:
                return res
        
        if node.wildcard:
            res = self.match(segments, idx + 1, node.wildcard)
            if res is not None:
                return res
        return None
            
        

router = Router()
router.addRoute("/foo", "foo")
router.addRoute("/foo/baz", "exact")
router.addRoute("/foo/*", "wild")
router.addRoute("/bar/*/baz", "bar")

print(router.callRoute("/foo"))          # foo
print(router.callRoute("/foo/baz"))      # exact
print(router.callRoute("/foo/abc"))      # wild
print(router.callRoute("/bar/a/baz"))    # bar


# with params

class Node:
    def __init__(self):
        self.static = {}     # exact matches
        self.param = None    # :id
        self.wildcard = None # *
        self.value = None    # end-of-pattern value


class Router:
    def __init__(self):
        self.root = Node()

    def addRoute(self, path, result):
        segments = [s for s in path.split("/") if s]
        node = self.root

        for seg in segments:
            if seg == "*":
                if not node.wildcard:
                    node.wildcard = Node()
                node = node.wildcard
            elif seg.startswith(":"):      # param
                if not node.param:
                    node.param = Node()
                node = node.param
            else:                           # static
                if seg not in node.static:
                    node.static[seg] = Node()
                node = node.static[seg]

        node.value = result

    def callRoute(self, path):
        segments = [s for s in path.split("/") if s]
        return self._dfs(self.root, segments, 0)

    # depth-first search with precedence:
    # 1. static
    # 2. param
    # 3. wildcard
    def _dfs(self, node, segs, i):
        if i == len(segs):
            return node.value

        s = segs[i]

        # 1) Try static
        if s in node.static:
            res = self._dfs(node.static[s], segs, i + 1)
            if res is not None:
                return res

        # 2) Try param
        if node.param:
            res = self._dfs(node.param, segs, i + 1)
            if res is not None:
                return res

        # 3) Try wildcard
        if node.wildcard:
            res = self._dfs(node.wildcard, segs, i + 1)
            if res is not None:
                return res

        return None
