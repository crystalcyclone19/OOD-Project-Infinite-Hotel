from AVLTree import AVLTree
from HashRing import HashHelper

class Customer:
    def __init__(self, c: int, s: int):
        self.id = (c, s)
        self.hash = HashHelper.get_guest_hash(c, s)
        self.room_no = self.calculate_room_no(c, s)
        self.node_id = None
        
    def calculate_room_no(self, c: int, s: int) -> int:
        a = c - 1
        b = s - 1
        return ((a + b) * (a + b + 1)) // 2 + b + 1

class HotelSystem:
    def __int__(self, hash_ring):
        self.building_tree = AVLTree()
        self.customer_tree = AVLTree()
        self.ring = hash_ring

    def add_customer(self, c: int, s: int) -> bool:
        #check for dupes
        guest_hash = HashHelper.get_guest_hash(c, s)
        if self.customer_tree.search(guest_hash) is not None:
            return False

        #create customer
        new_cust = Customer(c, s)

        #ask ring for building and assigning the building to cust.node_id
        new_cust.node_id = self.ring.get_node_id(new_cust.hash)

        self.customer_tree.add(new_cust.hash)

        #new dict key
        target_node = self.customer_tree.search(new_cust.guest_hash)
        target_node.data["customer_obj"] = new_cust

        return True

    def add_group_customer(self, c: int, s_start: int, n: int) -> bool:
        if n <= 0: 
            return False

        for i in range(n):
            # calculate the hash for each guest to check for conflicts
                check_hash = HashHelper.get_guest_hash(c, s_start + i)
                if self.customer_tree.search(check_hash) is not None:
                    return False

        for i in range(n):
            self.add_customer(c, s_start + i)

        return True

    def remove_customer(self, c: int, s: int) -> bool:
        target_hash = HashHelper.get_guest_hash(c, s)

        