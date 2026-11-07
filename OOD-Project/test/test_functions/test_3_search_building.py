import unittest
import sys
import os
import bisect
import csv
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from hotel_sys import HotelSystem, BuildingWithRoom, Customer
from HashRing import HashHelper, HashRing, VirtualNode

# โฟกัสการค้นหาอาคารจาก hash ที่ตรงกับอาคาร/อยู่ระหว่างอาคาร/เกินของอาคารสุดท้าย และทดสอลการสร้างอาคารที่ hash ซ้ำกันหลายๆ อัน
# <test script> python -m unittest test\test_all\test_search_building.py

# Constant
V_A = 1
V_B = 3
building_number_A = 10
building_number_B = 5
building_salt = "b1"
customer_salt = "c1"
global_test_hash = 1000

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
RESULT_CSV_DIR = os.path.join(os.path.dirname(__file__), "result_report_csv")
TEST_SEARCH_BUILDING_CSV_DIR = os.path.join(RESULT_CSV_DIR, "test_search_building_csv")

SUMMARY_HEADER = ["no.", "test_detail", "n_search", "n_found", "n_expect", "passed"]

def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def print_table(title, header, rows, limit=25):
    display_rows = rows[:limit]
    col_widths = []
    for col_idx in range(len(header)):
        max_len = len(str(header[col_idx]))
        for r in display_rows:
            if col_idx < len(r):
                max_len = max(max_len, len(str(r[col_idx])))
        col_widths.append(max_len)

    def format_row(row):
        formatted_cells = []
        for i, val in enumerate(row):
            w = col_widths[i]
            val_str = str(val)
            if isinstance(val, (int, float)) or val_str in ("True", "False") or (i == 0 and val_str.isdigit()):
                formatted_cells.append(f"{val_str:>{w}}")
            else:
                formatted_cells.append(f"{val_str:<{w}}")
        return " | ".join(formatted_cells)

    separator = "-+-".join("-" * w for w in col_widths)

    print(f"\n  {title} (ทั้งหมด {len(rows)} แถว)")
    print("    " + format_row(header))
    print("    " + separator)
    for r in display_rows:
        print("    " + format_row(r))
    if len(rows) > limit:
        print(f"    ... (แสดง {limit} จาก {len(rows)} แถว)")

