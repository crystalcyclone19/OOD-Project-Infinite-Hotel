class AVLTree:
    class AVLNode:
        def __init__(self, hash_value: int, left=None, right=None):
            self.data = {"hash_value": hash_value} # add more data as you want
            self.__left = left
            self.__right = right
            self.__height = 0
            self.setHeight()
        
        @property # get/set hash value by "node.hash_value" instead of "node.data['hash_value']"
        def hash_value(self):
            return self.data["hash_value"]
        @hash_value.setter
        def hash_value(self, hash_value):
            self.data["hash_value"] = hash_value
        
        @property
        def height(self):
            return self.__height
        
        @property
        def left(self):
            return self.__left
        @left.setter
        def left(self, node):
            if isinstance(node, (AVLTree.AVLNode, type(None))): self.__left = node
            else: raise ValueError("Parameter must be AVLTree.AVLNode type.")
            
        @property
        def right(self):
            return self.__right
        @right.setter
        def right(self, node):
            if isinstance(node, (AVLTree.AVLNode, type(None))): self.__right = node
            else: raise ValueError("Parameter must be AVLTree.AVLNode type.")
            
        def setHeight(self):
            self.__height = 1 + max(self.getHeight(self.__left), self.getHeight(self.__right))
            return self.__height
        
        def getHeight(self, node):
            return -1 if node is None else node.__height
        
        def balanceValue(self):
            return self.getHeight(self.__left) - self.getHeight(self.__right)
  
    def __init__(self, root = None):
        self.root = root
    
    def search(self, key, root = None):
        if root is None:
            root = self.root
        while root is not None:
            if key == root.hash_value:
                return root
            root = root.left if key < root.hash_value \
                            else root.right
        return None
      
    def add(self, key = None):
        if key is None: raise ValueError()
        self.root = self.__add(key, self.root)
  
    def remove(self, key):
        if key is None: raise ValueError()
        self.root = self.__remove(key, self.root)
    
    def __add(self, key, root):
        if root is None:
            return AVLTree.AVLNode(key)
        
        elif key < root.hash_value:
            root.left = self.__add(key, root.left)
        else:
            root.right = self.__add(key, root.right)
            
        return self.__rebalance(root)
          
    def __remove(self, key, root):
        if root is None:
            return None
        
        if key < root.hash_value:
            root.left = self.__remove(key, root.left)
        elif key > root.hash_value:
            root.right = self.__remove(key, root.right)
        else:
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            s = self.__getMinNode(root.right) #successor
            root.hash_value = s.hash_value
            root.right = self.__remove(s.hash_value, root.right)
        return self.__rebalance(root)

    def __rebalance(self, x):
        if x is None:
            return x
        
        x.setHeight()
        bf = x.balanceValue()
        
        if bf == 2:
            if x.left.balanceValue() < 0:
                x = self.__rotateLR(x)
            else:
                x = self.__rotateLL(x)
        elif bf == -2:
            if x.right.balanceValue() > 0:
                x = self.__rotateRL(x)
            else:
                x = self.__rotateRR(x)
        
        x.setHeight()
        return x
       
    def __getMinNode(self, root):
        if root.left is not None:
            return self.__getMinNode(root.left)
        return root
  
    def __rotateLL(self, x): # LL
        y = x.left
        x.left = y.right
        y.right = x
        x.setHeight()
        y.setHeight()
        return y

    def __rotateRR(self, x): # LL
        y = x.right
        x.right = y.left
        y.left = x
        x.setHeight()
        y.setHeight()
        return y

    def __rotateLR(self, x): # LR
        x.left = self.__rotateRR(x.left)
        return self.__rotateLL(x)
    
    def __rotateRL(self, x): # RL
        x.right = self.__rotateLL(x.right)
        return self.__rotateRR(x)
    
def print_tree(node, level=0, prefix="Root: "):
    """ฟังก์ชันเสริมสำหรับพิมพ์โครงสร้าง AVL Tree ออกมาดูทางหน้าจอ"""
    if node is not None:
        print(" " * (level * 4) + prefix + str(node.hash_value) + f" (H:{node.height})")
        print_tree(node.left, level + 1, "L--- ")
        print_tree(node.right, level + 1, "R--- ")

def tester():
    print("=== AVL Tree Tester ===")
    avl = AVLTree()
    
    # 1. ทดสอบการเพิ่มข้อมูล (Add & Rotations)
    # ลำดับนี้จะทำให้เกิดการหมุนทั้งแบบ RR, LL, RL, LR
    keys_to_insert = [30, 20, 10, 40, 50, 25]
    print("\n[1] Inserting nodes...")
    for key in keys_to_insert:
        print(f"Adding {key}")
        avl.add(key)
        
    print("\nTree Structure after Insertions:")
    print_tree(avl.root)

    # 2. ทดสอบการค้นหา (Search)
    print("\n[2] Searching nodes...")
    search_keys = [25, 10, 100]
    for key in search_keys:
        result = avl.search(key)
        if result:
            print(f"Search {key}: Found!")
        else:
            print(f"Search {key}: Not Found")

    # 3. ทดสอบการลบข้อมูล (Remove)
    print("\n[3] Removing nodes...")
    keys_to_remove = [20, 30] # ทดสอบลบโหนดที่มีลูก 1 ตัว และ 2 ตัว
    for key in keys_to_remove:
        print(f"\nRemoving {key}...")
        avl.remove(key)
        print_tree(avl.root)

if __name__ == "__main__":
    pass
