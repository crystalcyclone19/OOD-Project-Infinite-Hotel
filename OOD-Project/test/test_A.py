import sys 
from hotel_sys import HotelSystem,Customer
from util.csv_sys import (create_customer_csv,
                          create_moved_customer_csv,
                          create_node_csv,
                          count_line_csv,
                         )
from HashRing import HashHelper, HashRing
from AVLTree import AVLClassTree,AVLNormalTree

from util.graph import Graph
from util.timer import Timer
from util.memory_usage import MemoryUsage


import util.color as color
import util.math as m

import gc



# Constant
N = 10
V = 32
C_MAX = 10
customer_salts = ["c1","c2","c3"]
building_salts = ["b1","b2","b3"]
time_prefix = "us"
memory_prefix = "MiB"
iteration = 3
searching_number = 1000                

timer = Timer()
mem = MemoryUsage()

graph = Graph()
graph_err = Graph()



K = [1000,10000,100000]



def test_time():
  y_err_assign = [ [] for i in range(len(K))]
  y_err_search = [ [] for i in range(len(K))]
  y_err_ordering = [ [] for i in range(len(K))]

  for i in range(1,iteration+1):
    print(f"Round({i})")
    y_assign_guest = []
    y_search_guest = []
    y_ordering_guest = []
    x = []

    hotel = HotelSystem(V,building_salts[i-1],customer_salts[i-1])


    for k in K:

      #<==== Adding N(10) Buildings for testing ====>
      for j in range(1,N+1):
          hotel.add_building(j)

      print(f"Doing {k} samples... ",end="")
      #<==== Adding K Customers for testing ====>
      ids = [(((t - 1) % C_MAX) + 1, ((t - 1) // C_MAX) + 1) for t in range(1, k + 1)]

      timer.start() # Start < ======================================= Assign customer
      for c, s in ids:
          hotel.add_customer(c, s)
      y_assign_guest.append(timer.stop(time_prefix) / k) #< ================== Assign customer



      timer.start()# Start < ======================================= Search guest (Search 1000 person)
      n_search = min(searching_number, k)
      for t in range(n_search):
          c = ids[t][0]
          s = ids[t][1]
          hotel.search_customer_by_id(c,s)
      y_search_guest.append(timer.stop(time_prefix)/n_search)# Stop < ================== Search guest



      timer.start()# Start < ======================================= Ordering guest 
      hotel.get_buildings_with_rooms()
      y_ordering_guest.append(timer.stop(time_prefix))# Stop < ================== Ordering guest



      x.append(k)
      # Clear Data reader to the next step
      hotel.customer_tree = AVLClassTree()
      hotel.building_tree = AVLNormalTree()
      hotel.ring = HashRing(V, building_salts[i-1])

      # End 
      print(f"Done")
      #  < ================== 
      #  Keep the data
      #  < ================== 
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
    

    graph.set_title(f"Iteration({i})",f"Test A(round {i}): Time usage(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts[i-1]} \nCustomer salt={customer_salts[i-1]} ")
    graph.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_assign_guest,f"Time usage({time_prefix})",label="Assigning guest",color=color.GREEN)
    graph.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_search_guest,f"Time usage({time_prefix})",label="Searching guest",color=color.RED)
    graph.add_graph(f"Iteration({i})",x,"Number of persons(K)",y_ordering_guest,f"Time usage({time_prefix})",label="Ordering guest",color=color.BLUE)
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
  
    Ordering guest
    Variance:  {y_ordering_guest_var:.3f} {time_prefix}²
    Min:         {y_ordering_guest_min:.3f} {time_prefix}
    Max:        {y_ordering_guest_max:.3f} {time_prefix}
    Avg:         {y_ordering_guest_avg:.3f} {time_prefix}
                                        """)
    
    print()
  graph_err.set_title(f"assign_customer",f"Test A({iteration} rounds): Time(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("assign_customer",x,"Number of persons(K)",y_err_assign,f"Time usage({time_prefix})",
                                      label="Assign customer",color=color.GREEN
                                      )

  graph_err.set_title(f"search_customer",f"Test A({iteration} rounds): Time(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("search_customer",x,"Number of persons(K)",y_err_search,f"Time usage({time_prefix})",
                                      label="Search customer",color=color.RED
                                      )

  graph_err.set_title(f"ordering_customer",f"Test A({iteration} rounds): Time(us) VS Number of people(K) \nParameter: N={N}, V={V}, C(max)={C_MAX} \nSalt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("ordering_customer",x,"Number of persons(K)",y_err_ordering,f"Time usage({time_prefix})",
                                      label="Ordering customer",color=color.BLUE
                                      )
  graph.save("test_A_assign_search_ordering")  
  graph_err.save("test_A_assign_search_ordering_variance")
  graph.clear()
  graph_err.clear()

def test_memory():
  y_err_current = [[] for _ in K]      # one list of round values per K
  y_err_peak = [[] for _ in K]

  for i in range(1, iteration + 1):
    print(f"Round({i})")
    y_current = []
    y_peak = []
    for idx, k in enumerate(K):
      print(f"Doing {k} samples... ", end="")

      ids = [(((t - 1) % C_MAX) + 1, ((t - 1) // C_MAX) + 1) for t in range(1, k + 1)]

      hotel = HotelSystem(V, building_salts[i-1], customer_salts[i-1])
      for j in range(1, N + 1):
          hotel.add_building(j)

      gc.collect()
      mem.start()                                   # baseline before anything is built
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
    graph.set_title(f"Iteration({i})",f"Test A(round {i}): Memory usage({memory_prefix}) VS Number of people(K)\nParameter: N={N},V={V},C(max):{C_MAX} \nSalt: Building salt={building_salts[i-1]},Customer salt={customer_salts[i-1]} ")
    graph.add_graph(f"Iteration({i})",K,"Number of persons(K)",y_current,f"Memory usage({memory_prefix})",label="current",color=color.GREEN)
    graph.add_graph(f"Iteration({i})",K,"Number of persons(K)",y_peak,f"Memory usage({memory_prefix})"   ,label="peak",color=color.RED)
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


  graph_err.set_title("memory_current", f"Test A({iteration} rounds): Memory usage({memory_prefix}) VS Number of people(K)\nParameter: N={N}, V={V}, C(max):{C_MAX} \n Salt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("memory_current", K, "Number of persons (K)",
                                      y_err_current, f"Memory usage ({memory_prefix})",
                                      label="current", color=color.GREEN)

  graph_err.set_title("memory_peak", f"Test A({iteration} rounds): Memory usage({memory_prefix}) VS Number of people(K)\nParameter: N={N}, V={V} C(max):{C_MAX} \n Salt: Building salt={building_salts},Customer salt={customer_salts}\n(median of {iteration} rounds, bars = min..max)")
  graph_err.add_median_low_high_graph("memory_peak", K, "Number of persons (K)",
                                      y_err_peak, f"Memory usage ({memory_prefix})",
                                      label="peak", color=color.RED)

  graph_err.save("Test_A_memory_variance")
  graph.save("Test_A_memory")
  graph.clear()
  graph_err.clear()

if __name__ == "__main__":
    print("< === TEST TIME USAGE === >")
    test_time()
    print()
    print("< === TEST MEMORY USAGE === >")
    test_memory()