class TestSearchBuilding(unittest.TestCase):
    
    summary_rows = []

    @classmethod
    def setUpClass(cls):
        cls.summary_rows = []
        if os.path.isdir(TEST_SEARCH_BUILDING_CSV_DIR):
            shutil.rmtree(TEST_SEARCH_BUILDING_CSV_DIR)
        os.makedirs(TEST_SEARCH_BUILDING_CSV_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        summary_path = os.path.join(TEST_SEARCH_BUILDING_CSV_DIR, "summary_search_building.csv")
        write_csv(summary_path, SUMMARY_HEADER, cls.summary_rows)
        print("\n" + "=" * 80)
        print("Summary Search Building Results")
        print("=" * 80)
        print_table("summary_search_building.csv", SUMMARY_HEADER, cls.summary_rows)
        print(f"\n  Summary CSV saved at: {summary_path}\n")
    
    # ===========================================
    #             helper modules
    # ===========================================
    
    def set_up_A(self) -> HotelSystem:
        
        hotel = HotelSystem(V_A, building_salt, customer_salt)
        for i in range(1, building_number_A + 1):
            hotel.add_building(i)
        
        return hotel
    
    def set_up_B(self) -> HotelSystem:
        hotel = HotelSystem(V_B, building_salt, customer_salt)
        
        # define base hash and increment rate (step)
        base_hash = global_test_hash
        step_hash = global_test_hash
        
        # create 3 pair (6 test set) sort by minimum hash value
        for i in range(V_B):

            # 1. test set i + 1 (only node_id that not equal)
            hash_diff_node = base_hash + (2 * i) * step_hash
            v_idx = i
            for node_id in range(1, V_B + 1):  # node_id difference (1, 2, 3)
                hotel.ring._direct_add_virtual_node(node_id, hash_diff_node, v_idx)
            
            # 2. test set i + 1 (only v_idx (j) that not equal)
            hash_same_node = base_hash + (2 * i + 1) * step_hash
            node_id = i + 1
            for v_index in range(V_B):  # v_idx difference (0, 1, 2)
                hotel.ring._direct_add_virtual_node(node_id, hash_same_node, v_index)
        
        return hotel

    def print_virtual_node_list(self, hotel: HotelSystem):
        
        if not isinstance(hotel.ring, HashRing):
            raise TypeError("hotel.ring is not 'HashRing'")
        
        root = hotel.ring.data.root
        
        virtual_node_list: list[VirtualNode] = []
        
        self.get_all_virtual_nodes(root, virtual_node_list)
        
        virtual_node_list.sort(key=lambda x: x.hash)
        
        msg = f"\n{" All Virtual Nodes ":=^50}\n"
                
        count = 1
        for v in virtual_node_list:
            msg += f"\nNo. {count} : Virtual = {v.node_id}:{v.v_index}:{building_salt} | hash = {v.hash}"
            count += 1
        
        print(msg)

    def get_all_left_mode_virtual_node_dict(self, hotel: HotelSystem) -> dict:
        
        if not isinstance(hotel.ring, HashRing):
            raise TypeError("hotel.ring is not 'HashRing'")
        
        root = hotel.ring.data.root
        
        all_v_nodes: list[VirtualNode] = []
        
        self.get_all_virtual_nodes(root, all_v_nodes)
        
        all_v_nodes.sort(key=lambda x: x.hash)
        
        # print(all_v_nodes)
        
        left_most_v_nodes = {}
        
        for node in all_v_nodes:
            
            if node.hash not in left_most_v_nodes:
                left_most_v_nodes[node.hash] = node.node_id
        
        return left_most_v_nodes
        
    def get_all_virtual_nodes(self, node, virtual_node_list):
        # in-order traversal
        if node is not None:
            self.get_all_virtual_nodes(node.left, virtual_node_list)
            # extract the customer object
            if node.data is not None:
                virtual_node_list.append(node.data)
            self.get_all_virtual_nodes(node.right, virtual_node_list)
    
    def search_building_by_hash(self, hotel: HotelSystem, hash_val):
        
        node_result = hotel.ring.get_node_id(hash_val)
        
        self.assertIsNotNone(node_result)
        
        return node_result
            
    # ===========================================
    #             test methods
    # ===========================================

    # test 1: search building at building's hash on the ring
    def test_search_at_building_hash(self):
        hotel = self.set_up_A()
        
        # get all virtual node list and sorted by node_id
        virtual_nodes: list[VirtualNode] = []
        self.get_all_virtual_nodes(hotel.ring.data.root, virtual_nodes)
        virtual_nodes.sort(key=lambda x: x.hash)
        
        # save searched_by_hash for found virtual node
        node_searched_hash = {}
        
        # create 
        n_search = building_number_A
        n_found = 0
        n_matched = 0
        
        
        # start loop search for virtualnode
        for i in range(1, building_number_A + 1):
            # create hash
            node_hash = HashHelper.get_node_hash(i, 0, building_salt)
            
            # search for virtual node
            node_id = self.search_building_by_hash(hotel, node_hash)
            
            if node_id is not None:
                n_found += 1
            if node_id == i:
                n_matched += 1
                
            # find index of virtual node that match the node_id
            for idx, v in enumerate(virtual_nodes):
                if v.node_id == node_id:
                    node_searched_hash[idx] = node_hash
                    break
            
            # validate if node from searching match with target virtual node
            self.assertEqual(i, node_id)
            
        passed = (n_search == n_found == n_matched)
        case_no = len(TestSearchBuilding.summary_rows) + 1
        TestSearchBuilding.summary_rows.append([
            case_no, "search building at building's hash on the ring", n_search, n_found, n_matched, passed
        ])
        
        # สร้าง CSV แสดง virtual nodes ทั้งหมด พร้อมบอกว่าโหนดไหนถูกเซิร์จโดย hash อะไร
        # "no.,node_id, j, salt,virtual_node_hash,searched_by_hash"
        csv_header = ["no.", "node_id", "j", "salt", "virtual_node_hash", "searched_by_hash"]
        csv_rows = []
        
        for idx, v in enumerate(virtual_nodes, start=1):
            v_index_pos = idx - 1
            searched_by_hash = node_searched_hash.get(v_index_pos, "")
            csv_rows.append([idx, v.node_id, v.v_index, building_salt, v.hash, searched_by_hash])
            
        csv_path = os.path.join(TEST_SEARCH_BUILDING_CSV_DIR, "test_search_at_building_hash.csv")
        write_csv(csv_path, csv_header, csv_rows)
                            
    # test 2: search building between 2 buildings' hash on the ring (include exceed hash value)
    def test_search_not_at_building_hash(self):
        hotel = self.set_up_A()
        
        # get all virtual node list and sorted by node_id
        virtual_nodes: list[VirtualNode] = []
        self.get_all_virtual_nodes(hotel.ring.data.root, virtual_nodes)
        virtual_nodes.sort(key=lambda x: x.hash)
        
        # create node_hash: node_id dictionary pairs
        node_hash_pairs = {}
        for node in virtual_nodes:
            node_hash_pairs[node.hash] = node.node_id
        
        # extract keys and values as list
        node_hash_list = list(node_hash_pairs.keys())
        node_id_list = list(node_hash_pairs.values())
        
        # prepare hash for searching  and show expected node_id result
        # for each case: (search_hash, target_index_in_virtual_nodes, expected_node_id)
        search_cases = []
        for i in range(len(node_hash_list) - 1):
            h = (node_hash_list[i] + node_hash_list[i + 1]) // 2
            target_index = i + 1
            expected_id = node_id_list[i + 1]
            search_cases.append((h, target_index, expected_id))
            
        # case that hash exceed the most hash virtual node -> rotate back to start of ring (index 0)
        exceed_hash = node_hash_list[-1] + int(2e18)
        search_cases.append((exceed_hash, 0, node_id_list[0]))
        
        # save searched_by_hash map for each found virtual node
        node_searched_hash = {}
        
        n_search = len(search_cases)
        n_found = 0
        n_matched = 0
        
        # start loop chech  for matched expected value
        for h, target_index, expected_id in search_cases:
            
            # search for virtual node by hash between 2 virtual node
            node_id = self.search_building_by_hash(hotel, h)
            
            if node_id is not None:
                n_found += 1
            if node_id == expected_id:
                n_matched += 1
            
            node_searched_hash[target_index] = h
            
            # validate if result from search is expected
            self.assertEqual(expected_id, node_id)
            
        passed = (n_search == n_found == n_matched)
        case_no = len(TestSearchBuilding.summary_rows) + 1
        TestSearchBuilding.summary_rows.append([
            case_no, "search building not at building's hash on the ring", n_search, n_found, n_matched, passed
        ])
        
        # สร้าง CSV แสดง virtual nodes ทุกโหนด พร้อมระบุค่า hash ที่ค้นหาแล้วได้โหนดนั้น
        # "no.,node_id, j, salt,virtual_node_hash,searched_by_hash"
        csv_header = ["no.", "node_id", "j", "salt", "virtual_node_hash", "searched_by_hash"]
        csv_rows = []
        
        for idx, v in enumerate(virtual_nodes, start=1):
            v_index_pos = idx - 1
            searched_by_hash = node_searched_hash.get(v_index_pos, "")
            csv_rows.append([idx, v.node_id, v.v_index, building_salt, v.hash, searched_by_hash])
            
        csv_path = os.path.join(TEST_SEARCH_BUILDING_CSV_DIR, "test_search_not_at_building_hash.csv")
        write_csv(csv_path, csv_header, csv_rows)
    
    # test 3: create same hash building and search by sub-key (node_id, j or c, s)
    def test_search_repeated_building_hash(self):
        hotel = self.set_up_B()
        
        # get all virtual nodes list
        virtual_nodes: list[VirtualNode] = []
        self.get_all_virtual_nodes(hotel.ring.data.root, virtual_nodes)
        v_hash_list = [node.hash for node in virtual_nodes]
        
        # save searched_key map for each node that was found
        node_searched_key = {}
        
        n_search = building_number_B + 1
        n_found = 0
        n_matched = 0
        
        # define hash for testing (start with test_hash=1001, first virtual node's hash < test_hash < second virtual node's hash)
        test_hash = global_test_hash + 1
        # start loop searching and testing
        for i in range(building_number_B + 1):
            index = bisect.bisect_left(v_hash_list, test_hash)
            if index >= len(v_hash_list):
                index = 0
            
            target_node_id = virtual_nodes[index].node_id
            search_node_id = self.search_building_by_hash(hotel, test_hash)
            
            if search_node_id is not None:
                n_found += 1
            if search_node_id == target_node_id:
                n_matched += 1
                
            # save searched_key for every index of virtual node that was found
            node_searched_key[index] = test_hash

            # validate if target node_id is equal to result node_id
            self.assertEqual(target_node_id, search_node_id)
            # increase test_hash (example: 1001 -> 2002)
            test_hash += global_test_hash + 1
            
        passed = (n_search == n_found == n_matched)
        case_no = len(TestSearchBuilding.summary_rows) + 1
        TestSearchBuilding.summary_rows.append([
            case_no, "search repeated building hash", n_search, n_found, n_matched, passed
        ])
        
        # สร้าง CSV สำหรับ virtual nodes ทุกตัว
        # "no.,node_id, j, salt,virtual_node_hash,is_left_most,searched_key"
        csv_header = ["no.", "node_id", "j", "salt", "virtual_node_hash", "is_left_most", "searched_key"]
        csv_rows = []
        
        seen_hashes = set()
        for idx, v in enumerate(virtual_nodes, start=1):
            v_index_pos = idx - 1
            is_left_most = (v.hash not in seen_hashes)
            seen_hashes.add(v.hash)
            
            searched_key = node_searched_key.get(v_index_pos, "")
            csv_rows.append([idx, v.node_id, v.v_index, building_salt, v.hash, is_left_most, searched_key])
            
        csv_path = os.path.join(TEST_SEARCH_BUILDING_CSV_DIR, "test_search_repeated_building_hash.csv")
        write_csv(csv_path, csv_header, csv_rows)
        
if __name__ == "__main__":
    unittest.main()


