#include <iostream>
#include <string>

#include "compiler/compiler.hpp"

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

    std::ifstream file(file_path);
    file.close();

    compiler_data compiler;
    
    compiler.instructions.push_back("moja_mala_nesi:100");

    compiler.dump();

    compiler.write_to_inst_bin();

    return 0;
}
