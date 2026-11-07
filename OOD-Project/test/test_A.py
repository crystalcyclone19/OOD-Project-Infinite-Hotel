import sys 
from hotel_sys import HotelSystem,Customer
from util.csv_sys import (create_customer_csv,
                          create_moved_customer_csv,
                          create_node_csv,
                          count_line_csv,
                          save_results,
                        )

from HashRing import HashHelper, HashRing, HashModN   # FIX 1: import HashModN
from AVLTree import AVLClassTree,AVLNormalTree

from util.graph import Graph
from util.timer import Timer
from util.memory_usage import MemoryUsage


import util.color as color
import util.math as m

import gc
import statistics



# Constant
N = 10
V = 32
C_MAX = 10
customer_salts = ["0","1","2"]
building_salts = ["0","1","2"]
time_prefix = "us"
memory_prefix = "MiB"
iteration = 3
searching_number = 1000                

timer = Timer()
mem = MemoryUsage()

graph = Graph()
graph_2 = Graph()
graph_3 = Graph()
graph_err = Graph()




# K = [i for i in range(10,2000)]
K = [100,1000,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000,110000,120000,130000,140000,150000]
# K = [1000,10000,100000]



def test_time(hash_type="consistent"):
  y_err_assign = [ [] for i in range(len(K))]
  y_err_search = [ [] for i in range(len(K))]
  y_err_ordering = [ [] for i in range(len(K))]
  y_calculate_building_guest = []

  hash_t = "consistant_hashing" if hash_type=="consistent" else "hash_mod_n" 
  for i in range(1,iteration+1):
    print(f"Round({i}) Medthod({hash_t})")
    y_assign_guest = []
    y_search_guest = []
    y_ordering_guest = []
    x = []

    hotel = HotelSystem(V,building_salts[i-1],customer_salts[i-1],hash_type)

    for k in K:

      #<==== Adding N(10) Buildings for testing ====>
      for j in range(1,N+1):
          hotel.add_building(j)

      print(f"Doing {k} samples... ",end="")
      #<==== Adding K Customers for testing ====>
      ids = [(((t - 1) % C_MAX) + 1, ((t - 1) // C_MAX) + 1) for t in range(1, k + 1)]

      gc.collect()
      gc.disable()
      timer.start() # Start < ======================================= Assign customer
      for c, s in ids:
          hotel.add_customer(c, s)
      y_assign_guest.append(timer.stop(time_prefix) / k) #< ================== Assign customer
      gc.enable()


      gc.collect()
      gc.disable()
      timer.start()# Start < ======================================= Search guest (Search 1000 person)
      n_search = min(searching_number, k)
      for t in range(n_search):
          c = ids[t][0]
          s = ids[t][1]
          hotel.search_customer_by_id(c,s)
      y_search_guest.append(timer.stop(time_prefix)/n_search)# Stop < ================== Search guest
      gc.enable()


      gc.collect()
      gc.disable()
      timer.start()# Start < ======================================= Ordering guest 
      hotel.get_buildings_with_rooms()
      y_ordering_guest.append(timer.stop(time_prefix))# Stop < ================== Ordering guest
      gc.enable()


      x.append(k)
      # Clear Data reader to the next step
      hotel.customer_tree = AVLClassTree()
      hotel.building_tree = AVLNormalTree()
      # FIX 2: reset with the correct ring type (was always HashRing, even for mod N)
      hotel.ring = HashRing(V, building_salts[i-1]) if hash_type == "consistent" else HashModN()

      # End 
      print(f"Done")
      #  < ================== 
      #  Keep the data
      #  < ================== 
  
    bench = HotelSystem(V, building_salts[i-1], customer_salts[i-1], hash_type)
    for j in range(1, N + 1):
        bench.add_building(j)

    ids_1000 = [(((t - 1) % C_MAX) + 1, ((t - 1) // C_MAX) + 1) for t in range(1, 1000 + 1)]
    hashes = [HashHelper.get_guest_hash(c, s, customer_salts[i-1]) for c, s in ids_1000]
    gc.collect()
    gc.disable()
    timer.start() # Start < ======================================= Calculate building
    for ha in hashes:
        bench.ring.get_node_id(ha)
    re = timer.stop(time_prefix) / 1000
    y_calculate_building_guest.append(re) #< ================== Calculate building
    gc.enable()

    for u in range(len(K)):
      y_err_assign[u].append(y_assign_guest[u])
      y_err_search[u].append(y_search_guest[u])
      y_err_ordering[u].append(y_ordering_guest[u])



    #  < ================== 
    # Calculate: variance
    #  < ==================
    y_assign_guest_var = m.variance(y_assign_guest)
    y_assign_guest_min = m.min(y_assign_guest)
    y_assign_guest_max = m.max(y_assign_guest)
    y_assign_guest_avg = m.avg(y_assign_guest)

    y_search_guest_var = m.variance(y_search_guest)
    y_search_guest_min = m.min(y_search_guest)
    y_search_guest_max = m.max(y_search_guest)
    y_search_guest_avg = m.avg(y_search_guest)

    y_ordering_guest_var = m.variance(y_ordering_guest)
    y_ordering_guest_min = m.min(y_ordering_guest)
    y_ordering_guest_max = m.max(y_ordering_guest)
    y_ordering_guest_avg = m.avg(y_ordering_guest)


    # Show all
    graph_3.set_title(f"Iteration({i})",f"Test A(round {i}, {hash_t}): Time usage(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts[i-1]} \nCustomer salt={customer_salts[i-1]} ")
    graph_3.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_assign_guest,f"Time usage({time_prefix})",label="Assigning guest",color=color.GREEN)
    graph_3.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_search_guest,f"Time usage({time_prefix})",label="Searching guest",color=color.RED)
    graph_3.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_ordering_guest,f"Time usage({time_prefix})",label="Ordering guest",color=color.BLUE)
    graph_3.set_report(f"Iteration({i})",f"""
    Assign guest
    Variance:  {y_assign_guest_var:.3f} {time_prefix}²
    Min:         {y_assign_guest_min:.3f} {time_prefix}
    Max:        {y_assign_guest_max:.3f} {time_prefix}
    Avg:         {y_assign_guest_avg:.3f} {time_prefix}\n

    Search guest
    Variance:  {y_search_guest_var:.3f} {time_prefix}²
    Min:         {y_search_guest_min:.3f} {time_prefix}
    Max:        {y_search_guest_max:.3f} {time_prefix}
    Avg:         {y_search_guest_avg:.3f} {time_prefix}\n

    Ordering guest
    Variance:  {y_ordering_guest_var:.3f} {time_prefix}²
    Min:         {y_ordering_guest_min:.3f} {time_prefix}
    Max:        {y_ordering_guest_max:.3f} {time_prefix}
    Avg:         {y_ordering_guest_avg:.3f} {time_prefix}
                                        """)
    # Show assign_guest and search_guest
    graph.set_title(f"Iteration({i})",f"Test A(round {i}, {hash_t}): Time usage(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts[i-1]} \nCustomer salt={customer_salts[i-1]} ")
    graph.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_assign_guest,f"Time usage({time_prefix})",label="Assigning guest",color=color.GREEN)
    save_results(x_values=K,y_values=y_assign_guest,
                metadata={"test":"A",
                          "name":"assign_guest",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "round": i,
                          "salt": building_salts[i-1],
                          "method": hash_t
                          },
                x_name="amount of customer(K)",y_name=f"time usage({time_prefix})",folder_name=f"test_A/{hash_t}/round_{i}",file_name=f"assign_guest.csv")

    graph.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_search_guest,f"Time usage({time_prefix})",label="Searching guest",color=color.RED)
    save_results(x_values=K,y_values=y_search_guest,
                metadata={"test":"A",
                          "name":"search_guest",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "round": i,
                          "salt": building_salts[i-1],
                          "method": hash_t
                          },
                x_name="amount of customer(K)",y_name=f"time usage({time_prefix})",folder_name=f"test_A/{hash_t}/round_{i}",file_name=f"search_guest.csv")
    graph.set_report(f"Iteration({i})",f"""  
    Assign guest
    Variance:  {y_assign_guest_var:.3f} {time_prefix}²
    Min:         {y_assign_guest_min:.3f} {time_prefix}
    Max:        {y_assign_guest_max:.3f} {time_prefix}
    Avg:         {y_assign_guest_avg:.3f} {time_prefix}\n

    Search guest
    Variance:  {y_search_guest_var:.3f} {time_prefix}²
    Min:         {y_search_guest_min:.3f} {time_prefix}
    Max:        {y_search_guest_max:.3f} {time_prefix}
    Avg:         {y_search_guest_avg:.3f} {time_prefix}\n
                                        """)
    
    # Show ordering_guest
    graph_2.set_title(f"Iteration({i})",f"Test A(round {i}, {hash_t}): Time usage(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts[i-1]} \nCustomer salt={customer_salts[i-1]} ")
    graph_2.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_ordering_guest,f"Time usage({time_prefix})",label="Ordering guest",color=color.BLUE)
    save_results(x_values=K,y_values=y_ordering_guest,
                metadata={"test":"A",
                          "name":"ordering_guest",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "round": i,
                          "salt": building_salts[i-1],
                          "method": hash_t
                          },
                x_name="amount of customer(K)",y_name=f"time usage({time_prefix})",folder_name=f"test_A/{hash_t}/round_{i}",file_name=f"ordering_guest.csv")
    graph_2.set_report(f"Iteration({i})",f""" 
    Ordering guest
    Variance:  {y_ordering_guest_var:.3f} {time_prefix}²
    Min:         {y_ordering_guest_min:.3f} {time_prefix}
    Max:        {y_ordering_guest_max:.3f} {time_prefix}
    Avg:         {y_ordering_guest_avg:.3f} {time_prefix}
                                        """)

    save_results(  x_values=[i],y_values=[re],
                  metadata={"test":"A",
                            "name":"calculate_building_1000_time",
                            "N":N,
                            "V":V,
                            "C(max)": C_MAX,
                            "round": i,
                            "salt": building_salts[i-1],
                            "method": hash_t
                            },
                  x_name="round",y_name=f"time usage({time_prefix})",folder_name=f"test_A/{hash_t}/round_{i}",file_name=f"calculate_building_1000_time.csv")
    print()


  graph_err.set_title(f"assign_customer",f"Test A({iteration} rounds, {hash_t}): Time(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("assign_customer",x,"Number of persons(K)",y_err_assign,f"Time usage({time_prefix})",
                                      label="Assign customer",color=color.GREEN
                                      )

  fit_assign, r2_assign = m.fit_log_k_log_m(K, m.get_medians(y_err_assign), N * V)   # O(log K + log M), M = N*V
  save_results(x_values=K,y_values=m.get_medians(y_err_assign),
              metadata={  "test":"A",
                          "name":"medians_assign_guest",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "number_of_round": iteration,
                          "salt": building_salts,
                          "method": hash_t,
                          "function": fit_assign,
                          "R2": r2_assign
                        },
              x_name="amount of customer(K)",y_name=f"time usage({time_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_assign_guest.csv")

  graph_err.set_title(f"search_customer",f"Test A({iteration} rounds, {hash_t}): Time(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("search_customer",x,"Number of persons(K)",y_err_search,f"Time usage({time_prefix})",
                                      label="Search customer",color=color.RED
                                      )
  fit_search, r2_search = m.fit_text(K, m.get_medians(y_err_search), "search")
  save_results(x_values=K,y_values=m.get_medians(y_err_search),
              metadata={  "test":"A",
                          "name":"medians_searching_guest",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "number_of_round": iteration,
                          "salt": building_salts,
                          "method": hash_t,
                          "function": fit_search,
                          "R2": r2_search
                        },
              x_name="amount of customer(K)",y_name=f"time usage({time_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_searching_guest.csv")

  graph_err.set_title(f"ordering_customer",f"Test A({iteration} rounds, {hash_t}): Time(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("ordering_customer",x,"Number of persons(K)",y_err_ordering,f"Time usage({time_prefix})",
                                      label="Ordering customer",color=color.BLUE
                                      )                         
  fit_ordering, r2_ordering = m.fit_text(K, m.get_medians(y_err_ordering), "ordering")
  save_results(x_values=K,y_values=m.get_medians(y_err_ordering),
              metadata={  "test":"A",
                          "name":"medians_ordering_guest",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "number_of_round": iteration,
                          "salt": building_salts,
                          "method": hash_t,
                          "function": fit_ordering,
                          "R2": r2_ordering
                        },
              x_name="amount of customer(K)",y_name=f"time usage({time_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_ordering_guest.csv")

  # Save calculate medians 
  save_results(x_values=[3],y_values=[statistics.median(y_calculate_building_guest)],
              metadata={  "test":"A",
                          "name":"medians_calculate_building_1000_time_3_rounds",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "salt": building_salts,
                          "method": hash_t
                        },
              x_name="total_round",y_name=f"medians({time_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_calculate_building_1000_time_3_rounds.csv")
  
  graph.save(f"test_A/{hash_t}",f"test_A_assign_search")  
  graph_2.save(f"test_A/{hash_t}",f"test_A_ordering")
  graph_3.save(f"test_A/{hash_t}",f"test_A_assign_search_ordering")
  graph_err.save(f"test_A/{hash_t}",f"test_A_assign_search_ordering_variance")
  graph.clear()
  graph_2.clear()
  graph_3.clear()
  graph_err.clear()

