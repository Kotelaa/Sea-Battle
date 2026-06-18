## ⚓ Sea Battle
 
A classic Battleship game built in Python. Play in the terminal against the computer.
 
---
 
## How to Play
 
- You have a 6×6 grid
- Ships are placed randomly at the start
- Enter coordinates to shoot at the enemy board
- If you hit a ship – you get another turn
- First to sink all enemy ships wins
---
 
## Board Symbols
 
| Symbol | Meaning |
|--------|---------|
| `О` | Empty cell |
| `■` | Your ship |
| `X` | Hit |
| `T` | Miss |
 
---
 
## Ships
 
| Count | Length |
|-------|--------|
| 1 | 3 cells |
| 2 | 2 cells |
| 4 | 1 cell |
 
Ships cannot touch each other, even diagonally.
 
---
 
## Project Structure
 
| Class | Role |
|-------|------|
| `Dot` | A single cell on the board |
| `Ship` | Ship with position, length and lives |
| `Board` | Grid – manages ships, shots and display |
| `User` | Human player – reads input from console |
| `AI` | Computer – shoots in random order |
| `Game` | Sets up boards and runs the game loop |
 
---
 
## Tech Stack
 
- **Language:** Python
- **Interface:** Terminal / command line
- **Dependencies:** None – standard Python 3.8+ only
---
 
## Getting Started
 
**1. Clone the repository**
 
```bash
git clone https://github.com/Kotelaa/Sea-Battle.git
cd Sea-Battle
```
 
**2. Run the game**
 
```bash
python battleship.py
```
 
---
 
## Notes
 
- Boards are randomly generated at the start of every game
- The AI shoots in a pre-shuffled random order
- The AI's ships are hidden from the player during the game
- If you hit – you shoot again; if the AI hits – it shoots again
