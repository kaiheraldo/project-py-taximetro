import time

# Fares in euros per second (Madrid EMT zone, June 2025)
RATE_STOPPED = 0.02
RATE_MOVING = 0.05


def show_instructions():
    print("\n=== TAXI METER ===")
    print("Commands:")
    print("  start  -> begin a new trip")
    print("  stop   -> taxi is stopped (low rate: 0.02 EUR/s)")
    print("  move   -> taxi is moving  (high rate: 0.05 EUR/s)")
    print("  finish -> end the trip and show the total")
    print("  exit   -> close the program")


def start_trip():
    print("Trip started! The taxi is stopped.")
    return {"state": "stopped", "last_change": time.time(), "total": 0.0}


def update_fare(trip):
    """Add the cost of the time spent in the current state since the last change."""
    now = time.time()
    elapsed = now - trip["last_change"]
    rate = RATE_MOVING if trip["state"] == "moving" else RATE_STOPPED
    trip["total"] += elapsed * rate
    trip["last_change"] = now


def change_state(trip, new_state):
    if trip["state"] == new_state:
        print(f"The taxi is already {new_state}.")
        return
    update_fare(trip)  # charge the previous stretch at its own rate
    trip["state"] = new_state
    print(f"State changed to: {new_state}")


def finish_trip(trip):
    update_fare(trip)
    print(f"\nTrip finished. Total to pay: {trip['total']:.2f} EUR")


def main():
    trip = None  # None means no active trip
    show_instructions()

    while True:
        command = input("\n> ").strip().lower()

        if command == "start":
            if trip is not None:
                print("A trip is already active!")
            else:
                trip = start_trip()

        elif command in ("stop", "move"):
            if trip is None:
                print("No active trip. Type 'start' first.")
            else:
                change_state(trip, "stopped" if command == "stop" else "moving")

        elif command == "finish":
            if trip is None:
                print("No active trip to finish.")
            else:
                finish_trip(trip)
                trip = None  # ready for the next trip without closing the program

        elif command == "exit":
            if trip is not None:
                print("Finish the active trip before exiting.")
            else:
                print("Goodbye!")
                break

        else:
            print("Invalid command.")
            show_instructions()


if __name__ == "__main__":
    main()