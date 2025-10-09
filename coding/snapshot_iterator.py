class SnapshotSet:
    def __init__(self, initial_elements=None):
        self.version = 1
        # Map from element to list of (operation, version) tuples
        self.history = {}
        
        if initial_elements:
            for elem in initial_elements:
                self.history[elem] = [('add', 1)]
    
    def add(self, e):
        """Add element to the set"""
        if e not in self.history:
            self.history[e] = []
        
        # Optimization: compress consecutive operations at same version
        if self.history[e] and self.history[e][-1][1] == self.version:
            if self.history[e][-1][0] == 'remove':
                # Remove the 'remove' at current version
                self.history[e].pop()
                return
        
        self.history[e].append(('add', self.version))
    
    def remove(self, e):
        """Remove element from the set"""
        if e not in self.history:
            return
        
        # Optimization: compress consecutive operations at same version
        if self.history[e] and self.history[e][-1][1] == self.version:
            if self.history[e][-1][0] == 'add':
                # Remove the 'add' at current version
                self.history[e].pop()
                return
        
        self.history[e].append(('remove', self.version))
    
    def contains(self, e):
        """Check if element is in current set"""
        if e not in self.history or not self.history[e]:
            return False
        
        # Check the last operation at current version
        last_op, last_version = self.history[e][-1]
        return last_op == 'add' and last_version <= self.version
    
    def iterator(self):
        """Return a snapshot iterator at current version"""
        snapshot_version = self.version
        self.version += 1  # Increment for future operations
        return SnapshotIterator(self.history, snapshot_version)


class SnapshotIterator:
    def __init__(self, history, version):
        self.history = history
        self.version = version
        self.elements = self._get_snapshot_elements()
        self.index = 0
    
    def _get_snapshot_elements(self):
        """Get all elements that existed at snapshot version"""
        result = []
        for elem, ops in self.history.items():
            # Find last operation <= snapshot version
            last_op = None
            for op, ver in ops:
                if ver <= self.version:
                    last_op = op
                else:
                    break
            
            # If last operation was 'add', element exists in snapshot
            if last_op == 'add':
                result.append(elem)
        
        return result
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.elements):
            elem = self.elements[self.index]
            self.index += 1
            return elem
        raise StopIteration


# Test with the example from the problem
if __name__ == "__main__":
    print("Example 1:")
    ss = SnapshotSet([1, 2, 3])
    ss.add(4)
    iter1 = ss.iterator()
    ss.remove(1)
    iter2 = ss.iterator()
    ss.add(6)
    
    print(f"iter1 (should be [1, 2, 3, 4]): {sorted(list(iter1))}")
    print(f"iter2 (should be [2, 3, 4]): {sorted(list(iter2))}")
    
    print("\nExample 2 (from comments):")
    ss2 = SnapshotSet()
    ss2.add(5)
    ss2.add(2)
    ss2.add(8)
    ss2.remove(5)
    it = ss2.iterator()  # Snapshot has [2, 8]
    ss2.add(1)
    print(f"contains(2): {ss2.contains(2)}")  # True
    ss2.remove(2)
    print(f"contains(2): {ss2.contains(2)}")  # False
    print(f"it elements (should be [2, 8]): {sorted(list(it))}")  # [2, 8]