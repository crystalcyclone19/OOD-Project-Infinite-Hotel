from hotel_sys import HotelSystem
from util.csv_sys import (create_customer_csv,
                          create_moved_customer_csv,
                          create_node_csv,
                          count_line_csv,
                         )

V = 1  
N = 5
K_PER_C = 5
C_MAX = 3

building_salt = "b"
customer_salt = "c"

# Init System
hotel = HotelSystem(V,building_salt,customer_salt)

# Add Buildings 
for i in range(1,N+1):
  hotel.add_building(i)

# Add Customers 
for i in range(1,C_MAX+1):
   for j in range(1,K_PER_C+1):
      hotel.add_customer(i,j)

# Add Group Customer 
hotel.add_group_customer(1,16,5)


# Export Customers And Buildinds_with_rooms 
create_customer_csv("customers.csv",hotel.get_customers())
create_node_csv("buildings_with_rooms.csv",hotel.get_buildings_with_rooms())


# Remove Building And Export Moved Customers  
create_moved_customer_csv("moved_customers_from_remove_1.csv",hotel.remove_building(1))
create_moved_customer_csv("moved_customers_from_remove_2.csv",hotel.remove_building(2))

# Add Building And Export Moved Customers  
create_moved_customer_csv("moved_customers_from_add_1.csv",hotel.add_building(1))


# Search Customer By Id 
print(f"Search by Id: {hotel.search_customer_by_id(1,1)}")

# Search Customer By Id 
print(f"Search by building_id and room: {hotel.search_customer_by_room(3,3)}")

# Count line
print(f"Total lines:{count_line_csv("moved_customers_from_add_1.csv")}")





