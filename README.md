# IA-2027_1-Lab-2

Search algorithms demonstration for the Artificial Intelligence course (2027-1) taught by Dr. José Jaime Camacho Escoto. This project implements the *A\**, *BFG*, and *Bidirectional* search algorithms to find the solution for a Rubik's Cube.

## Getting Started

### Prerequisites

First, ensure you have installed the required dependencies listed in the requirements file:

```bash
pip install -r requirements.txt
```

### Usage Instructions

1. **Launch the Application**  
   Run the main program from your terminal:
   ```bash
   python3 src/interfaz_rubik.py
   ```

2. **Scramble the Cube**  
   Using the graphical interface, select the number of random moves to scramble the cube, or manually input the moves yourself.

3. **Find a Solution**  
   Select one of the three available search algorithms (A*, BFG, or Bidirectional) and click the **`Find a solution`** button to start the search.

4. **Solve the Cube**  
   If a solution is successfully found within the established time and memory limits, you can watch the cube solve itself by clicking the **`Apply solution`** button.
