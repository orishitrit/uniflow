#pragma once

#include <cstdint>
#include <vector>

namespace uniflow {
class CRC32 {
public:
    static uint32_t calculate(const uint8_t* data, size_t length);

    static uint32_t calculate(const std::vector<uint8_t>& data);

    static bool verify(const uint8_t* data, size_t length, uint32_t expected_crc);
};

}