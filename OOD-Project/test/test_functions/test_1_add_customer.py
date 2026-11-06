import unittest
import sys
import os
import csv
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from hotel_sys import HotelSystem, BuildingWithRoom, Customer

# โฟกัสการเพิ่ม User แล้วหมายเลขห้องไม่เปลี่ยนเลยแม้แต่คนเดียว
# <test script> python -m unittest test\test_all\test_add_customer.py

# Constant
V = 1
initial_channel = 1
building_salt = "b1"
customer_salt = "c1"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
RESULT_CSV_DIR = os.path.join(os.path.dirname(__file__), os.path.join("result_report_csv", "test_add_customer_csv"))
TEST_ADD_CUSTOMER_CSV_DIR = RESULT_CSV_DIR

CUSTOMER_HEADER = ["no.", "hash", "c", "s", "building_id", "room_no"]
SUMMARY_HEADER = ["no.", "test_detail", "n_before", "n_after", "n_changed", "n_expected", "passed"]

def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def print_table(title, header, rows, limit=25):
    display_rows = rows[:limit]
    # คำนวณความกว้างสูงสุดของแต่ละคอลัมน์โดยอิงจาก header และข้อมูลในแถว
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
            # จัดชิดซ้ายสำหรับข้อความ (text/detail) และจัดชิดขวาสำหรับตัวเลขหรือ boolean
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

