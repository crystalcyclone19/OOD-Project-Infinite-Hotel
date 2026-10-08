import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# 1. กำหนด Root Directory
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# from generate_mock_data_csv import generate_mock_data
from .generate_mock_data_csv import generate_mock_data # Claude told me : )
from hotel_sys import HotelSystem
# from load_data_to_system import load_data_to_system
from .load_data_to_system import load_data_to_system # Claude told me : )


import time
import numpy as np

def loop_test_2_to_20(hash_type: str, function: str):
    K = 10000  # จำนวนแขกคงที่
    
    building_counts = []     # เก็บจำนวนตึก N
    relocation_rates = []    # เก็บอัตราการย้าย (%)
    execution_times = []     # เก็บเวลาเฉลี่ย/มัธยฐาน (วินาที)

    print('=' * 60)
    print(f"Total guests = {K} คน")
    print(f"Test function: {function}")
    print(f"Hash type: {hash_type}")
    print('=' * 60)
    print()

    # วนลูป N ตั้งแต่ 2 ถึง 20
    for N in range(2, 21):
        # 1. สร้างไฟล์ mock data ตามจำนวนตึก N (นอกช่วงจับเวลา)
        generate_mock_data(
            num_buildings=N, buildings_filename="buildings.csv"
        )

        times = []
        move_total_last = None

        # 2. รัน 3 รอบเพื่อหาค่า Median ตามเกณฑ์ข้อ 7.2
        for run_idx in range(3):
            print("="*25 + f"Test {run_idx} round" + "="*25)
            system = HotelSystem(
                number_of_virtual=32,
                building_salt="testB",
                customer_salt="testB",
                hash_type=hash_type
            )
            load_data_to_system(system)

            # ================= [ เริ่มจับเวลา ] =================
            start_time = time.perf_counter()

            if function == "add_building":
                new_building_id = N + 1            
                move_total = system.add_building(new_building_id)
            elif function == "remove_building":
                remove_building_id = 2
                move_total = system.remove_building(remove_building_id)
            
            end_time = time.perf_counter()
            # ================= [ สิ้นสุดจับเวลา ] =================

            time_diff = end_time - start_time
            times.append(time_diff)
            move_total_last = move_total  # เก็บผลลัพธ์ย้ายไปคำนวณ Rate
            print(f"Round {run_idx} Time : {time_diff * 1000:.3f} ms")
            time.sleep(0.2)

        # 3. เรียงเวลา 3 รอบ แล้วดึงค่ามัธยฐาน (Median)
        median_time = np.median(times)

        # 4. คำนวณอัตราการย้าย (%)
        rate = (len(move_total_last) / K) * 100

        # บันทึกข้อมูล
        building_counts.append(N)
        relocation_rates.append(rate)
        execution_times.append(median_time)

        # แสดงผลลัพธ์ประจำ N (แปลงเวลาเป็น millisecond)
        print()
        print(
            f"Building N = {N:2d} | Moved = {len(move_total_last):4d} guests | "
            f"Relocation Rate = {rate:6.3f}% | Median Time = {median_time * 1000:7.3f} ms"
        )
        print()

    # คำนวณสถิติสรุปภาพรวม
    move_mean_rate = np.mean(relocation_rates)
    move_std_rate = np.std(relocation_rates, ddof=1) #ส่วนเบี่ยงเบนมาตรฐาน
    min_rate = np.min(relocation_rates)
    max_rate = np.max(relocation_rates)

    mean_time = np.mean(execution_times)
    time_std = np.std(execution_times, ddof=1) #ส่วนเบี่ยงเบนมาตรฐาน
    min_time = np.min(execution_times)
    max_time = np.max(execution_times)

    statistics_data = {
        'mean_rate' : move_mean_rate,
        'std_rate' : move_std_rate,
        'min_rate' : min_rate,
        'max_rate' : max_rate,
        'mean_time' : mean_time,
        'std_time' : time_std,
        'min_time' : min_time,
        'max_time' : max_time,
    }

    print("\n" + "=" * 50)
    print("สรุปผลสถิติการทดลอง B (Relocation Rate & Time Summary)")
    print("=" * 50)
    print(f"อัตราการย้ายเฉลี่ย                     : {move_mean_rate:.3f}%")
    print(f"ส่วนเบี่ยงเบนมาตรฐานของอัตราการย้าย     : {move_std_rate:.3f}%")
    print(f"อัตราย้ายต่ำสุด (Min rate)            : {min_rate:.3f}%")
    print(f"อัตราย้ายสูงสุด (Max rate)            : {max_rate:.3f}%")
    print()
    print(f"เวลาเฉลี่ยในการ {function}                  : {mean_time * 1000:.3f} ms")
    print(f"ส่วนเบี่ยงเบนมาตรฐานของเวลาในการ {function}  : {time_std * 1000:.3f} ms")
    print(f"เวลาต่ำสุด (Min time)                    : {min_time * 1000:.3f}ms")
    print(f"เวลาสูงสุด (Max time)                    : {max_time * 1000:.3f}ms")
    print("=" * 50)

    return building_counts, relocation_rates, execution_times, statistics_data

