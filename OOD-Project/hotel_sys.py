from AVLTree import AVLClassTree, AVLNormalTree
from HashRing import HashHelper, HashRing, HashModN
from pydantic import BaseModel

import time

class Customer:
    def __init__(self, c: int, s: int):
        self.id = (c, s)
        self.room_no = None
        self.node_id = None
        self.hash    = None

    def __str__(self):
        return (f"Customer(id={self.id}, room_no={self.room_no}, "
                f"node_id={self.node_id}, hash={self.hash})")

class MovedCustomer(BaseModel):
    id:tuple
    room_no:int
    old_node_id:int
    new_node_id:int

class BuildingWithRoom(BaseModel):
    building_id:int
    room_no:int
      





class HotelSystem:
    def __init__(self, number_of_virtual: int, building_salt: str,customer_salt: str, hash_type: str = 'consistent'):
        if hash_type == "consistent":
            self.ring = HashRing(number_of_virtual, building_salt)
        elif hash_type == "mod_n":
            self.ring = HashModN()
        
        self.building_tree = AVLNormalTree()
        self.customer_tree = AVLClassTree()
        self.customer_salt = customer_salt

    def calculate_room_no(self, c: int, s: int) -> int:
        # cantor pairing
        a = c - 1
        b = s - 1
        return ((a + b) * (a + b + 1)) // 2 + b + 1

    def _get_all_customers(self,node,customers_list):
        # in-order traversal
        if node is not None:
            self._get_all_customers(node.left, customers_list)
            # extract the customer object
            if node.data is not None:
                customers_list.append(node.data)
            self._get_all_customers(node.right, customers_list)

    def add_customer(self, c: int, s: int) -> bool:
        # check for dupes
        guest_hash = HashHelper.get_guest_hash(c, s, self.customer_salt)
        if self.customer_tree.search(guest_hash) is not None:
            print(f"[INVALID] add_customer failed: Guest {(c, s)} already exists in the system.")
            return False
        
        # create customer
        new_customer = Customer(c, s)

        customer_hash = HashHelper.get_guest_hash(c, s,self.customer_salt)
        customer_node_id = self.ring.get_node_id(customer_hash)
        customer_room = self.calculate_room_no(c,s)

        new_customer.hash = customer_hash
        new_customer.node_id = customer_node_id
        new_customer.room_no = customer_room

        # add into customer tree
        self.customer_tree.add(new_customer)       

        return True

    def add_group_customer(self, c: int, s: int, n: int) -> bool:
        # invalid group size
        if n <= 0: 
            print(f"[INVALID] add_group_customer failed: Invalid group size (n={n}).")
            return False

        for i in range(n):
            # calculate the hash for each guest to check for conflicts
            check_hash = HashHelper.get_guest_hash(c, s + i,self.customer_salt)
            
            if self.customer_tree.search(check_hash) is not None:
                print(f"[INVALID] add_group_customer failed: Conflict at guest {(c, s + i)}.")
                return False

        # adding process
        for i in range(n):
            self.add_customer(c, s + i)

        return True

    def remove_customer(self, c: int, s: int) -> bool:
        target_hash = HashHelper.get_guest_hash(c, s,self.customer_salt)

        # check existance
        if self.customer_tree.search(target_hash) is None:
            print(f"[INVALID] remove_customer failed: Guest {(c, s)} not found.")
            return False

        # delete
        self.customer_tree.remove(target_hash)
        return True

    def search_customer_by_id(self, c: int, s: int):
        target_hash = HashHelper.get_guest_hash(c, s,self.customer_salt)

        target_customer = self.customer_tree.search(target_hash)

        if target_customer is None:
            print(f"[INVALID] search_customer_by_id: Guest {(c, s)} not found in system.")
            return None

        return target_customer

    def search_customer_by_room(self, node_id: int, room_no: int):
        # get all customers
        all_customers = []
        self._get_all_customers(self.customer_tree.root,all_customers)

        # looping O(K)
        for customer in all_customers:
            if customer.node_id == node_id and customer.room_no == room_no:
                return customer

        print(f"[INVALID] search_customer_by_room: Building {node_id}, Room {room_no} is currently empty.")
        return None

    def get_customers(self) -> list:
        # get all customers
        all_customers = [] 
        self._get_all_customers(self.customer_tree.root,all_customers)

        all_customers.sort(key=lambda x: (x.node_id, x.room_no))

        return all_customers
        

    def add_building(self, node_id: int):
        if self.building_tree.search(node_id) is not None:
            print(f"[INVALID] add_building failed: Building {node_id} already exists.")
            return None

        self.building_tree.add(node_id)
        self.ring.add_node(node_id)

        all_customers = []
        self._get_all_customers(self.customer_tree.root,all_customers)

        moves = []
        for customer in all_customers:
            new_node_id = self.ring.get_node_id(customer.hash)
            if new_node_id != customer.node_id:
                moves.append(MovedCustomer(id=customer.id,
                                           room_no=customer.room_no,
                                           old_node_id=customer.node_id,
                                           new_node_id=new_node_id,
                                          ))
                customer.node_id = new_node_id

        return moves
    

    def remove_building(self, node_id: int):
        if self.building_tree.search(node_id) is None:
            print(f"[INVALID] remove_building failed: Building {node_id} not found.")
            return None

        root = self.building_tree.root
        if root.left is None and root.right is None:  # only one building in the tree
            print("[INVALID] remove_building failed: cannot remove the last building.")
            return None

        self.building_tree.remove(node_id)
        self.ring.remove_node(node_id)

        all_customers = []
        self._get_all_customers(self.customer_tree.root,all_customers)

        moves = []
        for customer in all_customers:
            new_node_id = self.ring.get_node_id(customer.hash)
            if new_node_id != customer.node_id:
                moves.append(MovedCustomer(id=customer.id,
                                           room_no=customer.room_no,
                                           old_node_id=customer.node_id,
                                           new_node_id=new_node_id,
                                          ))
                customer.node_id = new_node_id
        return moves

    def get_buildings_with_rooms(self) -> list:
        
        all_customers = []
        self._get_all_customers(self.customer_tree.root,all_customers)

        buildings = []
        for customer in all_customers:
            buildings.append(BuildingWithRoom(
                                            building_id=customer.node_id,
                                            room_no= customer.room_no
                                            ))
        return buildings
    