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

1. **Python:** ภาษา Python เวอร์ชัน 3.9 ขึ้นไป
2. **การติดตั้ง Dependencies:** (รันที่โฟลเดอร์โปรเจกต์หลัก `OOD-Project-Infinite-Hotel/`)
   ```bash
   cd OOD-Project-Infinite-Hotel
   pip install -r requirements.txt
   ```

---

## โครงสร้างโฟลเดอร์ที่สำคัญ

```text
OOD-Project-Infinite-Hotel/            # โฟลเดอร์โปรเจกต์หลักที่รวมทุกอย่างไว้ด้านใน
├── README.md                          # เอกสารภาพรวมและวิธีการรันระบบ/การทดสอบ
├── manual.md                          # คู่มือการใช้งาน Interactive CLI (app.py) อย่างละเอียด
├── requirements.txt                   # รายการไลบรารีที่จำเป็น
└── OOD-Project/                       # โฟลเดอร์ซอร์สโค้ดหลัก
    ├── app.py                         # โปรแกรมหลัก (Interactive CLI / Text UI)
    ├── hotel_sys.py                   # คลาสหลักของระบบ: HotelSystem, Customer, BuildingWithRoom, MovedCustomer
    ├── HashRing.py                    # HashHelper, VirtualNode, HashRing (Consistent Hashing), HashModN
    ├── AVLTree.py                     # AVLTree (AVLNormalTree, AVLClassTree) ใช้เก็บข้อมูลเรียงลำดับ
    ├── data/                          # ข้อมูลที่ app.py โหลด/บันทึก (สร้างอัตโนมัติ)
    │   ├── config.json                # ค่า hash_type, V, salt ของอาคารและแขก
    │   ├── buildings.csv              # รหัสอาคาร เรียงตามลำดับที่เพิ่ม
    │   └── guests.csv                 # channel_id, sequence_id, node_id, room_no
    ├── util/                          # ฟังก์ชันช่วยเหลือและคำนวณ
    │   ├── csv_sys.py                 # อ่าน/เขียนไฟล์ CSV
    │   ├── graph.py                   # สร้างกราฟผลลัพธ์
    │   ├── timer.py                   # จับเวลาการทำงาน
    │   ├── memory_usage.py            # วัดการใช้หน่วยความจำ
    │   ├── math.py                    # ฟังก์ชันคำนวณ (ค่ามัธยฐาน, ความแปรปรวน, Regression)
    │   └── color.py                   # แสดงผลข้อความสีบน Terminal
    ├── graph/                         # รูปกราฟผลลัพธ์จากการทดสอบ
    │   ├── test_A/                    # กราฟ Test A (แยก consistant_hashing/ และ hash_mod_n/)
    │   └── GRAPH_TestB/               # กราฟ Test B
    ├── CSV/                           # ไฟล์ CSV ผลลัพธ์
    │   ├── test_A/                    # CSV Test A (แยก consistant_hashing/ และ hash_mod_n/)
    │   ├── CSV_TestB/                 # CSV Test B
    │   ├── app_output/                # CSV ที่ app.py ส่งออก (เช่น รายการแขกที่ถูกย้าย)
    │   ├── test_C_results.csv         # CSV ผลลัพธ์ Test C
    │   ├── test_parameter_ref.md      # เอกสารอ้างอิงพารามิเตอร์การทดสอบ
    │   └── test_functions_csv/        # รายงานผลลัพธ์ Unit Test ทั้งหมด
    │       ├── overall_summary.csv    # สรุปภาพรวมผลการรัน Unit Test ทุกชุด
    │       ├── test_add_customer_csv/
    │       ├── test_room_conflict_csv/
    │       ├── test_search_building_csv/
    │       ├── test_manage_building_csv/
    │       └── test_edge_case/
    └── test/                          # ชุดทดสอบและสคริปต์การทดสอบ
        ├── test_A.py                  # สคริปต์การทดสอบ Test A (ประสิทธิภาพ 3 รอบ)
        ├── test_B/                    # สคริปต์และข้อมูลจำลอง Test B (Rebalance)
        │   ├── test_B.py              # สคริปต์หลัก Test B
        │   ├── generate_mock_data_csv.py   # สร้างข้อมูลจำลอง
        │   ├── load_data_to_system.py      # โหลดข้อมูลเข้าระบบ
        │   ├── buildings.csv          # ข้อมูลอาคารจำลอง
        │   └── guests.csv             # ข้อมูลแขกจำลอง
        ├── test_C.py                  # สคริปต์การทดสอบ Test C (Load Balancing & CV)
        ├── test_all_functions.py      # สคริปต์รัน Unit Test ทั้งหมด พร้อมสรุปผล
        └── test_functions/            # ชุด Unit Test ทดสอบฟังก์ชันแต่ละส่วน (9.2)
            ├── test_1_add_customer.py     # ทดสอบเพิ่มแขก/จัดสรรห้อง
            ├── test_2_room_conflict.py    # ทดสอบ Cantor Pairing Function & ตรวจจับห้องชน
            ├── test_3_search_building.py  # ทดสอบการค้นหาอาคารบนวงแหวน
            ├── test_4_manage_building.py  # ทดสอบการเพิ่ม/ลบอาคารแบบ dynamic
            ├── test_5_edge_case.py        # ทดสอบกรณีขอบเขต (Edge Cases ตามข้อ 4.5)
            ├── test_set_csv/              # ข้อมูลตั้งต้นสำหรับทดสอบ (buildings, customers)
            └── test_list.md               # รายการทดสอบขั้นต่ำตามข้อกำหนด
```

