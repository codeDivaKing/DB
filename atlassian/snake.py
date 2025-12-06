from collections import deque


class Snake:
    def __init__(self, w: int, h: int):
        self.cur_position = (0, 0)
        self.w = w
        self.h = h
        self.queue = deque()
        self.positions = set([(0, 0)])
        self.queue.append(self.cur_position)
        self.grow_count = 5
        self.move_count = 0
        
    def move(self, direction: str):
        nx, ny = self.cur_position
        if direction == 'Up':
            ny -= 1
        if direction == 'Down':
            ny += 1
        if direction == 'Right':
            nx += 1
        if direction == 'Left':
            nx -= 1
        
        if nx < 0 or nx >= self.w or ny < 0 or ny >= self.h:
            return False

        self.move_count += 1
        if self.move_count == self.grow_count:
            self.move_count = 0
        else:
            tail_x, tail_y =  self.queue.popleft()
            self.positions.remove((tail_x, tail_y))

        if (nx, ny) in self.positions:
            return False 
        self.positions.add((nx, ny))
        self.queue.append((nx, ny))
        self.cur_position = (nx, ny)
        return True


snake = Snake(5, 5)
print(snake.move('Down'))
print(snake.move('Up'))
print(snake.move('Right'))
print(snake.move('Down'))
print(snake.move('Down'))
print(snake.move('Down'))
print(snake.move('Down'))
print(snake.move('Down'))