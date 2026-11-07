import os
import sys
import csv
import tracemalloc
import statistics
import matplotlib.pyplot as plt

# Ensure root directory is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from hotel_sys import HotelSystem

def run_experiment_c():
    N = 10
    K = 10000
    C_MAX = 10
    guests_per_channel = K // C_MAX
    v_values = [1, 8, 32]
    salts = ["0", "1", "2"]

    print("Starting Experiment C...\n")

    # CSV data collector
    csv_rows = []

    # Arrays to store data for graphing (Consistent Hashing)
    avg_cv_list = []
    min_cv_list = []
    max_cv_list = []
    
    avg_mem_list = []
    min_mem_list = []
    max_mem_list = []

    # 1. Consistent Hashing (V = 1, 8, 32)
    for v in v_values:
        print(f"=== Testing Virtual Nodes (V) = {v} ===")
        cv_rounds = []
        mem_rounds = []

        for round_num, salt in enumerate(salts, 1):
            # 1. Measure Memory
            tracemalloc.start()
            hotel_mem = HotelSystem(v, salt, salt, hash_type="consistent")
            
            for i in range(1, N + 1):
                hotel_mem.add_building(i)
                
            for c in range(1, C_MAX + 1):
                for s in range(1, guests_per_channel + 1):
                    hotel_mem.add_customer(c, s)
                    
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            current_mib = current / (1024 * 1024)
            peak_mib = peak / (1024 * 1024)
            mem_rounds.append(current_mib)

            # 2. Measure Balance (CV) for the graph
            hotel = HotelSystem(v, salt, salt, hash_type="consistent")
            for i in range(1, N + 1):
                hotel.add_building(i)
            for c in range(1, C_MAX + 1):
                for s in range(1, guests_per_channel + 1):
                    hotel.add_customer(c, s)

            building_counts = {i: 0 for i in range(1, N + 1)}
            for customer in hotel.get_customers():
                if customer.node_id in building_counts:
                    building_counts[customer.node_id] += 1
            
            counts = list(building_counts.values())
            mean = statistics.mean(counts)
            std_dev = statistics.stdev(counts) if len(counts) > 1 else 0
            cv = std_dev / mean if mean > 0 else 0
            cv_rounds.append(cv)

            print(f"Round {round_num} (salt='{salt}'): CV = {cv:.4f}, Mem = {current_mib:.4f} MiB (Peak = {peak_mib:.4f} MiB)")

            # Record row for CSV
            csv_rows.append({
                "round": round_num,
                "salt": salt,
                "method": "consistent",
                "n": N,
                "k": K,
                "v": v,
                "c_max": C_MAX,
                "cv": round(cv, 6),
                "mean_guests": round(mean, 2),
                "std_dev": round(std_dev, 4),
                "min_guests": min(counts),
                "max_guests": max(counts),
                "memory_current_mib": round(current_mib, 4),
                "memory_peak_mib": round(peak_mib, 4),
            })

        avg_cv_list.append(statistics.mean(cv_rounds))
        min_cv_list.append(min(cv_rounds))
        max_cv_list.append(max(cv_rounds))

        avg_mem_list.append(statistics.mean(mem_rounds))
        min_mem_list.append(min(mem_rounds))
        max_mem_list.append(max(mem_rounds))
        print()

    # 2. Hash Mod N Baseline
    print("=== Testing Hash Mod N ===")
    cv_rounds_mod_n = []
    mem_rounds_mod_n = []

    for round_num, salt in enumerate(salts, 1):
        # 1. Measure Memory
        tracemalloc.start()
        hotel_mem = HotelSystem(0, salt, salt, hash_type="mod_n")
        
        for i in range(1, N + 1):
            hotel_mem.add_building(i)
            
        for c in range(1, C_MAX + 1):
            for s in range(1, guests_per_channel + 1):
                hotel_mem.add_customer(c, s)
                
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        current_mib = current / (1024 * 1024)
        peak_mib = peak / (1024 * 1024)
        mem_rounds_mod_n.append(current_mib)

        # 2. Measure Balance (CV) for the graph
        hotel = HotelSystem(0, salt, salt, hash_type="mod_n")
        for i in range(1, N + 1):
            hotel.add_building(i)
        for c in range(1, C_MAX + 1):
            for s in range(1, guests_per_channel + 1):
                hotel.add_customer(c, s)

        building_counts = {i: 0 for i in range(1, N + 1)}
        for customer in hotel.get_customers():
            if customer.node_id in building_counts:
                building_counts[customer.node_id] += 1
        
        counts = list(building_counts.values())
        mean = statistics.mean(counts)
        std_dev = statistics.stdev(counts) if len(counts) > 1 else 0
        cv = std_dev / mean if mean > 0 else 0
        cv_rounds_mod_n.append(cv)

        print(f"Round {round_num} (salt='{salt}'): CV = {cv:.4f}, Mem = {current_mib:.4f} MiB (Peak = {peak_mib:.4f} MiB)")

        # Record row for CSV
        csv_rows.append({
            "round": round_num,
            "salt": salt,
            "method": "mod_n",
            "n": N,
            "k": K,
            "v": "N/A",
            "c_max": C_MAX,
            "cv": round(cv, 6),
            "mean_guests": round(mean, 2),
            "std_dev": round(std_dev, 4),
            "min_guests": min(counts),
            "max_guests": max(counts),
            "memory_current_mib": round(current_mib, 4),
            "memory_peak_mib": round(peak_mib, 4),
        })

    avg_cv_mod_n = statistics.mean(cv_rounds_mod_n)
    avg_mem_mod_n = statistics.mean(mem_rounds_mod_n)
    print(f"\nHash Mod N Summary: Avg CV = {avg_cv_mod_n:.4f}, Avg Mem = {avg_mem_mod_n:.4f} MiB\n")

    # 3. Export to CSV (Section 10.1)
    csv_dir = os.path.join(PROJECT_ROOT, "CSV")
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, "test_C_results.csv")
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "round", "salt", "method", "n", "k", "v", "c_max",
            "cv", "mean_guests", "std_dev", "min_guests", "max_guests",
            "memory_current_mib", "memory_peak_mib"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"[CSV Export] Results saved to: {csv_path}\n")

    # 4. Generate the Graph (Friend's Preferred Layout)
    print("Generating graphs...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Graph 1: Effect of V on CV
    cv_err_lower = [avg_cv_list[i] - min_cv_list[i] for i in range(len(v_values))]
    cv_err_upper = [max_cv_list[i] - avg_cv_list[i] for i in range(len(v_values))]
    
    ax1.errorbar(v_values, avg_cv_list, yerr=[cv_err_lower, cv_err_upper], fmt='-o', color='blue', capsize=5, label='Consistent Hashing')
    ax1.axhline(avg_cv_mod_n, color='green', linestyle='--', label=f'Hash Mod N ({avg_cv_mod_n:.4f})')
    ax1.set_title(f'Effect of Virtual Nodes (V) on Balance (CV)\nParameters: N={N}, K={K}')
    ax1.set_xlabel('Number of Virtual Nodes (V)')
    ax1.set_ylabel('Coefficient of Variation (CV)')
    ax1.set_xticks(v_values)
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Graph 2: Effect of V on Memory
    mem_err_lower = [avg_mem_list[i] - min_mem_list[i] for i in range(len(v_values))]
    mem_err_upper = [max_mem_list[i] - avg_mem_list[i] for i in range(len(v_values))]
    
    ax2.errorbar(v_values, avg_mem_list, yerr=[mem_err_lower, mem_err_upper], fmt='-o', color='red', capsize=5, label='Consistent Hashing')
    ax2.axhline(avg_mem_mod_n, color='green', linestyle='--', label=f'Hash Mod N ({avg_mem_mod_n:.4f} MiB)')
    ax2.set_title(f'Effect of Virtual Nodes (V) on Memory\nParameters: N={N}, K={K}')
    ax2.set_xlabel('Number of Virtual Nodes (V)')
    ax2.set_ylabel('Memory Usage (MiB)')
    ax2.set_xticks(v_values)
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_experiment_c()
