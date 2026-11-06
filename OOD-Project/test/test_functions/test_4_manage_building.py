import unittest
import sys
import os
import csv
import shutil
from enum import Enum
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from hotel_sys import HotelSystem, BuildingWithRoom, Customer, MovedCustomer

# โฟกัสการตรวจสอบผลลัพท์การจัดการการเพิ่ม/ลดอาคาร
# <test script> python -m unittest test\test_all\test_manage_building.py

class Command(Enum):
    AddBuilding = 1
    RemoveBuilding = -1

# Constant
V = 5
building_number = 3
c = 1
n_max = 20
building_salt = "b1"
customer_salt = "c1"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
RESULT_CSV_DIR = os.path.join(os.path.dirname(__file__), "result_report_csv")
TEST_MANAGE_BUILDING_CSV_DIR = os.path.join(RESULT_CSV_DIR, "test_manage_building_csv")

BEFORE_AFTER_HEADER = ["no.", "hash", "c", "s", "building_id", "room_no_before", "building_id_after", "room_no_after", "is_affected"]
DIFF_HEADER = ["no.", "hash", "c", "s", "building_id_before", "building_id_after", "is_affected"]
EXAMPLE_HEADER = ["no.", "hash", "c", "s", "start_id", "after_add_4", "after_remove_2", "after_remove_3"]
SUMMARY_HEADER = ["no.", "test_detail", "target_building", "n_affected", "n_min_expected", "passed"]

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

