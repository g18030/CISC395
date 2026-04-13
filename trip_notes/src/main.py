import sys
import os

# Fix the import path so it works when run from the trip_notes/ root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Destination, TripCollection
from src.storage import load_trips, save_trips
from src.ai_assistant import ask, TRAVEL_SYSTEM_PROMPT, generate_trip_briefing

def main():
    # On startup: load existing trips
    collection = load_trips()

    while True:
        print("\n=== Trip Notes ===")
        print()
        print("-- Data --")
        print("[1] Add destination")
        print("[2] List all destinations")
        print("[3] Mark as visited")
        print("[4] Show statistics")
        print()
        print("-- AI --")
        print("[6] Ask AI a travel question")
        print("[7] Trip Briefing")
        print()
        print("[Q] Quit")

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
                    visited_status = " (Visited)" if trip.visited else " (Wishlist)"
                    print(f"{i}. {trip.name} ({trip.country}){visited_status} - Budget: ${trip.budget:.2f}")
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

        elif choice.lower() == 'q':
            break

        elif choice == '6':
            question = input("Your question: ")
            response = ask(question, system_prompt=TRAVEL_SYSTEM_PROMPT)

            if response is None:
                print("Could not get a response from the AI right now.")
                continue

            print(response)

            save_answer = input("Save this as a note on a trip? (y/n): ").strip().lower()
            if save_answer == "y":
                trips = collection.get_all()
                if not trips:
                    print("No trips saved yet.")
                    continue

                for i, trip in enumerate(trips, 1):
                    print(f"{i}. {trip.name}")

                try:
                    trip_number = int(input("Trip number: "))
                    trip = collection.get_by_index(trip_number - 1)
                    trip.add_note(response)
                    save_trips(collection)
                    print(f"Saved as a note on {trip.name}.")
                except (ValueError, IndexError):
                    print("Invalid trip number.")

        elif choice == '7':
            destinations = collection.get_all()
            if not destinations:
                print("No trips saved yet.")
                continue

            for i, dest in enumerate(destinations, 1):
                print(f"  [{i}] {dest.name}, {dest.country}")

            try:
                index_choice = int(input("Select trip number: "))
                index = index_choice - 1
                if index < 0 or index >= len(destinations):
                    print("Invalid selection.")
                    continue

                dest = destinations[index]
                print(f"Generating briefing for {dest.name}...")
                result = generate_trip_briefing(dest.name, dest.country, dest.notes)

                if result is None:
                    print("Briefing failed. Check your API connection.")
                    continue

                print(f"\n--- {dest.name} Briefing ---")
                print(f"Overview:\n{result['overview']}")
                print(f"\nPacking List:\n{result['packing_list']}")
            except ValueError:
                print("Invalid selection.")
        
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    main()
