#pragma once

#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>

class compiler_data
{
    public:
        // Vars
        std::vector<std::string> instructions;
    
        //  Funcs
        void dump();
        void write_to_inst_bin();
};
