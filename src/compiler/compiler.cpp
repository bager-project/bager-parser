#include "compiler.hpp"

void compiler_data::dump()
{
    printf("=== DUMPING DATA ===\n");
    for (auto i: compiler_data::instructions)
        std::cout << i << '\n';
}

void compiler_data::write_to_inst_bin()
{
    std::ofstream inst_bin("inst.bin", std::ios::out | std::ios::binary | std::ios::app);
    std::ostream_iterator<std::string> output_iterator(inst_bin, "\n");
    std::copy(compiler_data::instructions.begin(), compiler_data::instructions.end(), output_iterator);
}
