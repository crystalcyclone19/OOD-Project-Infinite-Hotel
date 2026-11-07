# OOD Project: Infinite Hotel

โปรเจกต์การจำลองและการทดสอบประสิทธิภาพระบบการจัดการข้อมูลสำหรับ **Infinite Hotel** (Consistent Hashing vs Hash Mod N)

---

## สารบัญ
- [ข้อกำหนดเบื้องต้นและการติดตั้ง (Prerequisites & Installation)](#-ข้อกำหนดเบื้องต้นและการติดตั้ง)
- [โครงสร้างโฟลเดอร์ (Directory Structure)](#โครงสร้างโฟลเดอร์ที่สำคัญ)
- [การรันโปรแกรมหลัก (Run the Application)](#การรันโปรแกรมหลัก)
- [System & Algorithm Tests](#system--algorithm-tests)
- [Unit Tests & Function Verification](#unit-tests--function-verification)

---

## 🛠 ข้อกำหนดเบื้องต้นและการติดตั้ง

1. **Python:** ภาษา Python เวอร์ชัน 3.8 ขึ้นไป
2. **การติดตั้ง Dependencies:** (รันที่โฟลเดอร์ `OOD-Project-Infinite-Hotel/`)
   ```bash
   pip install -r requirements.txt
   ```

---

## โครงสร้างโฟลเดอร์ที่สำคัญ

```text
OOD-Project-Infinite-Hotel/
├── README.md
├── requirements.txt
└── OOD-Project/                       # โฟลเดอร์หลักของโปรเจกต์ (รันคำสั่งทั้งหมดจากที่นี่)
    ├── app.py                         # โปรแกรมหลัก (Text UI)
    ├── hotel_sys.py                   # คลาสหลักของระบบ: HotelSystem, Customer, BuildingWithRoom, MovedCustomer
    ├── HashRing.py                    # HashHelper, VirtualNode, HashRing (Consistent Hashing), HashModN
    ├── AVLTree.py                     # AVLTree (AVLNormalTree, AVLClassTree) ใช้เก็บข้อมูลเรียงลำดับ
    ├── data/                          # ข้อมูลที่ app.py โหลด/บันทึก
    │   ├── config.json                # ค่า hash_type, V, salt ของอาคารและแขก
    │   ├── buildings.csv              # รหัสอาคาร เรียงตามลำดับที่เพิ่ม
    │   └── guests.csv                 # channel_id, sequence_id, node_id, room_no
    ├── util/                          # ฟังก์ชันช่วยเหลือ
    │   ├── csv_sys.py                 # อ่าน/เขียนไฟล์ CSV
    │   ├── graph.py                   # สร้างกราฟ
    │   ├── timer.py                   # จับเวลา
    │   ├── memory_usage.py            # วัดการใช้หน่วยความจำ
    │   ├── math.py                    # ฟังก์ชันคำนวณ (ค่ามัธยฐาน ความแปรปรวน การ fit โมเดล)
    │   └── color.py                   # สีสำหรับแสดงผลบน Terminal
    ├── graph/                         # รูปกราฟผลลัพธ์
    │   ├── test_A/                    # กราฟ Test A (แยก consistant_hashing/ และ hash_mod_n/)
    │   └── GRAPH_TestB/               # กราฟ Test B
    ├── CSV/                           # ไฟล์ CSV ผลลัพธ์
    │   ├── test_A/                    # CSV Test A (แยก consistant_hashing/ และ hash_mod_n/)
    │   ├── CSV_TestB/                 # CSV Test B
    │   ├── app_output/                # CSV ที่ app.py ส่งออก (เช่น รายการแขกที่ถูกย้าย)
    │   └── test_C_results.csv         # CSV Test C
    └── test/                          # Script สำหรับรันการทดสอบ
        ├── test_A.py                  # Test A
        ├── test_B/
        │   ├── test_B.py              # Test B
        │   ├── generate_mock_data_csv.py   # สร้างข้อมูลจำลอง
        │   ├── load_data_to_system.py      # โหลดข้อมูลเข้าระบบ
        │   ├── buildings.csv          # ข้อมูลอาคารจำลองที่สร้างขึ้น
        │   └── guests.csv             # ข้อมูลแขกจำลองที่สร้างขึ้น
        ├── test_C.py                  # Test C
        ├── test_all_functions.py      # ตัวรัน Unit Test ทั้งหมด + สรุปผลเป็น overall_summary.csv
        └── test_functions/            # ชุด Unit Test สำหรับทดสอบแต่ละฟังก์ชัน
            ├── test_1_add_customer.py
            ├── test_2_room_conflict.py
            ├── test_3_search_building.py
            ├── test_4_manage_building.py
            ├── test_5_edge_case.py
            ├── test_set_csv/          # ข้อมูลตั้งต้น (buildings_with_rooms.csv, customers.csv)
            ├── result_report_csv/     # รายงานผลการทดสอบ (CSV) ของแต่ละชุด + overall_summary.csv
            └── test_list.md           # รายการทดสอบขั้นต่ำตามโจทย์
```

---

## การรันโปรแกรมหลัก

โปรแกรมหลักเป็น Text UI ในไฟล์ `app.py` รันจากโฟลเดอร์ `OOD-Project`

```bash
cd OOD-Project-Infinite-Hotel/OOD-Project
python app.py
```

- ตอนเปิดโปรแกรม จะโหลดข้อมูลจากโฟลเดอร์ `data/` (`config.json`, `buildings.csv`, `guests.csv`)
- ข้อมูลหลักอยู่ในหน่วยความจำ ส่วนไฟล์ใน `data/` เป็นสำเนาที่บันทึกไว้ และจะถูกบันทึกใหม่หลังทุกคำสั่งที่เปลี่ยนข้อมูล
- ไฟล์ CSV ที่ส่งออกจากโปรแกรม (เช่น รายการแขกที่ถูกย้าย) อยู่ใน `CSV/app_output/`
- ค่าตั้งต้นของระบบ (`hash_type`, `V`, salt ของอาคารและแขก) แก้ได้ที่ `data/config.json`


---

## System & Algorithm Tests

การทดสอบประสิทธิภาพเชิงเปรียบเทียบระหว่าง Consistent Hashing และ Hash Mod N ในสถานการณ์ต่างๆ ตามโจทย์ข้อ 7
ในการรันฟังก์ชันต่างๆ ต้องเข้าไปที่โฟลเดอร์ `OOD-Project` ก่อน จึงจะสามารถรันด้วย Command ด้านล่างได้

```bash
cd OOD-Project-Infinite-Hotel/OOD-Project
```

| ชุดการทดสอบ | คำสั่ง (Command) | ผลลัพธ์และสิ่งที่ระบบแสดงผล (Output) |
| :--- | :--- | :--- |
| **Test A** | `python -m test.test_A` | แสดงสถานะบน Terminal สร้างรูปกราฟ 12 ภาพ (อัลกอริทึมละ 6 ภาพ) ในโฟลเดอร์ `graph/test_A/` และไฟล์ CSV ในโฟลเดอร์ `CSV/test_A/` |
| **Test B** | `python -m test.test_B.test_B` | แสดงสถานะและผลลัพธ์บน Terminal พร้อมเปิดหน้าต่าง Pop-up แสดงกราฟเปรียบเทียบ สร้างรูปกราฟ 6 ภาพในโฟลเดอร์ `graph/GRAPH_TestB/` และไฟล์ CSV ในโฟลเดอร์ `CSV/CSV_TestB/` |
| **Test C** | `python -m test.test_C` | แสดงสถานะและผลลัพธ์บน Terminal พร้อมเปิดหน้าต่าง Pop-up แสดงกราฟเปรียบเทียบ และไฟล์ CSV ในโฟลเดอร์ `CSV/` |

### รายละเอียดผลลัพธ์ Test A

#### 📄 1. CSV Files (ตำแหน่งจัดเก็บ: `CSV/test_A/` แยกตาม `consistant_hashing/` และ `hash_mod_n/`)
สำหรับทั้ง 2 อัลกอริทึม (`consistant_hashing` และ `hash_mod_n`) ระบบจะสร้างโครงสร้างไฟล์ CSV ดังนี้:

##### โครงสร้างภายในอัลกอริทึม:
* **โฟลเดอร์การทดสอบแต่ละรอบ (`round_1/`, `round_2/`, `round_3/`):**
  1. `assign_guest.csv`
  2. `calculate_building_1000_time.csv`
  3. `current_memory_usage.csv`
  4. `ordering_guest.csv`
  5. `peak_memory_usage.csv`
  6. `search_guest.csv`

* **ไฟล์ค่ามัธยฐาน (Medians CSVs):**
  1. `medians_assign_guest.csv`
  2. `medians_calculate_building_1000_time_3_rounds.csv`
  3. `medians_current_memory_usage.csv`
  4. `medians_ordering_guest.csv`
  5. `medians_peak_memory_usage.csv`
  6. `medians_routing_space_current.csv`
  7. `medians_routing_space_peak.csv`
  8. `medians_searching_guest.csv`

#### 📈 2. Graph Files (ตำแหน่งจัดเก็บ: `graph/test_A/`)
ทั้ง 2 อัลกอริทึม (`graph/test_A/consistant_hashing/` และ `graph/test_A/hash_mod_n/`) มีไฟล์ชื่อเหมือนกัน ดังนี้:
1. `test_A_assign_search.png`
2. `test_A_ordering.png`
3. `test_A_assign_search_ordering.png`
4. `test_A_assign_search_ordering_variance.png`
5. `Test_A_memory.png`
6. `Test_A_memory_variance.png`

### รายละเอียดผลลัพธ์ Test B
#### 📄 1. CSV Files (ตำแหน่งจัดเก็บ: `CSV/CSV_TestB/`)
1. `benchmark_results_bsalt_0_csalt_0.csv`
2. `benchmark_results_bsalt_1_csalt_1.csv`
3. `benchmark_results_bsalt_2_csalt_2.csv`
4. `relocation_moves_bsalt_0_csalt_0.csv`
5. `relocation_moves_bsalt_1_csalt_1.csv`
6. `relocation_moves_bsalt_2_csalt_2.csv`
7. `customers_sample.csv`

#### 📈 2. Graph Files (ตำแหน่งจัดเก็บ: `graph/GRAPH_TestB/`)
1. `grid_metrics_bsalt_0_csalt_0.png`
2. `grid_metrics_bsalt_1_csalt_1.png`
3. `grid_metrics_bsalt_2_csalt_2.png`
4. `summary_stats_bsalt_0_csalt_0.png`
5. `summary_stats_bsalt_1_csalt_1.png`
6. `summary_stats_bsalt_2_csalt_2.png`

---

### รายละเอียดผลลัพธ์ Test C
Test C บันทึกผลลัพธ์เฉพาะ CSV : `CSV/test_C_results.csv`

---

## Unit Tests & Function Verification

การทดสอบฟังก์ชันการทำงานพื้นฐาน การจัดการข้อมูล และการรองรับกรณีขอบเขต (Edge Cases) ตามโจทย์ข้อ 9.2

### คำสั่งสำหรับรันการทดสอบ Unit Test ทั้งหมด:
รันจากโฟลเดอร์ `OOD-Project` (สคริปต์ค้นหาไฟล์ `test_*.py` ใน `test/test_functions` จาก path สัมพัทธ์)
```bash
python test/test_all_functions.py
```
ผลลัพธ์: สรุปจำนวนที่ผ่าน/ไม่ผ่านบน Terminal และบันทึกเป็น `test/test_functions/result_report_csv/overall_summary.csv`
พร้อมรายงานของแต่ละชุดทดสอบในโฟลเดอร์ `result_report_csv/` เดียวกัน

### รายละเอียดชุดการทดสอบย่อย (Test Modules):
1. **`test_1_add_customer.py`**: ทดสอบระบบการเพิ่มลูกค้าและการจัดสรรห้องพักตามอัลกอริทึม
2. **`test_2_room_conflict.py`**: ทดสอบการจัดการกรณีห้องพักเกิดข้อขัดแย้ง/ชนกัน (Collision Handling)
3. **`test_3_search_building.py`**: ทดสอบฟังก์ชันการค้นหาอาคารและตรวจสอบตำแหน่งห้องพักของลูกค้า
4. **`test_4_manage_building.py`**: ทดสอบระบบการจัดการอาคาร การเพิ่มและลดอาคารแบบ dynamic
5. **`test_5_edge_case.py`**: ทดสอบกรณีขอบเขต ข้อมูลไม่สมบูรณ์ หรือกรณีข้อยกเว้นต่างๆ (Exception & Edge Cases)





