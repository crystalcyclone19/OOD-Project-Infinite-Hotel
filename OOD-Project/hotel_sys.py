from AVLTree import AVLTree
from HashRing import HashHelper

class customer:
    def __init__(self, c: int, s: int, guest_hash: int, room_no: int, node_id: int):
        self.customer_id = (c, s)
        self.guest_hash = HashHelper.get_guest_hash(c, s)
        self.room_no = self.calculate_room_no(c, s)
        self.node_id = None
        
    def calculate_room_no(self, c: int, s: int) -> int:
        a = c - 1
        b = s - 1
        return ((a + b) * (a + b + 1)) // 2 + b + 1