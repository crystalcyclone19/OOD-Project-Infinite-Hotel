import csv
import os
import random

# หาตำแหน่งโฟลเดอร์ที่ไฟล์สคริปต์นี้วางอยู่ (โฟลเดอร์ test_B)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_mock_data(
    num_buildings: int = 10,
    num_guests: int = 10000,
    num_channels: int = 5,
    buildings_filename: str = "buildings.csv",
    guests_filename: str = "guests.csv",
):
    """ฟังก์ชันสำหรับสร้างไฟล์ CSV ข้อมูลอาคารและแขกแบบจำลอง"""
    # สร้าง Absolute Path เต็ม
    buildings_filepath = os.path.join(BASE_DIR, buildings_filename)
    guests_filepath = os.path.join(BASE_DIR, guests_filename)

    # 1. สร้างไฟล์ CSV สำหรับอาคาร (ใช้ buildings_filepath)
    with open(buildings_filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["node_id"])
        for i in range(1, num_buildings + 1):
            writer.writerow([f"{i}"])

    # # 2. สร้างไฟล์ CSV สำหรับแขก (ใช้ guests_filepath)
    # with open(guests_filepath, mode="w", newline="", encoding="utf-8") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["channel_id", "sequence_id"])

    #     for seq_id in range(1, num_guests + 1):
    #         channel_id = random.randint(1, num_channels)
    #         writer.writerow([channel_id, seq_id])

    print("สร้างไฟล์สำเร็จ!")
    print(f"- {buildings_filepath}: จำนวน {num_buildings} อาคาร")
    # print(f"- {guests_filepath}: จำนวน {num_guests} แขก")


if __name__ == "__main__":
    N = 5  # จำนวนอาคาร (Building count)
    K = 10000  # จำนวนแขก (Guest count)

    generate_mock_data(
        num_buildings=N,
        num_guests=K,
        buildings_filename="buildings.csv",
        guests_filename="guests.csv",
    )