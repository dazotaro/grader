#include <cstdio>
#include "Sudoku.hpp"
#include "MySudoku.hpp"

int test01(void)
{
    // STUDENT'S
    //----------------------------
    Sudoku puzzle(9);
    if (!puzzle.loadBoard("./board01.txt"))
    {
        std::printf("Board not properly loaded\n");
        return 0;        
    }

    puzzle.solve();
    
    puzzle.printBoardToFile("yourboard01.txt");
    
    // GRADING
    //--------
    MySudoku my_puzzle(9);

    if (!my_puzzle.loadBoard("./yourboard01.txt"))
    {
        std::printf("Board not properly loaded\n");
        return 0;        
    }
    
    my_puzzle.printBoard();

    return 0;
}


int test02(void)
{
    // STUDENT'S
    //----------------------------
    Sudoku puzzle(9);
    if (!puzzle.loadBoard("./board02.txt"))
    {
        std::printf("Board not properly loaded\n");
        return 0;        
    }

    return 0;
}



int test03(void)
{
    // STUDENT'S
    //----------------------------
    Sudoku puzzle(9);
    if (!puzzle.loadBoard("./board03.txt"))
    {
        std::printf("Board not properly loaded\n");
        return 0;        
    }


    puzzle.solve();
    
    puzzle.printBoardToFile("yourboard03.txt");
    
    // GRADING
    //--------
    MySudoku my_puzzle(9);

    if (!my_puzzle.loadBoard("./yourboard03.txt"))
    {
        std::printf("Board not properly loaded\n");
        return 0;        
    }
    
    my_puzzle.printBoard();

    return 0;
}



int (*pTests[])() = {test01, test02, test03}; 

int main(int argc, char ** argv)
    try 
    {
        if (argc > 1)
        {
            int test = 0;
            std::sscanf(argv[1],"%i",&test);
            pTests[test - 1]();
        }
        return 0;
    }
    catch( char const* str)
    {
        std::printf("%s\n", str);
    }

