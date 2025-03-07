# **Python Chess Engine**  

## **General Info**  
I have been playing chess since primary school, and one day, I thought about creating a chess engine in Python.

## **Technologies Used**  
- **Python 3.7.8**  
- **Pygame 2.0.1**  
- **NumPy (planned for optimization)**  

## **Featurest**  
✔ Play against another player locally (PvP Mode)  
✔ Move logging & undo/reset functionality (`Z` to undo, `R` to reset)  
✔ Basic chess rules implemented  


## **Instructions**  

1. **Clone the repository:**  
   ```sh  
   git clone https://github.com/yourusername/chess-engine.git  
   cd chess-engine  
   ```  
2. **Install dependencies:**  
   ```sh  
   python3 -m pip install -r requirements.txt  
   ```  
3. **Run the game:**  
   ```sh  
   python3 ChessMain.py  
   ```  
4. **Controls:**  
   - Press **Z** to undo a move  
   - Press **R** to reset the game  

## **Future Improvements**  

- **Move Ordering:** Prioritize checks, captures, and threats to improve alpha-beta pruning.  
- **King Safety Evaluation:** Consider king positioning in the middle and endgame separately.  
- **Opening Book:** Implement an opening database for better early-game play.    
- Detect and handle **threefold repetition** and **50-move rule** for stalemate    
- Hashing previously visited positions to avoid redundant calculations  
---  
 

Inspired by Eddie Sharick’s tutorial series, this project aims to implement efficient move generation, evaluation strategies, and UI improvements to create a fully functional chess-playing engine. Future plans include **move optimization, board evaluation, and AI enhancements** to improve gameplay strength.

