# OOD Project: Infinite Hotel

โปรเจกต์การจำลองและการทดสอบประสิทธิภาพระบบการจัดการข้อมูลสำหรับ **Infinite Hotel** (Consistent Hashing vs Hash Mod N)

---

## สารบัญ
- [ข้อกำหนดเบื้องต้นและการติดตั้ง (Prerequisites & Installation)](#-ข้อกำหนดเบื้องต้นและการติดตั้ง)
- [โครงสร้างโฟลเดอร์ (Directory Structure)](#โครงสร้างโฟลเดอร์ที่สำคัญ)
- [7.2 System & Algorithm Tests](#72-system--algorithm-tests)
- [9.2 Unit Tests & Function Verification](#-92-unit-tests--function-verification)

---

## 🛠 ข้อกำหนดเบื้องต้นและการติดตั้ง

1. **Python:** ภาษา Python เวอร์ชัน 3.8 ขึ้นไป
2. **การติดตั้ง Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## โครงสร้างโฟลเดอร์ที่สำคัญ

```text
OOD-Project-Infinite-Hotel/
├── graph/                         # โฟลเดอร์เก็บรูปภาพกราฟผลลัพธ์จาก Test A, Test B
│   ├── test_A/                    # กราฟจาก Test A
│   └── GRAPH_TestB/               # กราฟจาก Test B
├── CSV/                           # โฟลเดอร์เก็บไฟล์ CSV จาก Process ต่างๆ
│   ├── test_A/                    # ไฟล์ CSV จาก Test A
│   └── CSV_TestB/                 # ไฟล์ CSV จาก Test B
└── test/                          # โฟลเดอร์เก็บ Script สำหรับรันการทดสอบ
    ├── test_A.py                  # Function run test_A
    ├── test_B/
    │   └── test_B.py              # Function run test_B
    ├── test_C.py                  # Function run test_C
    ├── test_all_functions.py      # Validation Function follow 9.2
    └── test_functions/            # ชุด Unit Test สำหรับทดสอบแต่ละฟังก์ชัน (9.2)
        ├── test_all_function.py
        ├── test_add_customer.py
        ├── test_room_conflict.py
        ├── test_search_building.py
        ├── test_manage_building.py
        └── test_edge_case.py
```

---

## 7.2 System & Algorithm Tests

การทดสอบประสิทธิภาพเชิงเปรียบเทียบระหว่าง Consistent Hashing และ Hash Mod N ในสถานการณ์ต่างๆ
ในการรันฟังก์ชันต่างๆ ต้องเข้าไปที่โฟลเดอร์โปรเจกต์ OOD-Project ก่อน จึงจะสามารถรันด้วย Command ด้านล่างได้

```bash
cd OOD-Project
```

| ชุดการทดสอบ | คำสั่ง (Command) | ผลลัพธ์และสิ่งที่ระบบแสดงผล (Output) |
| :--- | :--- | :--- |
| **Test A** | `python -m test.test_A` | แสดงสถานะบน Terminal สร้างรูปกราฟ 10 ภาพ (อัลกอริทึมละ 5 ภาพ) ในโฟลเดอร์ `graph/test_A/` และไฟล์ CSV ในโฟลเดอร์ `CSV/test_A/` |
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
  2. `medians_calculate_building_1000_time_3_round.csv`
  3. `medians_current_memory_usage.csv`
  4. `medians_ordering_guest.csv`
  5. `medians_peak_memory_usage.csv`
  6. `medians_routing_space_current.csv`
  7. `medians_routing_space_peak.csv`
  8. `medians_searching_guest.csv`

#### 📈 2. Graph Files (ตำแหน่งจัดเก็บ: `graph/test_A/`)
#### `graph/test_A/consistent_hashing/`
1. `test_A_consistant_hashing_assgin_search.png`
2. `test_A_consistant_hashing_ordering.png`
3. `test_A_consistant_hashing_memeory.png`
4. `test_A_consistant_hashing_assgin_ordering_variance.png`
5. `test_A_consistant_hashing_memeory_variance.png`
#### `graph/test_A/hash_mod_n/`
1. `test_A_hash_mod_n_assgin_search.png`
2. `test_A_hash_mod_n_ordering.png`
3. `test_A_hash_mod_n_memeory.png`
4. `test_A_hash_mod_n_assgin_ordering_variance.png`
5. `test_A_hash_mod_n_memeory_variance.png`

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

## 🧪 9.2 Unit Tests & Function Verification

การทดสอบฟังก์ชันการทำงานพื้นฐาน การจัดการข้อมูล และการรองรับกรณีขอบเขต (Edge Cases)

### คำสั่งสำหรับรันการทดสอบ Unit Test ทั้งหมด:
```bash
python -m test.test_functions.test_all_function
```

### รายละเอียดชุดการทดสอบย่อย (Test Modules):
1. **`test_add_customer.py`**: ทดสอบระบบการเพิ่มลูกค้าและการจัดสรรห้องพักตามอัลกอริทึม
2. **`test_room_conflict.py`**: ทดสอบการจัดการกรณีห้องพักเกิดข้อขัดแย้ง/ชนกัน (Collision Handling)
3. **`test_search_building.py`**: ทดสอบฟังก์ชันการค้นหาอาคารและตรวจสอบตำแหน่งห้องพักของลูกค้า
4. **`test_manage_building.py`**: ทดสอบระบบการจัดการอาคาร การเพิ่มและลดอาคารแบบ dynamic
5. **`test_edge_case.py`**: ทดสอบกรณีขอบเขต ข้อมูลไม่สมบูรณ์ หรือกรณีข้อยกเว้นต่างๆ (Exception & Edge Cases)
