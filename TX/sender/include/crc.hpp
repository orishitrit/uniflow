#pragma once

#include <cstdint>
#include <cstddef>
#include <vector>

namespace uniflow {

class CRC32 {
public:
    CRC32() = delete;

    static uint32_t calculate(const uint8_t* data, size_t length);

    static uint32_t calculate(const std::vector<uint8_t>& buffer);

private:
    static const uint32_t CRC32_POLYNOMIAL = 0xEDB88320u;
    static const uint32_t* get_lookup_table();
};

}