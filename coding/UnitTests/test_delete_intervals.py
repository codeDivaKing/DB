

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from databricks.coding.delete_intervals import *

class TestDeleteIntervals(unittest.TestCase):
    def test_example(self):
        intervals = [[10,12],[13,16],[4,8]]
        index = 3  # remove covered[2] = 6
        result = Solution.deletIntervals(intervals, index)
        expected = [(4, 5), (7, 7), (10, 11), (13, 15)]
        self.assertEqual(result, expected)

    def test_remove_first_element(self):
        intervals = [(1, 3), (5, 7)]
        index = 0  # remove 1
        result = Solution.deletIntervals(intervals, index)
        expected = [(2, 3), (5, 7)]
        self.assertEqual(result, expected)

    def test_remove_last_element(self):
        intervals = [(1, 3), (5, 7)]
        index = 5  # remove 7
        result = Solution.deletIntervals(intervals, index)
        expected = [(1, 3), (5, 6)]
        self.assertEqual(result, expected)

    def test_remove_middle_element(self):
        intervals = [(1, 5)]
        index = 2  # remove 3
        result = Solution.deletIntervals(intervals, index)
        expected = [(1, 2), (4, 5)]
        self.assertEqual(result, expected)

    def test_remove_nonexistent_element(self):
        intervals = [(1, 3), (5, 7)]
        index = 10  # out-of-bounds index
        result = Solution.deletIntervals(intervals, index)
        expected = [(1, 3), (5, 7)]
        self.assertEqual(result, expected)


    def test_single_interval_remove_only_element(self):
        intervals = [(2, 2)]
        index = 0  # remove 2
        result = Solution.deletIntervals(intervals, index)
        expected = []
        self.assertEqual(result, expected)

    def test_empty_intervals(self):
        intervals = []
        index = 0
        # Should not raise, just return []
        result = Solution.deletIntervals(intervals, index)
        expected = []
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
