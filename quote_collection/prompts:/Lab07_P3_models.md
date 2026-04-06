I am building a Quote Collection CLI app. The project structure is:

  quote_collection/
├── src/
│   ├── models.py     ← data class + collection class
│   ├── storage.py    ← load/save JSON (same pattern as trip_notes)
│   └── main.py       ← menu loop
└── data/

Create src/models.py with TWO classes using only the Python standard library
(dataclasses, field). No pip installs needed.

Class 1: Quote (@dataclass)
- text: str              (The quote text)
- person: str           (Who wrote/said this)
- medianame: str          (From which media)
- notes: list[str] = field(default_factory=list)
- Method: add_note(self, note: str) → appends note to self.notes

Class 2: QuoteCollection
- Stores a list of Quote objects internally as self._quotes
- Methods:
    add(self, quote: Quote) -> None
    get_all(self) -> list[Quote]
    search_by_text(self, text: str) -> list[Quote]  (case-insensitive match)
    get_by_index(self, index: int) -> Quote
    remove(self, index: int) -> None
    __len__(self) -> int

Do not add an if __name__ == "__main__" block.
Write the file directly to src/models.py.
