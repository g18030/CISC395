from dataclasses import dataclass, field
from datetime import date

@dataclass
class Destination:
    name: str
    country: str
    budget: float
    notes: list[str] = field(default_factory=list)
    date_added: str = field(default_factory=lambda: date.today().isoformat())
    visited: bool = False

    def add_note(self, note: str) -> None:
        """Appends a note to the destination's notes list."""
        self.notes.append(note)

class TripCollection:
    def __init__(self):
        self._trips: list[Destination] = []

    def add(self, destination: Destination) -> None:
        """Adds a Destination object to the collection."""
        self._trips.append(destination)

    def get_all(self) -> list[Destination]:
        """Returns all destinations in the collection."""
        return self._trips

    def search_by_country(self, country: str) -> list[Destination]:
        """Returns destinations matching the country name (case-insensitive)."""
        return [t for t in self._trips if t.country.lower() == country.lower()]

    def get_by_index(self, index: int) -> Destination:
        """Returns the destination at the given index."""
        return self._trips[index]

    def __len__(self) -> int:
        """Returns the number of destinations in the collection."""
        return len(self._trips)

    def get_wishlist(self) -> list[Destination]:
        """Returns trips where visited == False."""
        return [t for t in self._trips if not t.visited]

    def get_visited(self) -> list[Destination]:
        """Returns trips where visited == True."""
        return [t for t in self._trips if t.visited]

    def mark_visited(self, index: int) -> None:
        """Sets the trip at the given index as visited."""
        self._trips[index].visited = True
