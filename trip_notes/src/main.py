import sys
import os

# Fix the import path so it works when run from the trip_notes/ root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Destination, TripCollection
from src.storage import load_trips, save_trips

def main():
    # On startup: load existing trips
    collection = load_trips()

    while True:
        print("\n=== Trip Notes ===")
        print("[1] Add destination")
        print("[2] View all destinations")
        print("[3] Search by country")
        print("[4] Add note to a destination")
        print("[5] Quit")

        choice = input("Select an option: ").strip()

        if choice == '1':
            try:
                name = input("Enter name: ")
                country = input("Enter country: ")
                budget = float(input("Enter budget: "))
                
                new_dest = Destination(name=name, country=country, budget=budget)
                collection.add(new_dest)
                save_trips(collection)
                print("Destination added!")
            except ValueError:
                print("Invalid budget. Please enter a number.")

        elif choice == '2':
            if len(collection) == 0:
                print("No trips saved yet.")
            else:
                print("\n--- All Destinations ---")
                for i, trip in enumerate(collection.get_all(), 1):
                    notes_str = ", ".join(trip.notes) if trip.notes else "None"
                    print(f"{i}. {trip.name} ({trip.country}) - Budget: ${trip.budget:.2f}")
                    print(f"   Notes: {notes_str}")
                    print(f"   Added on: {trip.date_added}")

        elif choice == '3':
            country_search = input("Enter country: ")
            results = collection.search_by_country(country_search)
            if not results:
                print(f"No destinations found for '{country_search}'.")
            else:
                for trip in results:
                    notes_str = ", ".join(trip.notes) if trip.notes else "None"
                    print(f"- {trip.name} - Budget: ${trip.budget:.2f}")
                    print(f"  Notes: {notes_str}")

        elif choice == '4':
            if len(collection) == 0:
                print("No trips to add notes to.")
                continue
            
            # Print numbered list first
            for i, trip in enumerate(collection.get_all(), 1):
                print(f"{i}. {trip.name}")
            
            try:
                index_choice = int(input("Enter number to select: "))
                if 1 <= index_choice <= len(collection):
                    trip = collection.get_by_index(index_choice - 1)
                    note = input("Enter note: ")
                    trip.add_note(note)
                    save_trips(collection)
                    print("Note added!")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    main()