class TestAddCustomer(unittest.TestCase):
    
    summary_rows = []

    @classmethod
    def setUpClass(cls):
        cls.summary_rows = []
        if os.path.isdir(TEST_ADD_CUSTOMER_CSV_DIR):
            shutil.rmtree(TEST_ADD_CUSTOMER_CSV_DIR)
        os.makedirs(TEST_ADD_CUSTOMER_CSV_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        summary_path = os.path.join(RESULT_CSV_DIR, "summary_add_customer.csv")
        write_csv(summary_path, SUMMARY_HEADER, cls.summary_rows)
        print("\n" + "=" * 80)
        print("Summary Add Customer Results")
        print("=" * 80)
        print_table("summary_add_customer.csv", SUMMARY_HEADER, cls.summary_rows)
        print(f"\n  Summary CSV saved at: {summary_path}\n")

    # ===========================================
    #             helper modules
    # ===========================================
    
    def get_customer_rows(self, hotel: HotelSystem) -> list:
        customer_list = []
        hotel._get_all_customers(hotel.customer_tree.root, customer_list)
        rows = []
        for i, c in enumerate(customer_list, start=1):
            rows.append([i, c.hash, c.id[0], c.id[1], c.node_id, c.room_no])
        return rows

    def run_case_with_report(self, test_name: str, test_detail: str, action, n_expected: int, setup_fn=None):
        hotel = setup_fn() if setup_fn else self.set_up()
        
        # 1. Before operation
        before_dict = self.get_customer_data(hotel)
        before_rows = self.get_customer_rows(hotel)
        subfolder = os.path.join(TEST_ADD_CUSTOMER_CSV_DIR, test_name)
        write_csv(os.path.join(subfolder, "before.csv"), CUSTOMER_HEADER, before_rows)
        
        # 2. Action
        action(hotel)
        
        # 3. After operation
        after_dict = self.get_customer_data(hotel)
        after_rows = self.get_customer_rows(hotel)
        write_csv(os.path.join(subfolder, "after.csv"), CUSTOMER_HEADER, after_rows)
        
        # 4. Metric calculations
        n_before = len(before_dict)
        n_after = len(after_dict)
        n_changed = n_after - n_before
        
        room_changed = 0
        for customer_id, rb_before in before_dict.items():
            if customer_id in after_dict:
                if rb_before != after_dict[customer_id]:
                    room_changed += 1
            else:
                room_changed += 1
                
        passed = (n_changed == n_expected and room_changed == 0)
        
        case_no = len(TestAddCustomer.summary_rows) + 1
        TestAddCustomer.summary_rows.append([
            case_no, test_detail, n_before, n_after, n_changed, n_expected, passed
        ])
        
        self.assertEqual(n_changed, n_expected)
        self.assertEqual(room_changed, 0)
    
    def set_up(self) -> HotelSystem:
        hotel = HotelSystem(V, building_salt, customer_salt)
        hotel.add_building(1)
        hotel.add_group_customer(initial_channel, 1, 20)
        return hotel

    def set_up_repeated_group(self) -> HotelSystem:
        hotel = self.set_up()
        hotel.add_group_customer(initial_channel, 31, 10)
        hotel.add_customer(initial_channel, 50)
        return hotel
    
    def get_customer_data(self, hotel: HotelSystem) -> dict:
        
        customer_list = []
        
        hotel._get_all_customers(hotel.customer_tree.root, customer_list)
        
        customer_dict = {}
        
        for customer in customer_list:
            
            id = customer.id
            room = customer.room_no
            building = customer.node_id
            
            customer_dict[id] = (room, building)
        
        return customer_dict

    def check_customer_changed_room_building(self, before: dict, after: dict):
        try:
            for customer_id in before.keys():
                
                rb_before = before[customer_id]
                rb_after = after[customer_id]
                
                if rb_before != rb_after:
                    raise ValueError(f"Found room_no or building_id changed: {rb_before} -> {rb_after}")
        except ValueError as error:
            raise ValueError(error)

    def _test_add_customer(self, channel:int):
        
        hotel = self.set_up()
        
        # test 1: Try add customer
        
        before = self.get_customer_data(hotel)
        
        self.assertTrue(hotel.add_customer(channel,21))
        self.assertTrue(hotel.add_customer(channel,22))
        self.assertTrue(hotel.add_customer(channel,23))
                        
        after = self.get_customer_data(hotel)
        
        self.assertEqual(len(before) + 3, len(after))

        # test 2: Check for changed old customers room_no or building_id
        
        self.check_customer_changed_room_building(before, after)
        
    def _test_add_repeated_customer(self):
                
        hotel = self.set_up()
        
        # test 1: Try add repeated customers
                
        before = self.get_customer_data(hotel)
        
        self.assertFalse(hotel.add_customer(initial_channel,1))
        self.assertFalse(hotel.add_customer(initial_channel,15))
        self.assertFalse(hotel.add_customer(initial_channel,20))
        
        after = self.get_customer_data(hotel)
        
        self.assertEqual(len(before), len(after))
        
        # test 2: Check for changed old customers room_no or building_id
                
        self.check_customer_changed_room_building(before, after)
         
    def _test_add_group_customer(self, channel:int):
            
        hotel = self.set_up()
        
        # test 1: Try add customers
        
        before = self.get_customer_data(hotel)
        
        self.assertTrue(hotel.add_group_customer(channel, 21, 5))
        self.assertTrue(hotel.add_group_customer(channel, 31, 10))
                        
        after = self.get_customer_data(hotel)
        
        self.assertEqual(len(before) + 15, len(after))

        # test 2: Check for changed old customers room_no or building_id
        
        self.check_customer_changed_room_building(before, after)
        
    def _test_add_repeated_group_customer(self):
        
        hotel = self.set_up()
        
        hotel.add_group_customer(initial_channel, 31, 10)
        hotel.add_customer(initial_channel, 50)
                
        # test 1: Try add repeated customers
        
        before = self.get_customer_data(hotel)
        
        self.assertFalse(hotel.add_group_customer(initial_channel, 27, 5)) # tail overlapping
        self.assertFalse(hotel.add_group_customer(initial_channel, 20, 5)) # head overlapping
        self.assertFalse(hotel.add_group_customer(initial_channel, 46, 5)) # middle overlapping
        
        after = self.get_customer_data(hotel)
        
        self.assertEqual(len(before), len(after))
        
        # test 2: Check for changed old customers room_no or building_id
                
        self.check_customer_changed_room_building(before, after)
   
    # ===========================================
    #             test methods
    # ===========================================

    # test 1: add single customer with same channel
    def test_add_customer_old_channel(self):
        def action(hotel):
            self.assertTrue(hotel.add_customer(1, 21))
            self.assertTrue(hotel.add_customer(1, 22))
            self.assertTrue(hotel.add_customer(1, 23))

        self.run_case_with_report(
            test_name="test_add_customer_old_channel",
            test_detail="add single customer with same channel",
            action=action,
            n_expected=3
        )
    
    # test 2: add single customer with difference channel
    def test_add_customer_new_channel(self):
        def action(hotel):
            self.assertTrue(hotel.add_customer(5, 21))
            self.assertTrue(hotel.add_customer(5, 22))
            self.assertTrue(hotel.add_customer(5, 23))

        self.run_case_with_report(
            test_name="test_add_customer_new_channel",
            test_detail="add single customer with difference channel",
            action=action,
            n_expected=3
        )
    
    # test 3: add multiple customers with same channel
    def test_add_group_customer_old_channel(self):
        def action(hotel):
            self.assertTrue(hotel.add_group_customer(1, 21, 5))
            self.assertTrue(hotel.add_group_customer(1, 31, 10))

        self.run_case_with_report(
            test_name="test_add_group_customer_old_channel",
            test_detail="add multiple customers with same channel",
            action=action,
            n_expected=15
        )
    
    # test 4: add multiple customers with difference channel
    def test_add_group_customer_new_channel(self):
        def action(hotel):
            self.assertTrue(hotel.add_group_customer(5, 21, 5))
            self.assertTrue(hotel.add_group_customer(5, 31, 10))

        self.run_case_with_report(
            test_name="test_add_group_customer_new_channel",
            test_detail="add multiple customers with difference channel",
            action=action,
            n_expected=15
        )
    
    # test 5: add repeated single customer
    def test_add_repeated_customer(self):
        def action(hotel):
            self.assertFalse(hotel.add_customer(initial_channel, 1))
            self.assertFalse(hotel.add_customer(initial_channel, 15))
            self.assertFalse(hotel.add_customer(initial_channel, 20))

        self.run_case_with_report(
            test_name="test_add_repeated_customer",
            test_detail="add repeated single customer",
            action=action,
            n_expected=0
        )
    
    # test 6: add repeated multiple customers
    def test_add_repeated_group_customer(self):
        def action(hotel):
            self.assertFalse(hotel.add_group_customer(initial_channel, 27, 5))  # tail overlapping (ทับ 31)
            self.assertFalse(hotel.add_group_customer(initial_channel, 20, 5))  # head overlapping (ทับ 20)
            self.assertFalse(hotel.add_group_customer(initial_channel, 46, 5))  # middle overlapping (ทับ 50)

        self.run_case_with_report(
            test_name="test_add_repeated_group_customer",
            test_detail="add repeated multiple customers",
            action=action,
            n_expected=0,
            setup_fn=self.set_up_repeated_group
        )
        
if __name__ == "__main__":
    unittest.main()

"""
---- FOR CSV CREATION ----
    description:
        create subfolder of each test method result in "test/test_functions/result_report_csv/test_add_customer_csv/"
        each subfolder must contains
        1. before operation as before.csv
        2. after operation as after.csv
    each test result header:
        "no.,hash,c,s,building_id,room_no"

---- after all test_method ----
    description:
        create csv file name "summary_add_customer.csv" at "test/test_functions/result_report_csv/test_add_customer_csv/" to summarize number of customer changed in each operation
    summary test header:
        "no.,test_detail,n_before,n_after,n_changed,n_expected,passed"
        **  n_before is number of all customer in tree before operation
            n_after is number of all customer in tree after operation
            n_changed is n_after - n_before
            n_expected is expected "n_after - n_before" number
            room_changed is number of customer that changed their room or building
            pass is boolean statement (n_changed == n_expected and room_changed == 0)
---- console result printing ----
    description: print result belong to summary_add_customer.csv file on console

"""