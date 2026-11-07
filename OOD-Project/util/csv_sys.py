import csv
from pathlib import Path
import json


def create_customer_csv(file_name: str, customers: list):
    with open(f"CSV/{file_name}", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["no", "channel", "sequence", "node_id", "room_no"])
        for i, customer in enumerate(customers):
            channel, sequence = customer.id[0], customer.id[1]
            writer.writerow([i+1, channel, sequence, customer.node_id, customer.room_no])
    

def create_moved_customer_csv(file_name: str, moved_customers:list):
      """
      
      moved_customers --> [MovedCusotmer()]

      """
      with open(f"CSV/{file_name}", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["no", "channel", "sequence","room_no","old_node_id","new_node_id" ])
        for i, customer in enumerate(moved_customers):
            old_node_id = customer.old_node_id
            new_node_id = customer.new_node_id
            room_no = customer.room_no
            channel, sequence = customer.id[0], customer.id[1]
            writer.writerow([i+1, channel, sequence, room_no,old_node_id,new_node_id])


def create_node_csv(file_name: str, buildings_with_rooms:list):
      """
      
      moved_customers --> [MovedCusotmer()]

      """
      with open(f"CSV/{file_name}", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["no", "node_id", "room_no"])
        for i, building_with_room in enumerate(buildings_with_rooms):
            node_id = building_with_room.building_id
            room_no = building_with_room.room_no
            writer.writerow([i+1,node_id,room_no])


def count_line_csv(file_name: str) -> int:
    with open(f"CSV/{file_name}","r",newline="",encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader,None)
        return len(list(reader))

def save_results(x_values, y_values, metadata, x_name, y_name, folder_name, file_name="output.csv"):
    if len(x_values) != len(y_values):
        raise ValueError("x_values and y_values must be the same length")

    save_dir = Path("CSV") / folder_name
    save_dir.mkdir(parents=True, exist_ok=True)

    with open(save_dir / file_name, "w", newline="", encoding="utf-8") as f:
        for key, val in metadata.items():
            f.write(f"# {key}: {json.dumps(val)}\n")
        writer = csv.writer(f)
        writer.writerow([x_name, y_name])
        writer.writerows(zip(x_values, y_values))