from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

yourname = input("enter name\n")

print(f"{yourname}, the current time is {current_time}.")