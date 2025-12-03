from typing import List

def find_two_number_expressions(nums: List[int], target: int) -> List[str]:
    """
    Return all expressions of the form "a?b" where ? ∈ {+, -, *, /}
    such that applying the operation yields exactly `target`.

    Examples of valid output strings:
        "2+4", "4-2", "3*2", "6/3"
    """
    res = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if i == j:
                continue
            if nums[i] + nums[j] == target:
                res.append(f"{nums[i]}+{nums[j]}")
            if nums[i] - nums[j] == target:
                res.append(f"{nums[i]}-{nums[j]}")
            if nums[j] - nums[i] == target:
                res.append(f"{nums[j]}-{nums[i]}")
            if nums[i] * nums[j] == target:
                res.append(f"{nums[i]}*{nums[j]}")
            if nums[j] != 0 and nums[i] / nums[j] == target:
                res.append(f"{nums[i]}/{nums[j]}")
            if nums[i] != 0 and nums[j] / nums[i] == target:
                res.append(f"{nums[j]}/{nums[i]}")
    return res
            

# test
print(find_two_number_expressions([2, 4, 6], 6))
print(find_two_number_expressions([3, 3, 2], 6))
print(find_two_number_expressions([1, 5, 10], 5))
print(find_two_number_expressions([0, 6, -6], 0))
print(find_two_number_expressions([7, -1, 8], 7))
print(find_two_number_expressions([9, 3, 27], 3))
print(find_two_number_expressions([4, 2, 16], 8))
print(find_two_number_expressions([5, 2, 1], 10))
print(find_two_number_expressions([6, 2, -3], -1))
print(find_two_number_expressions([10, 5, 0], 2))