class TestManageBuilding(unittest.TestCase):
    
    summary_rows = []

    @classmethod
    def setUpClass(cls):
        cls.summary_rows = []
        if os.path.isdir(TEST_MANAGE_BUILDING_CSV_DIR):
            shutil.rmtree(TEST_MANAGE_BUILDING_CSV_DIR)
        os.makedirs(TEST_MANAGE_BUILDING_CSV_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # 1. เขียนไฟล์ summary_manage_building.csv
        summary_path = os.path.join(TEST_MANAGE_BUILDING_CSV_DIR, "summary_manage_building.csv")
        write_csv(summary_path, SUMMARY_HEADER, cls.summary_rows)

        # 2. Console result printing:
        # 2.1 แสดงผลทุกแถวจาก test_operate_building_example.csv
        example_csv_path = os.path.join(TEST_MANAGE_BUILDING_CSV_DIR, "test_operate_building_example", "test_operate_building_example.csv")
        if os.path.isfile(example_csv_path):
            with open(example_csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                ex_header = next(reader, [])
                ex_rows = list(reader)
            print("\n" + "=" * 80)
            print("All rows of test_operate_building_example.csv")
            print("=" * 80)
            print_table("test_operate_building_example.csv", ex_header, ex_rows, limit=len(ex_rows))

        # 2.2 แสดงผล summary_manage_building.csv บน console
        print("\n" + "=" * 80)
        print("Summary Manage Building Results")
        print("=" * 80)
        print_table("summary_manage_building.csv", SUMMARY_HEADER, cls.summary_rows)
        print(f"\n  Summary CSV saved at: {summary_path}\n")
    
    # ===========================================
    #             helper modules
    # ===========================================
    
    def set_up(self) -> HotelSystem:
        
        hotel = HotelSystem(V, building_salt, customer_salt)
        for i in range(1, building_number + 1):
            hotel.add_building(i)
        hotel.add_group_customer(c, 1, n_max)
        return hotel
    
    def get_customer_data(self, p: HotelSystem | list) -> dict:
        
        customer_list = []
        
        customer_dict = {}
        
        if isinstance(p, HotelSystem):
            p._get_all_customers(p.customer_tree.root, customer_list)
            for customer in customer_list:
                        
                id = customer.id
                room = customer.room_no
                building = customer.node_id
                
                customer_dict[id] = (room, building)
        elif isinstance(p, list):
            customer_list = p
            for customer in customer_list:
                                    
                id = customer.id
                room = customer.room_no
                old_building_id = customer.old_node_id
                new_building_id = customer.new_node_id
                
                customer_dict[id] = (room, old_building_id, new_building_id)
        else:
            raise ValueError('parameter(p) is not hotel system or list[MovedCustomer]')
        
        return customer_dict
    
    def get_building_with_room_data(self, hotel: HotelSystem) -> dict:
            
            bwr_list: list[BuildingWithRoom] = hotel.get_buildings_with_rooms()
            
            rwb_dict = {}
            
            for bwr in bwr_list:
                
                room_no = bwr.room_no
                building_id = bwr.building_id
                
                rwb_dict[room_no] = building_id
            
            return rwb_dict
    
    def print_customer_data(self, customer_dict: dict, title = ""):
        
        if title:
            title = title.capitalize()
        else:
            title = "Print Result"
        msg = "\n" + f" {title} ".center(50, '=') + "\n"
        for c_s, r_b in customer_dict.items():
            msg += f"c,s - {c_s} | r_b(r_bo_bn) - {r_b}\n"
            
        print(msg)
    
    def check_moved_customer_room_building(self, before: dict, after: dict, moved: dict):
        try:
            # Try check moved customers first if moved customer exist.
            if moved:
                for id in moved.keys():
                    customer_data = moved[id]
                    before_rb = before[id]
                    after_rb = after[id]
                    
                    self.assertEqual(before_rb, (customer_data[0], customer_data[1]))
                    self.assertEqual(after_rb, (customer_data[0], customer_data[2]))
                    
                    before.pop(id)
                    after.pop(id)
            
            # If no one moved / finished checking moved customer, try check non-moving customer.
            for id in before.keys():
                before_rb = before[id]
                after_rb = after[id]
                
                self.assertEqual(before_rb, after_rb)
                    
        except ValueError as error:
            raise ValueError(error)

    def manage_building(self, hotel: HotelSystem, node_id: int, command = Command.AddBuilding):
        
        before_c = self.get_customer_data(hotel)
        all_building_before = set()
        for rb in before_c.values():
            all_building_before.add(rb[1])
        
        if command is Command.AddBuilding:
            moved = hotel.add_building(node_id)
        elif command is Command.RemoveBuilding:
            moved = hotel.remove_building(node_id)
        else:
            raise TypeError("Invalid command (Command: Enum)")
        
        after_c = self.get_customer_data(hotel)
        all_building_after = set()
        for rb in after_c.values():
            all_building_after.add(rb[1])
        
        return before_c, after_c, len(all_building_before), len(all_building_after), moved
    
    def _test_manage_building(self, hotel, target_id, command: Command = Command.AddBuilding, test_name: str = None, test_detail: str = None):
        subfolder = os.path.join(TEST_MANAGE_BUILDING_CSV_DIR, test_name) if test_name else None
        if subfolder:
            os.makedirs(subfolder, exist_ok=True)

        # เก็บ snapshot ก่อนดำเนินการ
        cust_list_before = []
        hotel._get_all_customers(hotel.customer_tree.root, cust_list_before)
        before_state = {c.id: (c.hash, c.node_id, c.room_no) for c in cust_list_before}

        before_c, after_c,\
            before_b_count, after_b_count, \
            moved = self.manage_building(hotel, target_id, command)
        
        # เก็บ snapshot หลังดำเนินการ
        cust_list_after = []
        hotel._get_all_customers(hotel.customer_tree.root, cust_list_after)
        after_state = {c.id: (c.hash, c.node_id, c.room_no) for c in cust_list_after}

        if moved is None:
            b_delta = 0
        else:
            b_delta = command.value
        
        self.assertEqual(len(before_c), len(after_c))
        self.assertEqual(before_b_count + b_delta, after_b_count)
        
        # ตรวจสอบ moved customers
        moved_dict = self.get_customer_data(moved) if moved is not None else {}
        self.check_moved_customer_room_building(before=before_c, after=after_c, moved=moved_dict)

        # สร้าง CSV รายละเอียดสำหรับ test 1 - 4
        if subfolder and test_detail is not None:
            before_rows = []
            after_rows = []
            diff_rows = []

            n_affected = 0
            # เรียงตาม customer id (c, s)
            sorted_keys = sorted(before_state.keys())
            for idx, cid in enumerate(sorted_keys, start=1):
                c_hash, b_before, r_before = before_state[cid]
                _, b_after, r_after = after_state[cid]
                is_affected = (b_before != b_after or r_before != r_after)
                if is_affected:
                    n_affected += 1

                # before.csv
                before_rows.append([idx, c_hash, cid[0], cid[1], b_before, r_before, b_after, r_after, is_affected])
                # after.csv
                after_rows.append([idx, c_hash, cid[0], cid[1], b_after, r_before, b_after, r_after, is_affected])
                # diffrence.csv: "no.,hash,c,s,building_id_before,building_id_after,is_affected"
                diff_rows.append([idx, c_hash, cid[0], cid[1], b_before, b_after, is_affected])

            write_csv(os.path.join(subfolder, "before.csv"), BEFORE_AFTER_HEADER, before_rows)
            write_csv(os.path.join(subfolder, "after.csv"), BEFORE_AFTER_HEADER, after_rows)
            write_csv(os.path.join(subfolder, "diffrence.csv"), DIFF_HEADER, diff_rows)

            n_min_expected = len(moved) if moved is not None else 0
            passed = (n_affected == n_min_expected)

            case_no = len(TestManageBuilding.summary_rows) + 1
            TestManageBuilding.summary_rows.append([
                case_no, test_detail, target_id, n_affected, n_min_expected, passed
            ])

    # ===========================================
    #             test methods
    # ===========================================
    
    # test 1: Try add non-existing building. Check for matching all moved customer
    def test_add_building(self):
        hotel = self.set_up()
        self._test_manage_building(
            hotel, 4, command=Command.AddBuilding,
            test_name="test_add_building",
            test_detail="add non-existing building"
        )
        
    # test 2: Try add existing building. Program should reject and has no customer changed.
    def test_add_existing_building(self):
        hotel = self.set_up()
        self._test_manage_building(
            hotel, 1, command=Command.AddBuilding,
            test_name="test_add_existing_building",
            test_detail="add existing building"
        )
        
    # test 3: Try remove existing building. Check for matching all moved customer
    def test_remove_building(self):
        hotel = self.set_up()
        self._test_manage_building(
            hotel, 1, command=Command.RemoveBuilding,
            test_name="test_remove_building",
            test_detail="remove existing building"
        )
        
    # test 4: Try remove non-existing building. Program should reject and has no customer changed.
    def test_remove_non_existing_building(self):
        hotel = self.set_up()
        self._test_manage_building(
            hotel, 4, command=Command.RemoveBuilding,
            test_name="test_remove_non_existing_building",
            test_detail="remove non-existing building"
        )
    
    # test 5: Try add and remove existing building to express multi-operations in row
    def test_operate_building_example(self):
        hotel = self.set_up()
        subfolder = os.path.join(TEST_MANAGE_BUILDING_CSV_DIR, "test_operate_building_example")
        os.makedirs(subfolder, exist_ok=True)

        # 0. สถานะตั้งต้น (start)
        cust_list = []
        hotel._get_all_customers(hotel.customer_tree.root, cust_list)
        start_state = {c.id: (c.hash, c.node_id) for c in cust_list}

        # 1. after_add_4
        self._test_manage_building(hotel, 4, command=Command.AddBuilding)
        cust_list_4 = []
        hotel._get_all_customers(hotel.customer_tree.root, cust_list_4)
        state_add_4 = {c.id: c.node_id for c in cust_list_4}

        # 2. after_remove_2
        self._test_manage_building(hotel, 2, command=Command.RemoveBuilding)
        cust_list_2 = []
        hotel._get_all_customers(hotel.customer_tree.root, cust_list_2)
        state_rem_2 = {c.id: c.node_id for c in cust_list_2}

        # 3. after_remove_3
        self._test_manage_building(hotel, 3, command=Command.RemoveBuilding)
        cust_list_3 = []
        hotel._get_all_customers(hotel.customer_tree.root, cust_list_3)
        state_rem_3 = {c.id: c.node_id for c in cust_list_3}

        # สร้างไฟล์ test_operate_building_example.csv
        # "no.,hash,c,s,start_id, after_add_4, after_remove_2, after_remove_3"
        ex_rows = []
        sorted_keys = sorted(start_state.keys())
        for idx, cid in enumerate(sorted_keys, start=1):
            c_hash, start_id = start_state[cid]
            after_4 = state_add_4[cid]
            after_2 = state_rem_2[cid]
            after_3 = state_rem_3[cid]
            ex_rows.append([idx, c_hash, cid[0], cid[1], start_id, after_4, after_2, after_3])

        example_csv_path = os.path.join(subfolder, "test_operate_building_example.csv")
        write_csv(example_csv_path, EXAMPLE_HEADER, ex_rows)
        
    
if __name__ == "__main__":
    unittest.main()


"""
---- FOR CSV CREATION ----
    description:
        create subfolder of each test method result in "test/test_functions/result_report_csv/test_manage_building_csv/"
        each subfolder must contains
        1. before operation as before.csv
        2. after operation as after.csv
        3. before+after operation as diffrence.csv

    for before.csv and after.csv header:
        "no.,hash,c,s,building_id,room_no_before,building_id_after,room_no_after,is_affected"
        **  c,s is from customer_id = (c,s)
            building_id_before,room_no_before is before add/delete building operation of that customer
            building_id_after,room_no_after is after add/delete building operation of that customer
            is_affected is = true when customer changed their building_id or room_no, if not = false (boolean)
    for after.csv header:

    for diffrence.csv header:
        "no.,hash,c,s,building_id_before,building_id_after,is_affected"
        **  c,s is from customer_id = (c,s)
            building_id_before,room_no_before is before add/delete building operation of that customer
            building_id_after,room_no_after is after add/delete building operation of that customer
            is_affected is = true when customer changed their building_id or room_no, if not = false (boolean)

    special only for "test_operate_building_example.csv" instead of normal csv format requirement. create only this new ones
    named ".csv" and it's header is:
        "no.,hash,c,s,start_id, after_add_4, after_remove_2, after_remove_3"
        **  c,s is from customer_id = (c,s)
            start_id is start customer's node_id before any operation
            after_add_4 is current customer's node_id when operation add bulding 4
            after_remove_2 is current customer's node_id when operation remove bulding 2
            after_remove_3 is current customer's node_id when operation remove bulding 3


---- after all test_method ----
    description:
        create csv file name "summary_manage_building.csv" at "test/test_functions/result_report_csv/test_manage_building/" to summarize number of customer changed in each operation
    summary test header:
        "no.,test_detail,target_building, n_affected, n_min_expected passed"
        **  target_building is target building in operation (can be successful or unsuccessful)
            n_affected is number of customer that was changed thier building_id
            n_min_expected is number of customer that expected to move when
                1. new building (virtual_node in ring) was added before their old next building (virtual_node in ring)
                2. thier old building was removed and have to move to next building instead
            passed is boolean statement if only customer that should be affected
        ** test_operate_building_example.csv will be exclude from this summary

---- console result printing ----
    description: print all row of customer from test_operate_building_example.csv to see example of add and remove buliding
        then, print result belong to summary_add_customer.csv file on console
"""