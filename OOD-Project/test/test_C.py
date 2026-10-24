import tracemalloc
import statistics
import matplotlib.pyplot as plt
from hotel_sys import HotelSystem

def run_experiment_c():
    N = 10
    K = 10000
    channels = 10
    guests_per_channel = K // channels
    v_values = [1, 8, 32]
    salts = ["0", "1", "2"]

    print("Starting Experiment C...\n")

    # Arrays to store data for graphing
    avg_cv_list = []
    min_cv_list = []
    max_cv_list = []
    
    avg_mem_list = []
    min_mem_list = []
    max_mem_list = []

    for v in v_values:
        print(f"=== Testing Virtual Nodes (V) = {v} ===")
        
        cv_rounds = []
        mem_rounds = []

        for salt in salts:
            # 1. Measure Memory
            tracemalloc.start()
            hotel_mem = HotelSystem(v, salt, salt)
            
            for i in range(1, N + 1):
                hotel_mem.add_building(i)
                
            for c in range(1, channels + 1):
                for s in range(1, guests_per_channel + 1):
                    hotel_mem.add_customer(c, s)
                    
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            current_mib = current / (1024 * 1024)
            mem_rounds.append(current_mib)

            # 2. Measure Balance (CV)
            hotel = HotelSystem(v, salt, salt)
            
            for i in range(1, N + 1):
                hotel.add_building(i)
            
            for c in range(1, channels + 1):
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

            print(f"Round '{salt}': CV = {cv:.4f}, Mem = {current_mib:.4f} MiB")

        # Calculate averages and min/max for the graph
        avg_cv_list.append(statistics.mean(cv_rounds))
        min_cv_list.append(min(cv_rounds))
        max_cv_list.append(max(cv_rounds))

        avg_mem_list.append(statistics.mean(mem_rounds))
        min_mem_list.append(min(mem_rounds))
        max_mem_list.append(max(mem_rounds))
        print()

    # 3. Generate the Graph
    print("Generating graphs...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Graph 1: Effect of V on CV
    # Define error bars (distance from mean to min and max)
    cv_err_lower = [avg_cv_list[i] - min_cv_list[i] for i in range(len(v_values))]
    cv_err_upper = [max_cv_list[i] - avg_cv_list[i] for i in range(len(v_values))]
    
    ax1.errorbar(v_values, avg_cv_list, yerr=[cv_err_lower, cv_err_upper], fmt='-o', color='blue', capsize=5)
    ax1.set_title(f'Effect of Virtual Nodes (V) on Balance (CV)\nParameters: N={N}, K={K}')
    ax1.set_xlabel('Number of Virtual Nodes (V)')
    ax1.set_ylabel('Coefficient of Variation (CV)')
    ax1.set_xticks(v_values)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Graph 2: Effect of V on Memory
    mem_err_lower = [avg_mem_list[i] - min_mem_list[i] for i in range(len(v_values))]
    mem_err_upper = [max_mem_list[i] - avg_mem_list[i] for i in range(len(v_values))]
    
    ax2.errorbar(v_values, avg_mem_list, yerr=[mem_err_lower, mem_err_upper], fmt='-o', color='red', capsize=5)
    ax2.set_title(f'Effect of Virtual Nodes (V) on Memory\nParameters: N={N}, K={K}')
    ax2.set_xlabel('Number of Virtual Nodes (V)')
    ax2.set_ylabel('Memory Usage (MiB)')
    ax2.set_xticks(v_values)
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_experiment_c()