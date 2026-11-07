import csv
import os
import sys
import pandas as pd

# 1. ตั้งค่า Path ให้ Python มองเห็นโฟลเดอร์ OOD-Project
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from hotel_sys import HotelSystem

# หาตำแหน่งโฟลเดอร์ปัจจุบัน
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data_to_system(
    system,
    buildings_filename="buildings.csv",
    guests_filename="guests.csv",
):
    """ฟังก์ชันอ่านไฟล์ CSV และนำข้อมูลเข้าสู่ระบบ"""
    buildings_filepath = os.path.join(BASE_DIR, buildings_filename)
    guests_filepath = os.path.join(BASE_DIR, guests_filename)

    # 1. อ่านไฟล์อาคาร และเรียกใช้ add_building
    if os.path.exists(buildings_filepath):
        with open(buildings_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_id = int(row["node_id"])
                system.add_building(node_id)
        print(f"เพิ่มอาคารจาก {buildings_filename} เรียบร้อยแล้ว")
    else:
        print(f"ไม่พบไฟล์: {buildings_filepath}")

    # 2. อ่านไฟล์แขก/ลูกค้า และเรียกใช้ฟังก์ชันเพิ่มแขกเข้าสู่ระบบ
    if os.path.exists(guests_filepath):
        with open(guests_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                channel_id = int(row["channel_id"])
                sequence_id = int(row["sequence_id"])

                # เปลี่ยนเป็นชื่อฟังก์ชันเพิ่มแขกจริงในคลาสของคุณ
                # เช่น system.add_customer(channel_id, sequence_id) หรือ system.register_guest(...)
                system.add_customer(
                    c=channel_id, s=sequence_id
                )

        print(f"เพิ่มแขกจาก {guests_filename} เรียบร้อยแล้ว")
    else:
        print(f"ไม่พบไฟล์: {guests_filepath}")

def export_sample_customers(system, filename="customers_sample.csv"):
    CSV_DIR = os.path.join(PROJECT_ROOT, "CSV", "CSV_TestB")
    os.makedirs(CSV_DIR, exist_ok=True)

    all_customers = []
    system._get_all_customers(system.customer_tree.root, all_customers)
    
    data = []
    # สุ่มดึงตัวอย่างแขกสัก 100-1,000 คน หรือทั้งหมดตามต้องการ
    for c in all_customers:  
        data.append({
            "customer_id": c.id,
            "room_no": c.room_no,
            "building_id": c.node_id,
            "hash_value": getattr(c, 'hash', None)
        })
    
    df = pd.DataFrame(data)
    filepath = os.path.join(CSV_DIR, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"[CSV Export] บันทึกข้อมูลแขกตัวอย่างเรียบร้อย: {filepath}")

if __name__ == "__main__":
    system = HotelSystem(number_of_virtual=32, building_salt='testB', customer_salt='testB')
    load_data_to_system(system)