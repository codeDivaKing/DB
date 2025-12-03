from typing import List

class ErrorRate:
    def __init__(self, errors: List[int]):
        self.errors = errors

    def is_healthy(self, t: int, window_size: int, threshold: int) -> bool:
        error = 0
        for i in range(t - window_size, t + window_size + 1):
            error += self.errors[i]
        
        return error < threshold

error_rate = ErrorRate([1,1,0,1,0,0,1,0,0,0])

print(error_rate.is_healthy(4, 2, 2))