---

## การรันโปรแกรมหลัก

โปรแกรมหลักเป็น Interactive CLI / Text UI ในไฟล์ `app.py` สามารถรันได้โดย `cd` เข้าผ่าน `OOD-Project-Infinite-Hotel`:

```bash
cd OOD-Project-Infinite-Hotel/OOD-Project
python app.py
```

หรือหากอยู่ที่โฟลเดอร์ `OOD-Project-Infinite-Hotel/`:
```bash
python OOD-Project/app.py
```

- **การโหลดข้อมูล:** ตอนเริ่มโปรแกรม หากมีข้อมูลเดิมใน `data/` (`config.json`, `buildings.csv`, `guests.csv`) ระบบจะถามว่าต้องการโหลดหรือไม่ หากเลือกไม่โหลด จะเข้าสู่ขั้นตอนตั้งค่าระบบใหม่ (เลือก Hash Type, V, จำนวนอาคารเริ่มต้น, Salt ฯลฯ)
- **การบันทึกข้อมูล:** ข้อมูลหลักทำงานบนหน่วยความจำ และมีการซิงค์บันทึกลง `data/` อัตโนมัติเมื่อเกิดการเปลี่ยนแปลง
- **การส่งออก CSV:** ไฟล์ CSV ที่ export จากโปรแกรม (เช่น รายการแขกที่ถูกย้ายเมื่อเพิ่ม/ลบอาคาร) จะถูกเก็บไว้ใน `CSV/app_output/`
- **คู่มือการใช้งานแบบละเอียด:** ศึกษาเมนู คำสั่ง และตัวอย่างการใช้งานทั้งหมดได้ที่ [manual.md](manual.md)

---

## System & Algorithm Tests

การทดสอบประสิทธิภาพเชิงเปรียบเทียบระหว่าง Consistent Hashing และ Hash Mod N ในมิติต่างๆ ตามโจทย์ข้อ 7  
> **ข้อแนะนำ:** การรันคำสั่งทั้งหมดต้องเข้าไปที่โฟลเดอร์ `OOD-Project` ผ่าน `OOD-Project-Infinite-Hotel`:
> ```bash
> cd OOD-Project-Infinite-Hotel/OOD-Project
> ```

| ชุดการทดสอบ | คำสั่ง (Command)                  | ผลลัพธ์และสิ่งที่ระบบแสดงผล (Output)                                                                                                                             |
| :--------- | :----------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test A** | `python -m test.test_A`        | แสดงสถานะบน Terminal สร้างรูปกราฟ 12 ภาพ (อัลกอริทึมละ 6 ภาพ) ในโฟลเดอร์ `graph/test_A/` และไฟล์ CSV ในโฟลเดอร์ `CSV/test_A/`                                      |
| **Test B** | `python -m test.test_B.test_B` | แสดงสถานะและ progress bar บน Terminal พร้อมหน้าต่าง Pop-up กราฟเปรียบเทียบ สร้างรูปกราฟ 6 ภาพในโฟลเดอร์ `graph/GRAPH_TestB/` และไฟล์ CSV ในโฟลเดอร์ `CSV/CSV_TestB/` |
| **Test C** | `python -m test.test_C`        | แสดงสถานะและผลลัพธ์บน Terminal พร้อมหน้าต่าง Pop-up แสดงกราฟเปรียบเทียบ และบันทึกไฟล์สรุปใน `CSV/test_C_results.csv`                                                  |

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

