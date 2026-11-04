def start_trip():
    print("Taxi trip started!")
    return True


trip_active = False

while True:
    print("\n--- TAXI METER ---")
    print("1. Start trip")
    print("2. Exit")

    command = input("Choose an option: ")

    if command == "1":
        if trip_active:
            print("A trip is already active!")
        else:
            trip_active = start_trip()

    elif command == "2":
        print("Goodbye!")
        break

    else:
        print("Invalid option!")

    print("Trip active:", trip_active)