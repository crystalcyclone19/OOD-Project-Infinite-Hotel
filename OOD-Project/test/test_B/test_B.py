import os
import sys
import time
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



def loop_test_2_to_20(hash_type: str, function: str, K: int, building_salt: str, customer_salt: str):
    building_counts = []
    relocation_rates = []
    execution_times = []

    print('=' * 60)
    print(f"Total guests = {K} คน | Salt: B='{building_salt}', C='{customer_salt}'")
    print(f"Test function: {function} | Hash type: {hash_type}")
    print('=' * 60)

    for N in range(2, 21):
        generate_mock_data(num_buildings=N, buildings_filename="buildings.csv")
        times = []
        move_total_last = None

        for run_idx in range(3):
            system = HotelSystem(
                number_of_virtual=32,
                building_salt=building_salt,
                customer_salt=customer_salt,
                hash_type=hash_type
            )
            load_data_to_system(system)

            start_time = time.perf_counter()
            if function == "add_building":
                move_total = system.add_building(N + 1)
            elif function == "remove_building":
                move_total = system.remove_building(2)
            end_time = time.perf_counter()

            time_diff = end_time - start_time
            times.append(time_diff)
            move_total_last = move_total

        median_time = np.median(times)
        rate = (len(move_total_last) / K) * 100

        building_counts.append(N)
        relocation_rates.append(rate)
        execution_times.append(median_time)

    # คำนวณสถิติ
    move_mean_rate = np.mean(relocation_rates)
    move_std_rate = np.std(relocation_rates, ddof=1)
    min_rate = np.min(relocation_rates)
    max_rate = np.max(relocation_rates)

    mean_time = np.mean(execution_times)
    time_std = np.std(execution_times, ddof=1)
    min_time = np.min(execution_times)
    max_time = np.max(execution_times)

    statistics_data = {
        'mean_rate': move_mean_rate, 'std_rate': move_std_rate,
        'min_rate': min_rate, 'max_rate': max_rate,
        'mean_time': mean_time, 'std_time': time_std,
        'min_time': min_time, 'max_time': max_time,
    }

    return building_counts, relocation_rates, execution_times, statistics_data


def plot_all_experiments_grid(results_map: dict, K: int, building_salt: str, customer_salt: str):
    """
    รวมผลการทดสอบทั้ง 4 แบบลงใน Window เดียวกัน (2 แถว x 4 คอลัมน์)
    - ปรับสเกลแกน Y ร่วมกันให้เห็นแนวโน้ม Sideway ชัดเจน
    - ปรับการวางตำแหน่ง Text สลับขึ้น-ลง ไม่ให้ทับเส้นหรือชนขอบ
    """
    fig, axes = plt.subplots(2, 4, figsize=(22, 10), sharex=True, layout="constrained")

    param_text = f"Parameters: K = {K:,} guests | Building Salt = '{building_salt}' | Customer Salt = '{customer_salt}'"
    fig.suptitle(f"Benchmark Results (N = 2..20)\n{param_text}", fontsize=14, fontweight='bold')

    order_keys = [
        ("mod_n", "add_building"),
        ("mod_n", "remove_building"),
        ("consistent", "add_building"),
        ("consistent", "remove_building")
    ]

    # 📌 1. คำนวณหา Execution Time สูงสุดจากทุกเคสการทดลอง เพื่อใช้แกน Y สเกลเดียวกันทั้งหมด
    all_max_time_ms = max(
        [max(exec_times) * 1000 for _, _, exec_times, _ in results_map.values() if exec_times]
    )
    # ล็อคขอบบนแกน Y ของกราฟเวลา เผื่อพื้นที่ 25% สำหรับวางตัวเลข
    y_time_limit = max(all_max_time_ms * 1.25, 100)

    for col_idx, key in enumerate(order_keys):
        hash_type, function = key
        b_counts, rel_rates, exec_times, _ = results_map[key]
        times_ms = [t * 1000 for t in exec_times]

        ax_rate = axes[0, col_idx]
        ax_time = axes[1, col_idx]

        title_str = f"{hash_type.upper()} : {function}"

        # -------------------------------------------------------------
        # แถวบน: Relocation Rate (%)
        # -------------------------------------------------------------
        ax_rate.plot(b_counts, rel_rates, marker="o", color="#1f77b4", linestyle="--", linewidth=1.8, markersize=5)
        ax_rate.set_title(title_str, fontsize=11, fontweight='bold')
        ax_rate.set_ylabel("Relocation Rate (%)" if col_idx == 0 else "", fontsize=10)
        ax_rate.grid(True, linestyle="--", alpha=0.5)

        # เผื่อขอบบนแกน Y 20%
        max_r = max(rel_rates) if rel_rates else 100
        ax_rate.set_ylim(0, max_r * 1.20)

        # สลับตำแหน่งตัวเลข ขึ้น-ลง เพื่อป้องกันการบังกันเอง
        for idx, (x, y) in enumerate(zip(b_counts, rel_rates)):
            offset_y = 6 if idx % 2 == 0 else -12
            ax_rate.annotate(
                f"{y:.1f}%",
                (x, y),
                textcoords="offset points",
                xytext=(0, offset_y),
                ha="center",
                fontsize=6.5
            )

        # -------------------------------------------------------------
        # แถวล่าง: Execution Time (ms)
        # -------------------------------------------------------------
        ax_time.plot(b_counts, times_ms, marker="s", color="#d62728", linestyle="-", linewidth=1.5, markersize=5)

        mean_t = np.mean(times_ms) if times_ms else 0
        ax_time.axhline(y=mean_t, color="#444444", linestyle=":", linewidth=1.2, label=f"Mean: {mean_t:.1f}ms")

        ax_time.set_xlabel("Buildings (N)", fontsize=10)
        ax_time.set_ylabel("Execution Time (ms)" if col_idx == 0 else "", fontsize=10)
        ax_time.grid(True, linestyle="--", alpha=0.5)

        # 📌 ล็อคแกน Y เริ่มจาก 0 และใช้สเกลเดียวกันทุกคอลัมน์ ช่วยให้เห็น Sideway ชัดเจน
        ax_time.set_ylim(0, y_time_limit)
        ax_time.legend(loc="upper right", fontsize=8)

        # สลับตำแหน่งตัวเลข ขึ้น-ลง (ตัดคำว่า ms ออกเพื่อประหยัดพื้นที่เนื้อที่)
        for idx, (x, y) in enumerate(zip(b_counts, times_ms)):
            offset_y = 6 if idx % 2 == 0 else -12
            ax_time.annotate(
                f"{y:.1f}",
                (x, y),
                textcoords="offset points",
                xytext=(0, offset_y),
                ha="center",
                fontsize=6.5
            )


