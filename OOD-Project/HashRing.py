import hashlib
from AVLTree import AVLTree

class HashHelper:
    @staticmethod
    def hash_function(key_val: str):
        hash_bytes = hashlib.sha256(key_val.encode('utf-8')).digest()
        hash_val = int.from_bytes(hash_bytes[:8], byteorder='big')
        return hash_val
    
    @staticmethod
    def get_node_hash(node_id: int, j: int):
        text = f"node:{node_id}:{j}"
        return HashHelper.hash_function(text)

    @staticmethod
    def get_guest_hash(c: int, s: int):
        text = f"guest:{c}:{s}"
        return HashHelper.hash_function(text)
    
class HashRing:
    def __init__(self, V: int, data: AVLTree):
        self.v = V
        self.data = data

    def add_node(self, node_id: int):
        for i in range(self.v):
            node_hash = HashHelper.get_node_hash(node_id, i)
            node_val = (node_hash, node_id, i)
            self.data.add(node_val) #function add in class AVLTree
        return self.data

    def remove_node(self, node_id: int):
        for i in range(self.v):
            node_hash = HashHelper.get_node_hash(node_id, i)
            node_val = (node_hash, node_id, i)
            self.data.remove(node_val) #function remove in class AVLTree
        return self.data

    def get_node_id(self, guest_hash: int):
        data = self.find_ceiling((guest_hash,-1,-1))  
        node_id = data[1]
        return node_id
    
    def findmin(self, node: int):
        while node.left is not None:
            node = node.left
        return node

    def find_ceiling(self, data: int):
        result =  self._find_ceiling(self.data.root, data)

        if result is not None:
            return result

        min_node = self.findmin(self.data.root)
        return min_node.data["hash_value"]         # According to AVLtree {"hash_value": hash_value}
    
    def _find_ceiling(self, node: AVLTree, data: int):
        if node is None:
            return None

        if node.data["hash_value"] == data:  # According to AVLtree {"hash_value": hash_value}
            return node.data["hash_value"]   # According to AVLtree {"hash_value": hash_value}

        if data < node.data["hash_value"]:   # According to AVLtree {"hash_value": hash_value}
            left_result = self._find_ceiling(node.left, data)
            return left_result if left_result is not None else node.data["hash_value"]   # According to AVLtree {"hash_value": hash_value}
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