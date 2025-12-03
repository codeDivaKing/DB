# Implement a function that assigns each booking to a court such that:

# A court cannot host overlapping bookings.

# You have unlimited courts available.

# You must use the minimum number of courts.

# Return a list of assignments like:

import heapq

class BookingRecord:
    def __init__(self, id: int, start_time: int, finish_time: int):
        self.id = id
        self.start_time = start_time
        self.finish_time = finish_time

class Bookings:
    def __init__(self, courts: int):
        self.bookings = []
        self.courts = courts

    def assign_courts(self, bookings: list[BookingRecord]) -> list[tuple[int, int]]:
        bookings.sort(key=lambda x: x.start_time)
        heap = []
        available = list(range(self.courts))

        for b in bookings:
            while heap and heap[0][0] < b.start_time:
                _, court_id = heapq.heappop(heap)
                heapq.heappush(available, court_id)
            
            if available:
                court_id = heapq.heappop(available)
            else:
                _, court_id = heapq.heappop(heap)
            
            heapq.heappush(heap, (b.finish_time, court_id))
            self.bookings.append((b.id, court_id))
                

    def get_bookings(self) -> list[tuple[int, int]]:
        return self.bookings



bookings = Bookings(5)
bookings.assign_courts([
    BookingRecord(1, 1, 4),
    BookingRecord(2, 2, 8),
    BookingRecord(3, 3, 5),
    BookingRecord(4, 7, 9),
    BookingRecord(5, 6, 10),
    BookingRecord(6, 1, 3),
    BookingRecord(7, 4, 7),
    BookingRecord(8, 10, 12),
    BookingRecord(9, 5, 6),
    BookingRecord(10, 9, 11)
])

    
print(bookings.get_bookings())