def plot_building_vs_metrics(building_counts: list, relocation_rates: list, execution_times: list, hash_type: str, function: str):
    """
    พล็อตกราฟเปรียบเทียบ 2 กรอบ (บน-ล่าง):
    - กรอบบน: อัตราการย้าย Relocation Rate (%) [สีน้ำเงิน]
    - กรอบล่าง: เวลาในการประมวลผล Execution Time (ms) [สีแดง] ปรับสเกลแกน Y เริ่มจาก 0
    """
    # แปลงเวลาจากวินาที (s) เป็นมิลลิวินาที (ms)
    times_ms = [t * 1000 for t in execution_times]

    # สร้างพื้นที่พล็อตขนาด 10x10 นิ้ว แบ่งเป็น 2 แถว 1 คอลัมน์ (ใช้ X-axis ร่วมกัน)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True, layout="constrained")
    fig.suptitle(f"Experiment: {hash_type} | Function: {function}", fontsize=14, fontweight='bold')

    # -----------------------------------------------------------------
    # กรอบบน: Relocation Rate (%)
    # -----------------------------------------------------------------
    ax1.plot(
        building_counts,
        relocation_rates,
        marker="o",
        color="#1f77b4",  # สีน้ำเงิน (Steel Blue)
        linestyle="--",
        linewidth=2,
        markersize=6,
        label="Relocation Rate (%)"
    )
    ax1.set_ylabel("Relocation Rate (%)", fontsize=12)
    ax1.set_title("Relocation Rate vs Number of Buildings (N) : (Top graph)", fontsize=13, pad=10)
    ax1.grid(True, linestyle="--", alpha=0.6)

    # ปรับแกน Y ของกราฟบนเริ่มจาก 0 และเผื่อขอบบนไม่ให้ตัวอักษรโดนตัด
    max_rate = max(relocation_rates) if relocation_rates else 100
    ax1.set_ylim(0, max_rate * 1.15)

    # แสดง Label เปอร์เซ็นต์กำกับจุดในกราฟบน
    for x, y in zip(building_counts, relocation_rates):
        ax1.annotate(
            f"{y:.2f}%",
            (x, y),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )
    ax1.legend(loc="upper right")

    # -----------------------------------------------------------------
    # กรอบล่าง: Execution Time (ms)
    # -----------------------------------------------------------------
    ax2.plot(
        building_counts,
        times_ms,
        marker="s",       # มาร์กเกอร์สี่เหลี่ยม
        color="#d62728",  # สีแดงอมส้ม (Crimson Red)
        linestyle="-",
        linewidth=1.8,
        markersize=6,
        label="Execution Time (ms)"
    )

    # 1. คำนวณค่าเฉลี่ยเวลา และเพิ่มเส้นอ้างอิงแนวนอน (Baseline) สะท้อนแนวโน้ม Sideway
    mean_time = np.mean(times_ms) if times_ms else 0
    ax2.axhline(
        y=mean_time,
        color="#444444",
        linestyle=":",
        linewidth=1.5,
        label=f"Mean Time ({mean_time:.1f} ms)"
    )

    # 2. ปรับแกน Y ของกราฟล่างให้เริ่มต้นจาก 0 ms เสมอ และเผื่อขอบบนไม่ให้ตัวอักษรชนขอบ
    max_time = max(times_ms) if times_ms else 100
    ax2.set_ylim(0, max_time * 1.20)

    ax2.set_xlabel("Number of Buildings (N)", fontsize=12)
    ax2.set_ylabel("Execution Time (ms)", fontsize=12)
    ax2.set_title("Execution Time vs Number of Buildings (N) : (Bottom graph)", fontsize=13, pad=10)
    ax2.grid(True, linestyle="--", alpha=0.6)

    # แสดง Label ค่าเวลา (ms) กำกับจุดในกราฟล่าง
    for x, y in zip(building_counts, times_ms):
        ax2.annotate(
            f"{y:.1f}ms",
            (x, y),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )
    ax2.legend(loc="upper right")

    # ปรับแต่งระยะห่างช่องไฟ
    # plt.tight_layout()
    # plt.show()

