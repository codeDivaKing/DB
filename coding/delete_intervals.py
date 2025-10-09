# Array of intervals。给一个interval array,每个interval不相交。再给一个所有interval cover的list中的index。
# 要求给出删掉这个index所cover的element之后的interval array.
# 比如：
# 有这样一个array: [(4, 7), (10, 11), (13, 15)]，它所cover的list是: [4, 5, 6, 7, 10, 11, 13, 14, 15]。
# 如果index是2的话，把6从covered list中删掉，output是[(4, 5), (7,7), (10, 11), (13, 15)]。

from typing import List, Tuple

class Solution:
    @staticmethod
    def deletIntervals(self, intervals: List[List[int]], index: int) -> List[Tuple[int, int]]:
        ans = []
        count = 0
        intervals.sort(key=lambda x: x[0])
        for start, end in intervals:
            diff = end - start
            if count <= index <= (count + diff):
                if index == count and index == count + diff:
                    continue
                elif index == count:
                    ans.append((start + 1, end))
                elif count < index < count + diff:
                    ans.append((start, start + (index - count)-1))
                    ans.append((start + (index - count) + 1, end))
                else:
                    ans.append((start, end - 1))
            else:
                ans.append((start, end))
            count += diff + 1
        return ans
