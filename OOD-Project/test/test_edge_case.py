"""
ทดสอบกรณีขอบ (Edge Cases) ตามหัวข้อ 4.5 ของโครงงาน Distributed Hilbert's Hotel
------------------------------------------------------------------------------
- อ่านข้อมูลตั้งต้นจาก customers.csv และ buildings_with_rooms.csv
- ทุกกรณีขอบจะเริ่มจากระบบใหม่ที่โหลดข้อมูลจาก CSV ชุดเดิมเสมอ
- กรณีเกี่ยวกับอาคาร -> output เฉพาะ *_buildings.csv, กรณีเกี่ยวกับแขก -> output เฉพาะ *_customers.csv
- ก่อนเรียกฟังก์ชัน  -> บันทึกสถานะ  before_*.csv
- หลังเรียกฟังก์ชัน  -> บันทึกสถานะ  after_*.csv
- ผลลัพธ์อยู่ในโฟลเดอร์ edge_case_output/<ชื่อกรณี>/
- รัน:  python test_script_project.py
"""
import csv
import os
import shutil
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from hotel_sys import HotelSystem

CUSTOMERS_CSV = os.path.join(BASE_DIR, "customers.csv")
BUILDINGS_CSV = os.path.join(BASE_DIR, "buildings_with_rooms.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "edge_case_output")

# พารามิเตอร์ระบบ (คงที่ทุกกรณี เพื่อให้ผลทำซ้ำได้)
V = 32
BUILDING_SALT = "0"
CUSTOMER_SALT = "0"


# ======================================================================
# ฟังก์ชันช่วย: อ่าน/เขียน CSV และแสดงตาราง
# ======================================================================
def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def print_table(title, header, rows, limit=25):
    print(f"  {title}  (ทั้งหมด {len(rows)} แถว)")
    print("    " + " | ".join(f"{h:>10}" for h in header))
    for r in rows[:limit]:
        print("    " + " | ".join(f"{str(x):>10}" for x in r))
    if len(rows) > limit:
        print(f"    ... (แสดง {limit} จาก {len(rows)} แถว ดูครบในไฟล์ CSV)")


CUSTOMER_HEADER = ["no", "channel", "sequence", "node_id", "room_no"]
BUILDING_HEADER = ["no", "node_id", "room_no"]


# ======================================================================
# สถานะของระบบ (snapshot)
# ======================================================================
def building_ids(hotel):
    """ดึงรหัสอาคารทั้งหมดจาก building_tree (in-order)"""
    ids = []

    def walk(node):
        if node is None:
            return
        walk(node.left)
        ids.append(node.data if hasattr(node, "data") else node.key)
        walk(node.right)

    walk(hotel.building_tree.root)
    return ids


def snapshot(hotel):
    """คืน dict {'customers': [...], 'buildings': [...]} ในรูปแบบเดียวกับไฟล์ CSV ต้นฉบับ"""
    customers = []
    for i, c in enumerate(hotel.get_customers(), start=1):
        customers.append([i, c.id[0], c.id[1], c.node_id, c.room_no])

    rooms_by_building = {}
    for b in hotel.get_buildings_with_rooms():
        rooms_by_building.setdefault(b.building_id, []).append(b.room_no)

    buildings = []
    n = 1
    for bid in sorted(building_ids(hotel)):
        rooms = sorted(rooms_by_building.get(bid, []))
        if not rooms:                       # อาคารที่ยังไม่มีแขก: room_no เว้นว่าง
            buildings.append([n, bid, ""])
            n += 1
        for r in rooms:
            buildings.append([n, bid, r])
            n += 1
    return {"customers": customers, "buildings": buildings}


# ======================================================================
# สร้างระบบจากข้อมูล CSV
# ======================================================================
def building_ids_from_csv():
    """รหัสอาคารทั้งหมดที่ปรากฏใน customers.csv และ buildings_with_rooms.csv"""
    ids = set()
    for r in read_csv(CUSTOMERS_CSV):
        ids.add(int(r["node_id"]))
    for r in read_csv(BUILDINGS_CSV):
        ids.add(int(r["node_id"]))
    return sorted(ids)


def make_hotel(buildings, with_customers=True):
    hotel = HotelSystem(V, BUILDING_SALT, CUSTOMER_SALT)
    for bid in buildings:
        hotel.add_building(bid)
    if with_customers:
        for r in read_csv(CUSTOMERS_CSV):
            hotel.add_customer(int(r["channel"]), int(r["sequence"]))
    return hotel


# ======================================================================
# Test cases
# ======================================================================
class TestEdgeCases(unittest.TestCase):

    summary_rows = []

    @classmethod
    def setUpClass(cls):
        cls.summary_rows = []
        if os.path.isdir(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)
        cls.all_buildings = building_ids_from_csv()

        print("\n" + "=" * 78)
        print("ข้อมูลนำเข้าจากไฟล์ CSV (ก่อนเข้าฟังก์ชัน)")
        print("=" * 78)
        cust = read_csv(CUSTOMERS_CSV)
        bld = read_csv(BUILDINGS_CSV)
        print_table("customers.csv", CUSTOMER_HEADER,
                    [[r[h] for h in CUSTOMER_HEADER] for r in cust])
        print_table("buildings_with_rooms.csv", BUILDING_HEADER,
                    [[r[h] for h in BUILDING_HEADER] for r in bld])
        print(f"  รหัสอาคารที่ใช้สร้างระบบ (รวมจากทั้งสองไฟล์): {cls.all_buildings}")
        print(f"  V={V}, building_salt={BUILDING_SALT!r}, customer_salt={CUSTOMER_SALT!r}")

    @classmethod
    def tearDownClass(cls):
        """สร้างไฟล์สรุป summary.csv: คำสั่ง | จำนวนก่อน | จำนวนหลัง"""
        rows = [[cmd, b, a] for _, cmd, b, a in sorted(cls.summary_rows)]
        header = ["command", "before_count", "after_count"]
        path = os.path.join(OUTPUT_DIR, "summary.csv")
        write_csv(path, header, rows)
        print("\n" + "=" * 78)
        print("สรุปจำนวนก่อน/หลังของทุกกรณีขอบ  (building = นับจำนวนอาคาร, customer = นับจำนวนแขก)")
        print("=" * 78)
        print_table("summary.csv", header, rows)
        print(f"  ไฟล์สรุปอยู่ที่: {path}")

    # ------------------------------------------------------------------
    def run_case(self, key, title, hotel, action, scope, command):
        """บันทึก before -> เรียก action(hotel) -> บันทึก after -> แสดงผลบนจอ

        scope = "building" -> output เฉพาะข้อมูลอาคาร (before/after_buildings.csv)
        scope = "customer" -> output เฉพาะข้อมูลแขก   (before/after_customers.csv)
        """
        assert scope in ("building", "customer")
        name, header = {
            "building": ("buildings", BUILDING_HEADER),
            "customer": ("customers", CUSTOMER_HEADER),
        }[scope]

        folder = os.path.join(OUTPUT_DIR, key)
        os.makedirs(folder, exist_ok=True)

        print("\n" + "=" * 78)
        print(f"[{key}] ({scope}) {title}")
        print("=" * 78)

        before = snapshot(hotel)
        write_csv(os.path.join(folder, f"before_{name}.csv"), header, before[name])
        print_table(f"BEFORE {name}", header, before[name])

        print("  --- เรียกฟังก์ชัน ---")
        result = action(hotel)
        print(f"  ผลที่ฟังก์ชันคืนค่า: {result!r}")

        after = snapshot(hotel)
        write_csv(os.path.join(folder, f"after_{name}.csv"), header, after[name])
        print_table(f"AFTER {name}", header, after[name])
        print(f"  ไฟล์ CSV อยู่ที่: {folder}")

        # เก็บยอดสำหรับไฟล์สรุป: building -> นับจำนวนอาคาร, customer -> นับจำนวนแขก
        if scope == "building":
            n_before = len({r[1] for r in before["buildings"]})
            n_after = len({r[1] for r in after["buildings"]})
        else:
            n_before = len(before["customers"])
            n_after = len(after["customers"])
        self.summary_rows.append((key, command, n_before, n_after))
        return before, after, result

    # ==================================================================
    # กรณีขอบ 1: เพิ่มรหัสอาคารที่มีอยู่แล้ว
    # ==================================================================
    def test_edge_case_1_add_existing_building(self):
        hotel = make_hotel(self.all_buildings)
        existing = self.all_buildings[0]
        before, after, result = self.run_case(
            "edge1_add_existing_building",
            f"เพิ่มอาคาร {existing} ซ้ำ (มีอยู่แล้ว) -> ต้องปฏิเสธ คืน None",
            hotel, lambda h: h.add_building(existing),
            scope="building",
            command=f"add_building({existing})")
        self.assertIsNone(result)
        self.assertEqual(before, after)          # ข้อมูลเดิมต้องไม่เปลี่ยน

    # ==================================================================
    # กรณีขอบ 2: ลบรหัสอาคารที่ไม่มีอยู่
    # ==================================================================
    def test_edge_case_2_remove_non_existing_building(self):
        hotel = make_hotel(self.all_buildings)
        before, after, result = self.run_case(
            "edge2_remove_non_existing_building",
            "ลบอาคาร 999 (ไม่มีอยู่) -> ต้องปฏิเสธ คืน None ไม่มีรายการย้าย",
            hotel, lambda h: h.remove_building(999),
            scope="building",
            command="remove_building(999)")
        self.assertIsNone(result)
        self.assertEqual(before, after)

    # ==================================================================
    # กรณีขอบ 3: ลบอาคารสุดท้าย
    # ==================================================================
    def test_edge_case_3_remove_last_building(self):
        last = self.all_buildings[0]
        hotel = make_hotel([last])               # ระบบมีอาคารเดียว
        before, after, result = self.run_case(
            "edge3_remove_last_building",
            f"ลบอาคาร {last} ซึ่งเป็นอาคารสุดท้าย -> ต้องปฏิเสธ (N >= 1)",
            hotel, lambda h: h.remove_building(last),
            scope="building",
            command=f"remove_building({last})")
        self.assertIsNone(result)
        self.assertEqual(before, after)
        self.assertEqual(building_ids(hotel), [last])

    # ==================================================================
    # กรณีขอบ 4: เพิ่มรหัสแขกที่ซ้ำ
    # ==================================================================
    def test_edge_case_4_add_duplicate_customer(self):
        hotel = make_hotel(self.all_buildings)
        first = read_csv(CUSTOMERS_CSV)[0]
        c, s = int(first["channel"]), int(first["sequence"])
        before, after, result = self.run_case(
            "edge4_add_duplicate_customer",
            f"เพิ่มแขก {(c, s)} ซ้ำ -> ต้องคืน False ไม่เขียนทับ",
            hotel, lambda h: h.add_customer(c, s),
            scope="customer",
            command=f"add_customer({c}, {s})")
        self.assertFalse(result)
        self.assertEqual(before, after)

    # ==================================================================
    # กรณีขอบ 5: นำแขกที่ไม่มีอยู่ออก
    # ==================================================================
    def test_edge_case_5_remove_non_existing_customer(self):
        hotel = make_hotel(self.all_buildings)
        before, after, result = self.run_case(
            "edge5_remove_non_existing_customer",
            "นำแขก (99, 99) ที่ไม่มีอยู่ออก -> ต้องคืน False ไม่เกิด KeyError",
            hotel, lambda h: h.remove_customer(99, 99),
            scope="customer",
            command="remove_customer(99, 99)")
        self.assertFalse(result)
        self.assertEqual(before, after)

    # ==================================================================
    # กรณีขอบ 6: ค้นหาแล้วไม่พบ (ทั้งทาง ID และทาง Room)
    # ==================================================================
    def test_edge_case_6_search_not_found(self):
        hotel = make_hotel(self.all_buildings)

        def action(h):
            return (h.search_customer_by_id(99, 99),
                    h.search_customer_by_room(node_id=999, room_no=123456))

        before, after, result = self.run_case(
            "edge6_search_not_found",
            "ค้นหา (99,99) และ (อาคาร 999, ห้อง 123456) ที่ไม่มี -> คืน None ทั้งคู่",
            hotel, action,
            scope="customer",
            command="search_customer_by_id(99, 99) + search_customer_by_room(999, 123456)")
        self.assertEqual(result, (None, None))
        self.assertEqual(before, after)

    # ==================================================================
    # กรณีขอบ 7: ยังไม่มีแขกในระบบ (K = 0)
    # ==================================================================
    def test_edge_case_7_empty_system_k_zero(self):
        hotel = make_hotel(self.all_buildings[:2], with_customers=False)
        new_id, victim = 777, self.all_buildings[0]

        def action(h):
            customers = h.get_customers()
            rooms = h.get_buildings_with_rooms()
            moves_add = h.add_building(new_id)
            moves_remove = h.remove_building(victim)
            return customers, rooms, moves_add, moves_remove

        before, after, result = self.run_case(
            "edge7_empty_system_k_zero",
            f"K=0: get_customers / add_building({new_id}) / remove_building({victim})"
            " -> ต้องไม่พัง ย้าย 0 คน (ไม่คำนวณอัตราย้ายเพราะไม่มีแขก)",
            hotel, action,
            scope="building",
            command=f"get_customers() + get_buildings_with_rooms() + add_building({new_id}) + remove_building({victim})")
        customers, rooms, moves_add, moves_remove = result
        self.assertEqual(customers, [])
        self.assertEqual(rooms, [])
        self.assertEqual(moves_add, [])
        self.assertEqual(moves_remove, [])
        self.assertEqual(after["customers"], [])
        self.assertEqual(sorted(building_ids(hotel)),
                         sorted([b for b in self.all_buildings[:2] if b != victim] + [new_id]))

    # ==================================================================
    # กรณีขอบเพิ่มเติม (4.1 ข้อ 3): เพิ่มกลุ่มซ้ำบางรายการ -> ปฏิเสธทั้งกลุ่ม
    # ==================================================================
    def test_edge_case_8_group_add_partial_conflict(self):
        hotel = make_hotel(self.all_buildings)
        # customers.csv มี (2,1),(2,2),(2,3) -> กลุ่ม (2,2)..(2,4) ชน 2 รายการ
        before, after, result = self.run_case(
            "edge8_group_add_partial_conflict",
            "เพิ่มกลุ่ม c=2, s_start=2, n=3 (ชน (2,2),(2,3)) -> ปฏิเสธทั้งกลุ่ม",
            hotel, lambda h: h.add_group_customer(2, 2, 3),
            scope="customer",
            command="add_group_customer(2, 2, 3)")
        self.assertFalse(result)
        self.assertEqual(before, after)
        self.assertIsNone(hotel.search_customer_by_id(2, 4))   # รายการที่ไม่ซ้ำก็ต้องไม่ถูกเพิ่ม

    # ==================================================================
    # กรณีขอบเพิ่มเติม (4.1 ข้อ 3): จำนวนกลุ่ม n = 0 และ n < 0
    # ==================================================================
    def test_edge_case_9_group_add_zero_and_negative(self):
        hotel = make_hotel(self.all_buildings)

        def action(h):
            return (h.add_group_customer(5, 1, 0), h.add_group_customer(5, 1, -2))

        before, after, result = self.run_case(
            "edge9_group_add_zero_and_negative",
            "เพิ่มกลุ่ม n=0 (ไม่เปลี่ยนข้อมูล) และ n=-2 (ปฏิเสธ) -> ข้อมูลต้องไม่เปลี่ยน",
            hotel, action,
            scope="customer",
            command="add_group_customer(5, 1, 0) + add_group_customer(5, 1, -2)")
        self.assertEqual(before, after)
        # หมายเหตุ: n=0 ตามโจทย์ถือว่า "ถูกต้องแต่ไม่เปลี่ยนข้อมูล"
        # ส่วน n<0 ต้องถูกปฏิเสธ (False)
        self.assertFalse(result[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
