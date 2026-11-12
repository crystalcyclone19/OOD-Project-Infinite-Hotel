import unittest
import sys
import os
import csv
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from hotel_sys import HotelSystem, BuildingWithRoom, Customer

# โฟกัสการตรวจสอบ สมการ Cantor Pairing Function เพื่อพิสูจน์ว่า c/s ของ customer ที่ต่างกันจะไม่ได้เลขที่ซ้ำกันเลย
# <test script> python -m unittest test\test_all\test_room_conflict.py

# Constant
V = 1
c_max = 100
n_max = 1000
building_salt = "b1"
customer_salt = "c1"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
RESULT_CSV_DIR = os.path.join(os.path.dirname(__file__), "result_report_csv")
TEST_ROOM_CONFLICT_CSV_DIR = os.path.join(RESULT_CSV_DIR, "test_room_conflict_csv")

ROOM_CONFLICT_HEADER = ["no.", "c", "s", "room_no", "building_id", "is_missing"]
SUMMARY_HEADER = ["no.", "test_detail", "n_c", "n_s", "n_created", "n_existed", "n_missing", "passed"]

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

class TestRoomConflict(unittest.TestCase):
    
    summary_rows = []

    @classmethod
    def setUpClass(cls):
        cls.summary_rows = []
        if os.path.isdir(TEST_ROOM_CONFLICT_CSV_DIR):
            shutil.rmtree(TEST_ROOM_CONFLICT_CSV_DIR)
        os.makedirs(TEST_ROOM_CONFLICT_CSV_DIR, exist_ok=True)
        os.makedirs(TEST_ROOM_CONFLICT_CSV_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # บันทึก summary_room_no_conflict.csv ตามคำสั่ง
        # บันทึกลงทั้งใน test_room_conflict_csv และ test_search_building_csv ตาม docstring
        summary_path_search = os.path.join(TEST_ROOM_CONFLICT_CSV_DIR, "summary_room_no_conflict.csv")
        summary_path_conflict = os.path.join(TEST_ROOM_CONFLICT_CSV_DIR, "summary_room_no_conflict.csv")
        write_csv(summary_path_search, SUMMARY_HEADER, cls.summary_rows)
        write_csv(summary_path_conflict, SUMMARY_HEADER, cls.summary_rows)

        # Console result printing:
        # 1. แสดง 20 แถวแรกจากไฟล์ test_room_no_conflict.csv
        detail_csv_path = os.path.join(TEST_ROOM_CONFLICT_CSV_DIR, "test_room_no_conflict.csv")
        if os.path.isfile(detail_csv_path):
            with open(detail_csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, [])
                rows = list(reader)
            print("\n" + "=" * 80)
            print("Preview 20 rows of test_room_no_conflict.csv")
            print("=" * 80)
            print_table("test_room_no_conflict.csv", header, rows, limit=20)

        # 2. แสดงผลสรุปของ summary_room_no_conflict.csv
        print("\n" + "=" * 80)
        print("Summary Room No Conflict Results")
        print("=" * 80)
        print_table("summary_room_no_conflict.csv", SUMMARY_HEADER, cls.summary_rows)
        print(f"\n  Summary CSV saved at: {summary_path_search}\n")
    
    # ===========================================
    #             helper modules
    # ===========================================
    
    def set_up(self) -> HotelSystem:
        
        hotel = HotelSystem(V, building_salt, customer_salt)
        hotel.add_building(1)
        return hotel
    
    def check_repeated_rooms(self, hotel: HotelSystem, cn):
        
        building_with_rooms = hotel.get_buildings_with_rooms()
        
        room_no_set = set()
        repeated_rooms = []
        
        for bwr in building_with_rooms:
            
            building_id = bwr.building_id
            room_no = bwr.room_no
            
            if room_no not in room_no_set:
                room_no_set.add(room_no)
            else:
                repeated_rooms.append((building_id, room_no))
                
        if (len(room_no_set) != cn):
            error_msg = self.create_repeated_room_message(repeated_rooms)
            self.assertEqual(len(room_no_set), cn, msg=error_msg)
    
    def create_repeated_room_message(self, repeated_rooms) -> str:
        
        error_msg = ""
        
        error_msg += f"\n{' Repeated Room No. List ':=^50}\n"
        
        count = 1
        for b, r in repeated_rooms:
            error_msg += f"\nNo. {count} : room_no = {r} | building_id = {b}"
            count += 1
            
        return error_msg
    
    def _create_multiple_user(self, hotel: HotelSystem,  c: int, n: int):
        # print(f"Creating customer at channel '{c}', number of customer '{n}'...")
        hotel.add_group_customer(c, 1, n)

    # ===========================================
    #             test methods
    # ===========================================
    
    # test 1: add c_max*n_max customers and search for repeated room_no.
    def test_room_no_conflict(self):
        hotel = self.set_up()
        
        for c in range(1, c_max + 1):
            self._create_multiple_user(hotel, c, n_max)
        
        # get all customer from customer_tree
        all_customers = []
        hotel._get_all_customers(hotel.customer_tree.root, all_customers)
        
        # create index for checking customer (c, s)
        cust_map = {c.id: c for c in all_customers}
        
        # create CSV for test_room_no_conflict.csv
        # Header: "no.,c, s, room_no, building_id, is_missing"
        csv_rows = []
        counter = 1
        
        for c in range(1, c_max + 1):
            for s in range(1, n_max + 1):
                cust = cust_map.get((c, s))
                if cust is not None:
                    # customer is in tree.
                    csv_rows.append([counter, c, s, cust.room_no, cust.node_id, False])
                else:
                    # customer is missing (not found in tree)
                    expected_room = hotel.calculate_room_no(c, s)
                    csv_rows.append([counter, c, s, expected_room, "", True])
                counter += 1
                
        detail_csv_path = os.path.join(TEST_ROOM_CONFLICT_CSV_DIR, "test_room_no_conflict.csv")
        write_csv(detail_csv_path, ROOM_CONFLICT_HEADER, csv_rows)
        
        # summary
        n_created = c_max * n_max
        
        n_existed = len(all_customers)
        n_missing = n_created - n_existed
        passed = (n_created == n_existed)
        
        case_no = len(TestRoomConflict.summary_rows) + 1
        TestRoomConflict.summary_rows.append([
            case_no, "add c_max*n_max customers and check room conflict",
            c_max, n_max, n_created, n_existed, n_missing, passed
        ])
        
        self.check_repeated_rooms(hotel, n_created)
    
if __name__ == "__main__":
    unittest.main()