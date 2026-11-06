import time
import logging

# Fares in euros per second (Madrid EMT zone, June 2025)
RATE_STOPPED = 0.02
RATE_MOVING = 0.05

# Every event is written to taximeter.log with date and time
logging.basicConfig(
    filename="taximeter.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


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
    logging.info("Trip started")
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
        logging.warning("Tried to set state to %s but it was already %s", new_state, new_state)
        return
    update_fare(trip)  # charge the previous stretch at its own rate
    trip["state"] = new_state
    print(f"State changed to: {new_state}")
    logging.info("State changed to %s", new_state)


def finish_trip(trip):
    update_fare(trip)
    print(f"\nTrip finished. Total to pay: {trip['total']:.2f} EUR")
    logging.info("Trip finished. Total: %.2f EUR", trip["total"])


def main():
    trip = None  # None means no active trip
    logging.info("Program started")
    show_instructions()

    while True:
        command = input("\n> ").strip().lower()

        if command == "start":
            if trip is not None:
                print("A trip is already active!")
                logging.warning("Start requested while a trip was active")
            else:
                trip = start_trip()

        elif command in ("stop", "move"):
            if trip is None:
                print("No active trip. Type 'start' first.")
                logging.warning("'%s' requested with no active trip", command)
            else:
                change_state(trip, "stopped" if command == "stop" else "moving")

        elif command == "finish":
            if trip is None:
                print("No active trip to finish.")
                logging.warning("Finish requested with no active trip")
            else:
                finish_trip(trip)
                trip = None  # ready for the next trip without closing the program

        elif command == "exit":
            if trip is not None:
                print("Finish the active trip before exiting.")
                logging.warning("Exit requested while a trip was active")
            else:
                print("Goodbye!")
                logging.info("Program closed")
                break

        else:
            print("Invalid command.")
            logging.warning("Invalid command: %s", command)
            show_instructions()


if __name__ == "__main__":
    main()