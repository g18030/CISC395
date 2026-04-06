import os
import json
from dataclasses import asdict
from .models import Destination, TripCollection

def _get_data_path() -> str:
    """Helper function to determine the trips.json file path."""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(BASE_DIR, "data", "trips.json")

def load_trips() -> TripCollection:
    """Loads TripCollection from a JSON file. Returns an empty collection if file is missing."""
    data_path = _get_data_path()
    collection = TripCollection()

    if not os.path.exists(data_path):
        return collection

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            list_of_dicts = json.load(f)
            for d in list_of_dicts:
                collection.add(Destination(**d))
    except (json.JSONDecodeError, IOError):
        # If there's an error reading the file, we return an empty collection as a fallback
        pass

    return collection

def save_trips(collection: TripCollection) -> None:
    """Saves a TripCollection to a JSON file, creating the data directory if needed."""
    data_path = _get_data_path()
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    list_of_dicts = [asdict(d) for d in collection.get_all()]

    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(list_of_dicts, f, indent=2)
