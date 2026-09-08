#include "../include/crc.hpp"

#include <array>
#include <cstddef>
namespace uniflow {
constexpr std::array<uint32_t, 256> generate_crc32_table() {
    std::array<uint32_t, 256> table{};
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t crc = i;
        for (int j = 0; j < 8; ++j) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc >>= 1;
            }
        }
        table[i] = crc;
    }
    return table;
}

uint32_t CRC32::calculate(const uint8_t* data, size_t length) {
    if(data == nullptr || length == 0) {
        return 0;
    }

    static const std::array<uint32_t, 256> crc_table = generate_crc32_table();
    uint32_t crc = 0xFFFFFFFFU;

    for(size_t i = 0; i < length; ++i) {
        uint8_t lookup_index = static_cast<uint8_t>((crc ^ data[i]) & 0xFF);
        crc = (crc >> 8) ^ crc_table[lookup_index];
    }

    return crc ^ 0xFFFFFFFFU;
}

uint32_t CRC32::calculate(const std::vector<uint8_t>& data) {
    return calculate(data.data(), data.size());
}

bool CRC32::verify(const uint8_t* data, size_t length, uint32_t expected_crc) {
    return calculate(data, length) == expected_crc;
}

}