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
    def __init__(self, hash_ring):
        self.building_tree = AVLTree()
        self.customer_tree = AVLTree()
        self.ring = hash_ring

    def _get_all_customers(self, node, cust_list):
        if node is not None:
            self._get_all_customers(node.left, cust_list)
            if "customer_obj" in node.data:
                cust_list.append(node.data["customer_obj"])
            self._get_all_customers(node.right, cust_list)

    def add_customer(self, c: int, s: int) -> bool:
        # check for dupes
        guest_hash = HashHelper.get_guest_hash(c, s)
        if self.customer_tree.search(guest_hash) is not None:
            return False

        # create customer
        new_customer = Customer(c, s)

        # ask ring for building and assigning the building to cust.node_id
        new_customer.node_id = self.ring.get_node_id(new_customer.hash)

        self.customer_tree.add(new_customer.hash)

        # new dict key
        target_node = self.customer_tree.search(new_customer.hash)
        target_node.data["customer_obj"] = new_customer

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

        if self.customer_tree.search(target_hash) is None:
            return False

        self.customer_tree.remove(target_hash)
        return True

    def search_customer_by_id(self, c: int, s: int):
        target_hash = HashHelper.get_guest_hash(c, s)
        target_customer = self.customer_tree.search(target_hash)

        if target_customer is None:
            return None

        return target_customer.data["customer_obj"]

    def search_customer_by_room(self, node_id: int, room_no: int):
        all_customers = []
        self._get_all_customers(self.customer_tree.root, all_customers)

        for customer in all_customers:
            if customer.node_id == node_id and customer.room_no == room_no:
                return customer

        return None

    def get_customers(self) -> dict:
        all_customers = [] 
        self._get_all_customers(self.customer_tree.root, all_customers)

        all_customers.sort(key=lambda x: (x.node_id, x.room_no))

        result_dict = {}
        for customer in all_customers:
            result_dict[str(customer.hash)] = str(customer.node_id)

        return result_dict