def plot_summary_minmax_std(labels: list, stats_list: list, K: int, building_salt: str, customer_salt: str):
    """
    พล็อตกราฟสรุปค่า Mean / Min / Max พร้อมระบุส่วนเบี่ยงเบนมาตรฐาน (SD) ไว้ด้านล่าง
    และลากเส้นประเชื่อมจุด Mean ของแต่ละอัลกอริทึม
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
    
    param_text = f"Parameters: K = {K:,} guests | Building Salt = '{building_salt}' | Customer Salt = '{customer_salt}'"
    fig.suptitle(f"Overall Statistics Comparison\n{param_text}", fontsize=13, fontweight='bold')

    colors = ['#1f77b4', '#1f77b4', '#ff7f0e', '#ff7f0e']

    rate_mean = [s['mean_rate'] for s in stats_list]
    rate_min = [s['min_rate'] for s in stats_list]
    rate_max = [s['max_rate'] for s in stats_list]
    rate_std = [s['std_rate'] for s in stats_list]

    time_mean = [s['mean_time'] * 1000 for s in stats_list]
    time_min = [s['min_time'] * 1000 for s in stats_list]
    time_max = [s['max_time'] * 1000 for s in stats_list]
    time_std = [s['std_time'] * 1000 for s in stats_list]

    # -------------------------------------------------------------
    # 📌 เพิ่มเส้นประเชื่อมจุด Mean สำหรับแต่ละกลุ่มอัลกอริทึม
    # -------------------------------------------------------------
    # 1. กลุ่ม Hash Mod N (จุดที่ 0 ถึง 1)
    ax1.plot(labels[:2], rate_mean[:2], linestyle=':', color='#1f77b4', alpha=0.7, zorder=1)
    ax2.plot(labels[:2], time_mean[:2], linestyle=':', color='#1f77b4', alpha=0.7, zorder=1)

    # 2. กลุ่ม Consistent Hash (จุดที่ 2 ถึง 3)
    ax1.plot(labels[2:], rate_mean[2:], linestyle=':', color='#ff7f0e', alpha=0.7, zorder=1)
    ax2.plot(labels[2:], time_mean[2:], linestyle=':', color='#ff7f0e', alpha=0.7, zorder=1)

    for i in range(len(labels)):
        lbl_hash = 'Hash Mod N' if i == 0 else ('Consistent Hash' if i == 2 else None)

        rate_yerr = [[rate_mean[i] - rate_min[i]], [rate_max[i] - rate_mean[i]]]
        time_yerr = [[time_mean[i] - time_min[i]], [time_max[i] - time_mean[i]]]

        # Graph 1: Relocation Rate
        ax1.errorbar(labels[i], rate_mean[i], yerr=rate_yerr, fmt='o', color=colors[i], capsize=5, capthick=1.5, markersize=8, label=lbl_hash, zorder=2)
        ax1.annotate(f"Max: {rate_max[i]:.2f}%", (i, rate_max[i]), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold', color=colors[i])
        ax1.annotate(f"Mean: {rate_mean[i]:.2f}%\n(SD: ±{rate_std[i]:.2f}%)", (i, rate_mean[i]), textcoords="offset points", xytext=(12, -8), ha='left', fontsize=8)
        ax1.annotate(f"Min: {rate_min[i]:.2f}%", (i, rate_min[i]), textcoords="offset points", xytext=(0, -14), ha='center', fontsize=8, color=colors[i])

        # Graph 2: Execution Time
        ax2.errorbar(labels[i], time_mean[i], yerr=time_yerr, fmt='o', color=colors[i], capsize=5, capthick=1.5, markersize=8, label=lbl_hash, zorder=2)
        ax2.annotate(f"Max: {time_max[i]:.2f}ms", (i, time_max[i]), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, fontweight='bold', color=colors[i])
        ax2.annotate(f"Mean: {time_mean[i]:.2f}ms\n(SD: ±{time_std[i]:.2f}ms)", (i, time_mean[i]), textcoords="offset points", xytext=(12, -8), ha='left', fontsize=8)
        ax2.annotate(f"Min: {time_min[i]:.2f}ms", (i, time_min[i]), textcoords="offset points", xytext=(0, -14), ha='center', fontsize=8, color=colors[i])

    ax1.set_ylim(0, max(rate_max) * 1.25)
    ax2.set_ylim(0, max(time_max) * 1.25)

    ax1.set_title('Relocation Rate (Min, Mean, Max & SD)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Relocation Rate (%)', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')

    ax2.set_title('Execution Time (Min, Mean, Max & SD)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Time (ms)', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')


if __name__ == "__main__":
    K = 10000

    # 1. กำหนดโฟลเดอร์สำหรับเก็บรูปภาพอัตโนมัติ
    output_dir = "output_plots"
    os.makedirs(output_dir, exist_ok=True)

    salt_configs = [
        {"b_salt": "0", "c_salt": "0"},
        {"b_salt": "1", "c_salt": "1"},
        {"b_salt": "2", "c_salt": "2"},
    ]

    order_keys = [
        ("mod_n", "add_building"),
        ("mod_n", "remove_building"),
        ("consistent", "add_building"),
        ("consistent", "remove_building"),
    ]

    for salt_idx, config in enumerate(salt_configs, 1):
        b_salt = config["b_salt"]
        c_salt = config["c_salt"]

        results_map = {}
        labels = []
        stats_list = []

        # รันการทดสอบ 4 แบบต่อ 1 ชุด Salt
        for hash_type, function in order_keys:
            b_counts, rel_rates, exec_times, stats = loop_test_2_to_20(
                hash_type=hash_type,
                function=function,
                K=K,
                building_salt=b_salt,
                customer_salt=c_salt
            )

            key = (hash_type, function)
            results_map[key] = (b_counts, rel_rates, exec_times, stats)

            labels.append(f"{function}\n({hash_type})")
            stats_list.append(stats)

        # -------------------------------------------------------------
        # 1. พล็อตและบันทึก Window ที่ 1: Grid 2x4
        # -------------------------------------------------------------
        plot_all_experiments_grid(results_map, K, b_salt, c_salt)
        grid_filepath = os.path.join(output_dir, f"grid_metrics_bsalt_{b_salt}_csalt_{c_salt}.png")
        plt.savefig(grid_filepath, dpi=300, bbox_inches='tight')
        print(f"[Auto-Save] บันทึกไฟล์เรียบร้อย: {grid_filepath}")

        # -------------------------------------------------------------
        # 2. พล็อตและบันทึก Window ที่ 2: Summary Stats
        # -------------------------------------------------------------
        plot_summary_minmax_std(labels, stats_list, K, b_salt, c_salt)
        stats_filepath = os.path.join(output_dir, f"summary_stats_bsalt_{b_salt}_csalt_{c_salt}.png")
        plt.savefig(stats_filepath, dpi=300, bbox_inches='tight')
        print(f"[Auto-Save] บันทึกไฟล์เรียบร้อย: {stats_filepath}")

        # สั่งแสดงผลกราฟขึ้นหน้าจอ
        plt.show()