#include <iostream>
#include <string>

#include "compiler/compiler.hpp"
#include "parser/parser.hpp"

int main(int argc, char* argv[])
{
    std::string file_path = "";

    std::cout << "B.A.G.E.R project documentation parser!\r\n";

    if (argc < 2)
    {
        std::cout << "Enter file path: ";
        getline(std::cin, file_path);
    }

    else
    {
        file_path = argv[1];
    }

    test();

    return 0;
}
