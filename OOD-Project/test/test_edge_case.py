import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 1. แก้ไขปัญหา Path เพื่อให้รันได้จากทุกตำแหน่ง Directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. นำเข้าคลาสจากไฟล์ hotel_sys.py (ชื่อไฟล์ตามในโปรเจกต์)
from hotel_sys import Customer, HotelSystem

class TestHotelSystem(unittest.TestCase):

    def setUp(self):
        """เตรียม Mock objects และ instance สำหรับใช้ในการทดสอบแต่ละกรณี"""
        self.mock_hash_ring = MagicMock()
        
        # จำลองค่า hash default ให้กับ guest
        self.mock_hash_ring.get_node_id.return_value = 101

        # Patch HashHelper ใน hotel_sys เพื่อไม่ต้องพึ่งพาการคำนวณจริงขณะทดสอบ
        self.patcher = patch('hotel_sys.HashHelper')
        self.mock_hash_helper = self.patcher.start()
        
        # กำหนดฟังก์ชันคำนวณ Hash จำลอง (ใช้ c * 1000 + s เพื่อให้ได้ค่าไม่ซ้ำกันตาม c, s)
        self.mock_hash_helper.get_guest_hash.side_effect = lambda c, s: c * 1000 + s

        self.hotel = HotelSystem(self.mock_hash_ring)

    def tearDown(self):
        self.patcher.stop()

    # ==========================================
    # 1. Normal Functionality Tests (การทำงานปกติ)
    # ==========================================

    def test_cantor_pairing_room_no(self):
        """ทดสอบการคำนวณหมายเลขห้องด้วย Cantor Pairing Function"""
        customer = Customer(1, 1)
        self.assertEqual(customer.room_no, 1)
        
        customer2 = Customer(2, 3)
        # a = 1, b = 2 => ((1+2)*(1+2+1))//2 + 2 + 1 = (3*4)//2 + 3 = 6 + 3 = 9
        self.assertEqual(customer2.room_no, 9)

    def test_add_and_search_customer_success(self):
        """ทดสอบการเพิ่มและค้นหาแขกสำเร็จ"""
        result = self.hotel.add_customer(1, 1)
        self.assertTrue(result)

        cust = self.hotel.search_customer_by_id(1, 1)
        self.assertIsNotNone(cust)
        self.assertEqual(cust.id, (1, 1))

    def test_remove_customer_success(self):
        """ทดสอบการลบแขกออกจากระบบสำเร็จ"""
        self.hotel.add_customer(1, 1)
        remove_result = self.hotel.remove_customer(1, 1)
        self.assertTrue(remove_result)
        
        # ตรวจสอบว่าค้นหาไม่พบแล้ว
        self.assertIsNone(self.hotel.search_customer_by_id(1, 1))

    def test_add_group_customer_success(self):
        """ทดสอบการเพิ่มแขกเป็นกลุ่มสำเร็จ"""
        result = self.hotel.add_group_customer(1, 1, 3) # เพิ่ม (1,1), (1,2), (1,3)
        self.assertTrue(result)
        self.assertIsNotNone(self.hotel.search_customer_by_id(1, 1))
        self.assertIsNotNone(self.hotel.search_customer_by_id(1, 2))
        self.assertIsNotNone(self.hotel.search_customer_by_id(1, 3))

    # ==========================================
    # 2. Edge Case Tests (กรณีขอบตามเอกสารข้อ 4.5)
    # ==========================================

    def test_edge_case_1_add_existing_building(self):
        """[กรณีขอบ 1] เพิ่มรหัสอาคารที่มีอยู่แล้ว ต้องปฏิเสธและคืนค่า None"""
        self.hotel.add_building(101)
        # เพิ่มอาคารเดิมซ้ำ
        result = self.hotel.add_building(101)
        self.assertIsNone(result)

    def test_edge_case_2_remove_non_existing_building(self):
        """[กรณีขอบ 2] ลบรหัสอาคารที่ไม่มีอยู่ ต้องปฏิเสธและคืนค่า None"""
        self.hotel.add_building(101)
        self.hotel.add_building(102)
        # ลบอาคารที่ไม่ได้อยู่ในระบบ
        result = self.hotel.remove_building(999)
        self.assertIsNone(result)

    def test_edge_case_3_remove_last_building(self):
        """[กรณีขอบ 3] ลบอาคารสุดท้ายในระบบ ต้องปฏิเสธการลบเพื่อรักษา N >= 1"""
        self.hotel.add_building(101)
        # พยายามลบอาคารเดียวที่เหลืออยู่
        result = self.hotel.remove_building(101)
        self.assertIsNone(result)

    def test_edge_case_4_add_duplicate_customer(self):
        """[กรณีขอบ 4] เพิ่มรหัสแขกที่ซ้ำกัน ต้องคืนค่า False และไม่เขียนทับ"""
        self.hotel.add_customer(1, 1)
        # เพิ่มแขกรหัสเดิมซ้ำ
        result = self.hotel.add_customer(1, 1)
        self.assertFalse(result)

    def test_edge_case_5_remove_non_existing_customer(self):
        """[กรณีขอบ 5] นำแขกที่ไม่มีอยู่ออก ต้องคืนค่า False และไม่ยกเว้น KeyError"""
        result = self.hotel.remove_customer(99, 99)
        self.assertFalse(result)

    def test_edge_case_6_search_not_found(self):
        """[กรณีขอบ 6] ค้นหาแล้วไม่พบ ทั้งทาง ID และทาง Room ต้องคืนค่า None โดยไม่พัง"""
        # ค้นหาตาม ID
        cust_by_id = self.hotel.search_customer_by_id(99, 99)
        self.assertIsNone(cust_by_id)

        # ค้นหาตาม Building / Room
        cust_by_room = self.hotel.search_customer_by_room(node_id=101, room_no=50)
        self.assertIsNone(cust_by_room)

    def test_edge_case_7_empty_system_k_zero(self):
        """[กรณีขอบ 7] เมื่อยังไม่มีแขกในระบบ (K = 0) ฟังก์ชันดึง/จัดการแขกต้องทำงานได้ไม่ค้าง/พัง"""
        # ดึงรายชื่อแขกขณะ K = 0
        customers = self.hotel.get_customers()
        self.assertEqual(customers, {})

        # เพิ่มอาคารใหม่ขณะ K = 0
        self.hotel.add_building(101)
        self.hotel.add_building(102)
        
        # ย้ายอาคารขณะ K = 0 ต้องคืนลิสต์ว่าง ไม่เกิด ZeroDivisionError
        moves = self.hotel.remove_building(102)
        self.assertEqual(moves, [])

    def test_edge_case_group_add_partial_conflict_rejection(self):
        """[กรณีขอบเพิ่มเติม] ปฏิเสธการเพิ่มแขกแบบกลุ่มทั้งหมด หากมีซ้ำแม้เพียงรายการเดียว"""
        # เพิ่มแขก (1, 2) ล่วงหน้าไว้ก่อน
        self.hotel.add_customer(1, 2)

        # พยายามเพิ่มกลุ่ม (1, 1), (1, 2), (1, 3) -> มี (1, 2) ซ้ำ
        result = self.hotel.add_group_customer(1, 1, 3)
        self.assertFalse(result)

        # ตรวจสอบว่า (1, 1) และ (1, 3) ต้องไม่ถูกเพิ่มเข้าไปด้วย (Atomic rollback/rejection)
        self.assertIsNone(self.hotel.search_customer_by_id(1, 1))
        self.assertIsNone(self.hotel.search_customer_by_id(1, 3))


if __name__ == '__main__':
    unittest.main()