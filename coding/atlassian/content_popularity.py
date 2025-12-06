from collections import defaultdict
from sortedcontainers import SortedDict

class ContentPopularity:
    def __init__(self):
        self.pop = defaultdict(int)        # contentId → popularity
        self.freq = SortedDict()           # popularity → set of contentIds

    # Helper to add content to a frequency bucket
    def _add_to_freq(self, p, cid):
        if p not in self.freq:
            self.freq[p] = set()
        self.freq[p].add(cid)

    # Helper to remove content from a frequency bucket
    def _remove_from_freq(self, p, cid):
        bucket = self.freq[p]
        bucket.remove(cid)
        if not bucket:
            del self.freq[p]              # remove empty key

    # -------------------------------------------------------

    def increasePopularity(self, contentid: int):
        old_p = self.pop[contentid]
        new_p = old_p + 1
        self.pop[contentid] = new_p

        # Remove from old bucket
        if old_p > 0:
            self._remove_from_freq(old_p, contentid)

        # Add to new bucket
        self._add_to_freq(new_p, contentid)

    def decreasePopularity(self, contentid: int):
        if contentid not in self.pop:
            return    # silently ignore (reasonable design)
        
        old_p = self.pop[contentid]
        new_p = max(0, old_p - 1)
        self.pop[contentid] = new_p

        # Remove from old frequency bucket
        if old_p > 0:
            self._remove_from_freq(old_p, contentid)

        # If still positive, insert into new bucket
        if new_p > 0:
            self._add_to_freq(new_p, contentid)

    # -------------------------------------------------------

    def getMostPopularContent(self):
        if not self.freq:
            return -1

        # peekitem(-1) → last (max key)
        max_pop, content_set = self.freq.peekitem(-1)

        if max_pop <= 0:
            return -1

        # if ties, return any one (or min(content_set) if deterministic needed)
        return next(iter(content_set))

contentPopularity = ContentPopularity()

contentPopularity.increasePopularity('1')
contentPopularity.increasePopularity('1')
contentPopularity.increasePopularity('2')
contentPopularity.increasePopularity('1')

contentPopularity.increasePopularity('2')
contentPopularity.increasePopularity('2')
contentPopularity.increasePopularity('1')

print(contentPopularity.getMostPopularContent())

contentPopularity.decreasePopularity('1')
contentPopularity.decreasePopularity('1')

contentPopularity.decreasePopularity('1')

contentPopularity.decreasePopularity('1')


print(contentPopularity.getMostPopularContent())