def plot_statistics_minmax(
    labels: list, 
    rate_mean: list, rate_min: list, rate_max: list, 
    time_mean: list, time_min: list, time_max: list
):
    colors = ['#1f77b4', '#1f77b4', '#ff7f0e', '#ff7f0e']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")

    # แปลงเวลาเป็น ms
    time_mean = [t * 1000 for t in time_mean]
    time_min = [t * 1000 for t in time_min]
    time_max = [t * 1000 for t in time_max]

    for i in range(len(labels)):
        lbl_hash = 'Hash mod N' if i == 0 else ('Consistent Hash' if i == 2 else None)
        
        # คำนวณระยะลงล่างและขึ้นบน
        rate_yerr = [[rate_mean[i] - rate_min[i]], [rate_max[i] - rate_mean[i]]]
        time_yerr = [[time_mean[i] - time_min[i]], [time_max[i] - time_mean[i]]]

        ax1.errorbar(
            labels[i], rate_mean[i], yerr=rate_yerr, 
            fmt='o', color=colors[i], ecolor=colors[i], 
            capsize=5, capthick=1.5, markersize=8, label=lbl_hash
        )
        ax2.errorbar(
            labels[i], time_mean[i], yerr=time_yerr, 
            fmt='o', color=colors[i], ecolor=colors[i], 
            capsize=5, capthick=1.5, markersize=8, label=lbl_hash
        )

        # -------------------------------------------------------------
        # 1. แสดงค่า Min, Mean, Max บนกราฟ Relocation Rate (%)
        # -------------------------------------------------------------
        ax1.annotate(f"Max: {rate_max[i]:.2f}%", (i, rate_max[i]), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold', color=colors[i])
        ax1.annotate(f"Mean: {rate_mean[i]:.2f}%", (i, rate_mean[i]), textcoords="offset points", xytext=(10, -3), ha='left', fontsize=8)
        ax1.annotate(f"Min: {rate_min[i]:.2f}%", (i, rate_min[i]), textcoords="offset points", xytext=(0, -14), ha='center', fontsize=8, color=colors[i])

        # -------------------------------------------------------------
        # 2. แสดงค่า Min, Mean, Max บนกราฟ Execution Time (ms)
        # -------------------------------------------------------------
        ax2.annotate(f"Max: {time_max[i]:.2f}ms", (i, time_max[i]), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold', color=colors[i])
        ax2.annotate(f"Mean: {time_mean[i]:.2f}ms", (i, time_mean[i]), textcoords="offset points", xytext=(10, -3), ha='left', fontsize=8)
        ax2.annotate(f"Min: {time_min[i]:.2f}ms", (i, time_min[i]), textcoords="offset points", xytext=(0, -14), ha='center', fontsize=8, color=colors[i])

    # เส้นเชื่อมระหว่างจุด
    ax1.plot(labels, rate_mean, linestyle=':', color='gray', alpha=0.5, zorder=1)
    ax2.plot(labels, time_mean, linestyle=':', color='gray', alpha=0.5, zorder=1)

    # ขยายขอบแกน Y เผื่อพื้นที่ให้ Text แสดงครบ ไม่โดนตัดขอบ
    ax1.set_ylim(0, max(rate_max) * 1.18)
    ax2.set_ylim(0, max(time_max) * 1.18)

    ax1.set_title('Relocation Rate (Min, Mean, Max)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Relocation Rate (%)', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')

    ax2.set_title('Execution Time (Min, Mean, Max)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Time (ms)', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')

if __name__ == "__main__":
    order = {
        1 : ("mod_n", "add_building"),
        2 : ("mod_n", "remove_building"),
        3 : ("consistent", "add_building"), 
        4 : ("consistent", "remove_building"),
    }

    labels = []
    rate_mean = []
    rate_min = []
    rate_max = []
    time_mean = []
    time_min = []
    time_max = []

    for key, (hash_type, function) in order.items():

        building_counts, relocation_rates, execution_times, statistics_data = loop_test_2_to_20(
            hash_type=hash_type, 
            function=function
        )

        plot_building_vs_metrics(
            building_counts, 
            relocation_rates, 
            execution_times,
            hash_type,
            function
        )
        
        labels.append(f"{function}\n({hash_type})")

        rate_mean.append(statistics_data['mean_rate'])
        rate_min.append(statistics_data['min_rate'])
        rate_max.append(statistics_data['max_rate'])

        time_mean.append(statistics_data['mean_time'])
        time_min.append(statistics_data['min_time'])
        time_max.append(statistics_data['max_time'])

    plot_statistics_minmax(
        labels=labels, 
        rate_mean=rate_mean, rate_min=rate_min, rate_max=rate_max, 
        time_mean=time_mean, time_min=time_min, time_max=time_max
    )
            
    plt.show()
        
        


   