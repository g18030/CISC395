I am building a Quote Collection CLI app.

The project already has:
- src/models.py with Quote (@dataclass) and QuoteCollection
  QuoteCollection methods: add(), get_all(), search_by_text(), get_by_index(), remove(), __len__()
- src/storage.py with load_quotes() -> QuoteCollection and save_quotes(collection) -> None

Read src/models.py and src/storage.py first, then create src/main.py.

src/main.py must:
1. Fix the import path at the top so it works when run from the quote_collection/ root:
       import sys, os
       sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

2. Import Quote, QuoteCollection from src.models
   Import load_quotes, save_quotes from src.storage

3. On startup: collection = load_quotes()

4. Show this menu in a loop until the user quits:
       === Quote Collection ===
       [1] Add quote
       [2] View all quotes
       [3] Delete quote
       [4] Quit

5. Implement each option using QuoteCollection methods:
   [1] Add: input text, person, medianame -> Quote -> collection.add() -> save_quotes()
   [2] View all: if len(collection) == 0 print "No quotes saved yet."
       else print each quote numbered with text, person, and medianame
   [3] Delete: if len(collection) == 0 print "No quotes to delete."
       else: show numbered list -> input number -> collection.remove(n-1) -> save_quotes() -> print "Quote deleted."
   [4] Quit: print "Goodbye!" and exit

6. Handle invalid menu input with: print("Invalid option, try again.")

Use only input() and print(). No external libraries.
Write the file directly to src/main.py.