การทดสอบฟังก์ชันการทำงานพื้นฐาน การจัดการข้อมูล และการรองรับกรณีขอบเขต (Edge Cases) ตามข้อกำหนดโจทย์ 9.2

### วิธีการรัน Unit Test ทั้งหมด:

สามารถรันสคริปต์ `test_all_functions.py` ได้ทั้งจากโฟลเดอร์หลักและโฟลเดอร์ `OOD-Project/`:

- **รันจากโฟลเดอร์โปรเจกต์หลัก (`OOD-Project-Infinite-Hotel/`):**
  ```bash
  python OOD-Project/test/test_all_functions.py
  ```

- **หรือ cd เข้าไปที่ `OOD-Project/` ผ่าน `OOD-Project-Infinite-Hotel`:**
  ```bash
  cd OOD-Project-Infinite-Hotel/OOD-Project
  python test/test_all_functions.py
  ```

- **หรือรันผ่าน `unittest discover` ใน `OOD-Project/`:**
  ```bash
  cd OOD-Project-Infinite-Hotel/OOD-Project
  python -m unittest discover -s test/test_functions -p "test_*.py"
  ```

**ผลลัพธ์การทดสอบ:**
- แสดงตารางสรุปจำนวน Test Case ที่รัน ทั้งหมด ผ่าน, ไม่ผ่าน, ข้อผิดพลาด (Passed / Failed / Errors) ทาง Terminal
- บันทึกผลสรุปภาพรวมลงไฟล์ CSV ที่:
  `OOD-Project/CSV/test_functions_csv/overall_summary.csv`
- บันทึกไฟล์ CSV ผลการทดสอบโดยละเอียดของแต่ละโมดูลแยกโฟลเดอร์ใน `OOD-Project/CSV/test_functions_csv/`

---

### รายละเอียดชุดการทดสอบย่อย (Test Modules):

สามารถแยกรันแต่ละไฟล์เดี่ยวๆ ได้ตามต้องการ (โดย cd เข้าไปที่ `OOD-Project-Infinite-Hotel/OOD-Project`):

| ไฟล์ทดสอบ                        | คำสั่งรันเดี่ยว (ใน `OOD-Project/`)                          | รายละเอียดและสิ่งที่ทดสอบ                                                                      | โฟลเดอร์ CSV ผลลัพธ์                                  |
| :------------------------------ | :----------------------------------------------------- | :---------------------------------------------------------------------------------------- | :------------------------------------------------- |
| **`test_1_add_customer.py`**    | `python test/test_functions/test_1_add_customer.py`    | ทดสอบเพิ่มแขกเดี่ยว/กลุ่ม ทั้งช่องทางเดิมและใหม่ พร้อมยืนยันว่าแขกเดิมไม่ถูกเปลี่ยนห้อง                        | `CSV/test_functions_csv/test_add_customer_csv/`    |
| **`test_2_room_conflict.py`**   | `python test/test_functions/test_2_room_conflict.py`   | ทดสอบสมการ Cantor Pairing Function ตรวจสอบว่า c และ s ต่างกันจะไม่ได้เลขห้องซ้ำกัน                 | `CSV/test_functions_csv/test_room_conflict_csv/`   |
| **`test_3_search_building.py`** | `python test/test_functions/test_3_search_building.py` | ทดสอบค้นหาอาคารตรงจุดพอดี ระหว่างจุด และกรณีวนลูปกลับจุดเริ่มต้นของวงแหวน                             | `CSV/test_functions_csv/test_search_building_csv/` |
| **`test_4_manage_building.py`** | `python test/test_functions/test_4_manage_building.py` | ทดสอบการเพิ่ม/ลบอาคารขณะ V > 1 ตรวจสอบความถูกต้องของการย้ายแขกและยอดแขกรวม                     | `CSV/test_functions_csv/test_manage_building_csv/` |
| **`test_5_edge_case.py`**       | `python test/test_functions/test_5_edge_case.py`       | ทดสอบกรณีขอบเขต (Edge Cases ตามข้อ 4.5 ทั้งหมด 9 กรณี) เช่น อาคารซ้ำ, ลบอาคารไม่พบ, input ติดลบ/ศูนย์ | `CSV/test_functions_csv/test_edge_case/`           |





