# 大概内容就是实现一个in memory 的 文件管理系统,

# 支持增删改查, 以及支持 version, 难度不高
class Node:
    def __init__(self):
        self.children = {}       # name -> Node
        self.is_file = False
        self.content = ""
        self.versions = []       # list of {"version": x, "content": str}
        self.version_counter = 0


class FileSystem:

    def __init__(self):
        self.root = Node()

    # --------------------------------------
    # Helper: traverse or create directories
    # --------------------------------------
    def _traverse(self, path: str, auto_create=False) -> Node:
        if path == "/":
            return self.root
        
        cur = self.root
        parts = path.split("/")[1:]   # skip first ""
        
        for name in parts:
            if name not in cur.children:
                if not auto_create:
                    raise FileNotFoundError(path)
                cur.children[name] = Node()
            cur = cur.children[name]
        return cur

    # -----------------------------
    # LS
    # -----------------------------
    def ls(self, path: str):
        node = self._traverse(path)
        if node.is_file:
            return [path.split("/")[-1]]
        return sorted(node.children.keys())

    # -----------------------------
    # MKDIR
    # -----------------------------
    def mkdir(self, path: str):
        self._traverse(path, auto_create=True)

    # -----------------------------
    # ADD CONTENT (append)
    # -----------------------------
    def addContentToFile(self, filePath: str, content: str):
        node = self._traverse(filePath, auto_create=True)
        if not node.is_file:
            node.is_file = True
        
        node.content += content
        node.version_counter += 1
        node.versions.append({
            "version": node.version_counter,
            "content": node.content
        })

    # -----------------------------
    # READ CONTENT (latest)
    # -----------------------------
    def readContentFromFile(self, filePath: str) -> str:
        node = self._traverse(filePath)
        return node.content

    # -----------------------------
    # READ SPECIFIC VERSION
    # -----------------------------
    def readVersion(self, filePath: str, version_id: int) -> str:
        node = self._traverse(filePath)
        for v in node.versions:
            if v["version"] == version_id:
                return v["content"]
        raise ValueError("Version not found")

    # -----------------------------
    # UPDATE (overwrite file)
    # -----------------------------
    def update(self, filePath: str, new_content: str):
        node = self._traverse(filePath, auto_create=True)
        node.is_file = True
        node.content = new_content

        node.version_counter += 1
        node.versions.append({
            "version": node.version_counter,
            "content": new_content
        })

    # -----------------------------
    # DELETE (file or empty directory)
    # -----------------------------
    def delete(self, path: str):
        if path == "/":
            raise ValueError("cannot delete root")

        parts = path.split("/")[1:]
        parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
        name = parts[-1]

        parent = self._traverse(parent_path)
        if name not in parent.children:
            raise FileNotFoundError(path)

        node = parent.children[name]

        # If directory, must be empty to delete
        if not node.is_file and node.children:
            raise ValueError("Directory not empty")

        del parent.children[name]
