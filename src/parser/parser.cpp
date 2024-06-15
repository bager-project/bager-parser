#include "parser.hpp"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

Parser::Parser(std::string path)
{
    int width, height, bpp;

    uint8_t* rgb_image = stbi_load(path.c_str(), &width, &height, &bpp, 3);

    stbi_image_free(rgb_image);

    std::cout << std::to_string(width);
}
