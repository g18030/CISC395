import os
import json
from dataclasses import asdict
from src.models import Destination, TripCollection

def _get_data_path():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(BASE_DIR, "data", "trips.json")

def load_trips() -> TripCollection:
    data_path = _get_data_path()
    collection = TripCollection()
    
    if not os.path.exists(data_path):
        return collection
    
    try:
        with open(data_path, 'r') as f:
            trips_data = json.load(f)
            for d in trips_data:
                collection.add(Destination(**d))
    except (json.JSONDecodeError, FileNotFoundError):
        pass
        
    return collection

def save_trips(collection: TripCollection) -> None:
    data_path = _get_data_path()
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    
    list_of_dicts = [asdict(t) for t in collection.get_all()]
    
    with open(data_path, 'w') as f:
        json.dump(list_of_dicts, f, indent=2)
