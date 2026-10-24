import hashlib
from AVLTree import AVLClassTree, AVLNode

class HashHelper:
    @staticmethod
    def hash_function(key_val: str):
        hash_bytes = hashlib.sha256(key_val.encode('utf-8')).digest()
        hash_val = int.from_bytes(hash_bytes[:8], byteorder='big')
        return hash_val
    
    @staticmethod
    def get_node_hash(node_id: int, j: int, salt: int):
        text = f"node:{node_id}:{j}:{salt}"
        return HashHelper.hash_function(text)

    @staticmethod
    def get_guest_hash(c: int, s: int, salt: str):
        text = f"guest:{c}:{s}:{salt}"
        return HashHelper.hash_function(text)

class VirtualNode:
    def __init__(self, hash_value: int, node_id: int, v_index: int):
        self.hash = hash_value
        self.node_id = node_id
        self.v_index = v_index
    
class HashRing:
    def __init__(self, V: int, salt: str):
        self.v = V
        self.salt = salt
        self.data = AVLClassTree()

    def add_node(self, node_id: int):
        for i in range(self.v):
            node_hash = HashHelper.get_node_hash(node_id, i, self.salt)
            node_val = VirtualNode(node_hash, node_id, i)
            self.data.add(node_val) #function add in class AVLTree
        return self.data

    def remove_node(self, node_id: int):
        for i in range(self.v):
            node_hash = HashHelper.get_node_hash(node_id, i, self.salt)
            node_val = VirtualNode(node_hash, node_id, i)
            self.data.remove(node_val) #function remove in class AVLTree
        return self.data

    def get_node_id(self, guest_hash: int):
        node = self.find_ceiling(guest_hash)
        if node is None:
            return None
        return node.node_id
    
    def findmin(self, node: int):
        while node.left is not None:
            node = node.left
        return node

    def find_ceiling(self, data: int):
        if self.data.root is None:
            return None
        
        result =  self._find_ceiling(self.data.root, data)

        if result is not None:
            return result

        min_node = self.findmin(self.data.root)
        return min_node.data         
    
    def _find_ceiling(self, node: AVLNode, data: int):
        if node is None:
            return None

        node_data = self.data._get_key(node) #function _get_key in class AVLTree

        if node_data == data:  
            return node.data   
            
        if data < node_data:  
            left_result = self._find_ceiling(node.left, data)
            return left_result if left_result is not None else node.data 
        else:
            return self._find_ceiling(node.right, data)

class HashModN:
    def __init__(self):
        self.building_list = []

    def add_node(self, node_id: int):
        if node_id not in self.building_list:
            self.building_list.append(node_id)

    def remove_node(self, node_id: int):
        if node_id in self.building_list:
            self.building_list.remove(node_id)

    def get_node_id(self, guest_hash: int):
        node_index = guest_hash % len(self.building_list)
        return self.building_list[node_index]