def test_memory(hash_type="consistent"):
  y_err_current = [[] for _ in K]      # one list of round values per K
  y_err_peak = [[] for _ in K]
  y_routing_current = []               # routing space (ring + buildings, no guests), one value per round
  y_routing_peak = []
  hash_t = "consistant_hashing" if hash_type == "consistent" else "hash_mod_n" 

  for i in range(1, iteration + 1):
    print(f"Round({i}) Medthod({hash_t})")
    y_current = []
    y_peak = []

    # OPTIONAL: routing space (ring / building list only, before any guests). Does not depend on K.
    gc.collect()
    mem.start()
    r = HotelSystem(V, building_salts[i-1], customer_salts[i-1], hash_type)
    for j in range(1, N + 1):
        r.add_building(j)
    routing_current, routing_peak = mem.stop()
    y_routing_current.append(routing_current)
    y_routing_peak.append(routing_peak)
    del r

    for idx, k in enumerate(K):
      print(f"Doing {k} samples... ", end="")
      ids = [(((t - 1) % C_MAX) + 1, ((t - 1) // C_MAX) + 1) for t in range(1, k + 1)]

      # FIX 3: start measuring BEFORE building the system so the ring is included (total data space)
      gc.collect()
      mem.start()                                   # baseline before anything is built
      hotel = HotelSystem(V, building_salts[i-1], customer_salts[i-1],hash_type)
      for j in range(1, N + 1):
          hotel.add_building(j)
      for c, s in ids:
          hotel.add_customer(c, s)
      current, peak = mem.stop()
      y_current.append(current)
      y_peak.append(peak)


      y_err_current[idx].append(current)
      y_err_peak[idx].append(peak)
      del hotel
      print("Done")



    #  < ================== 
    # Calculate: variance
    #  < ==================
    y_current_var = m.variance(y_current)
    y_current_min = m.min(y_current)
    y_current_max = m.max(y_current)
    y_current_avg = m.avg(y_current)

    y_peak_var = m.variance(y_peak)
    y_peak_min = m.min(y_peak)
    y_peak_max = m.max(y_peak)
    y_peak_avg = m.avg(y_peak)

    print()
    graph.set_title(f"Iteration({i})",f"Test A(round {i}, {hash_t}) : Memory usage({memory_prefix}) VS Number of people(K)\nParameter: N={N},V={V},C(max):{C_MAX} \nSalt: Building salt={building_salts[i-1]},Customer salt={customer_salts[i-1]} ")
    graph.add_graph(f"Iteration({i})",K,"Number of persons(K)",y_current,f"Memory usage({memory_prefix})",label="current",color=color.GREEN)
    save_results(x_values=K,y_values=y_current,
                metadata={"test":"A",
                          "name":"current_memory_usage",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "round": i,
                          "salt": building_salts[i-1],
                          "method": hash_t
                        },
                x_name="amount of customer(K)",y_name=f"memory usage({memory_prefix})",folder_name=f"test_A/{hash_t}/round_{i}",file_name=f"current_memory_usage.csv")


    graph.add_graph(f"Iteration({i})",K,"Number of persons(K)",y_peak,f"Memory usage({memory_prefix})"   ,label="peak",color=color.RED)
    save_results(x_values=K,y_values=y_peak,
                metadata={"test":"A",
                          "name":"peak_memory_usage",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "round": i,
                          "salt": building_salts[i-1],
                          "method": hash_t
                          },
                x_name="amount of customer(K)",y_name=f"memory usage({memory_prefix})",folder_name=f"test_A/{hash_t}/round_{i}",file_name=f"peak_memory_usage.csv")

    graph.set_report(f"Iteration({i})",f"""

    Current
    Variance:  {y_current_var:.3f} {memory_prefix}
    Min:         {y_current_min:.3f} {memory_prefix}
    Max:        {y_current_max:.3f} {memory_prefix}
    Avg:         {y_current_avg:.3f} {memory_prefix}\n

    Peak
    Variance:  {y_peak_var:.3f} {memory_prefix}
    Min:         {y_peak_min:.3f} {memory_prefix}
    Max:        {y_peak_max:.3f} {memory_prefix}
    Avg:         {y_peak_avg:.3f} {memory_prefix}\n

                                        """)


  graph_err.set_title("memory_current", f"Test A({iteration} rounds, {hash_t}): Memory usage({memory_prefix}) VS Number of people(K)\nParameter: N={N}, V={V}, C(max):{C_MAX} \n Salt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("memory_current", K, "Number of persons (K)",
                                      y_err_current, f"Memory usage ({memory_prefix})",
                                      label="current", color=color.GREEN)
  fit_current, r2_current = m.fit_text(K, m.get_medians(y_err_current), "memory")
  save_results(x_values=K,y_values=m.get_medians(y_err_current),
              metadata={  "test":"A",
                          "name":"medians_current_memory_usage",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "number_of_round": iteration,
                          "salt": building_salts,
                          "method": hash_t,
                          "function": fit_current,
                          "R2": r2_current
                        },
              x_name="amount of customer(K)",y_name=f"memory usage({memory_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_current_memory_usage.csv")

  graph_err.set_title("memory_peak", f"Test A({iteration} rounds, {hash_t}): Memory usage({memory_prefix}) VS Number of people(K)\nParameter: N={N}, V={V} C(max):{C_MAX} \n Salt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("memory_peak", K, "Number of persons (K)",
                                      y_err_peak, f"Memory usage ({memory_prefix})",
                                      label="peak", color=color.RED)
  fit_peak, r2_peak = m.fit_text(K, m.get_medians(y_err_peak), "memory")
  save_results(x_values=K,y_values=m.get_medians(y_err_peak),
              metadata={  "test":"A",
                          "name":"medians_peak_memory_usage",
                          "N":N,
                          "V":V,
                          "C(max)": C_MAX,
                          "number_of_round": iteration,
                          "salt": building_salts,
                          "method": hash_t,
                          "function": fit_peak,
                          "R2": r2_peak
                        },
              x_name="amount of customer(K)",y_name=f"memory usage({memory_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_peak_memory_usage.csv")

  # OPTIONAL: routing space (median of 3 rounds, with min/max in the printed line)
  save_results(x_values=[iteration],y_values=[statistics.median(y_routing_current)],
              metadata={  "test":"A",
                          "name":"medians_routing_space_current",
                          "N":N,
                          "V":V,
                          "number_of_round": iteration,
                          "min": min(y_routing_current),
                          "max": max(y_routing_current),
                          "salt": building_salts,
                          "method": hash_t
                        },
              x_name="total_round",y_name=f"memory usage({memory_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_routing_space_current.csv")
  save_results(x_values=[iteration],y_values=[statistics.median(y_routing_peak)],
              metadata={  "test":"A",
                          "name":"medians_routing_space_peak",
                          "N":N,
                          "V":V,
                          "number_of_round": iteration,
                          "min": min(y_routing_peak),
                          "max": max(y_routing_peak),
                          "salt": building_salts,
                          "method": hash_t
                        },
              x_name="total_round",y_name=f"memory usage({memory_prefix})",folder_name=f"test_A/{hash_t}",file_name=f"medians_routing_space_peak.csv")
  print(f"Routing space ({hash_t}): current median={statistics.median(y_routing_current):.4f} {memory_prefix}, peak median={statistics.median(y_routing_peak):.4f} {memory_prefix}")

  graph_err.save(f"test_A/{hash_t}",f"Test_A_memory_variance")
  graph.save(f"test_A/{hash_t}",f"Test_A_memory")
  graph.clear()
  graph_err.clear()




if __name__ == "__main__":
    print("< ======== CONSISTANT HASH === >")
    print("< === TEST TIME USAGE === >")
    test_time()
    print()
    print("< === TEST MEMORY USAGE === >")
    test_memory()
    print()

    print("< ======== HASH MOD N ======== >")
    print("< === TEST TIME USAGE === >")
    test_time("mod_n")
    print()
    print("< === TEST MEMORY USAGE === >")
    test_memory("mod_n")