#include "crc.hpp"
#include <array>

namespace uniflow {

const uint32_t* CRC32::get_lookup_table() {
    static const auto table = []() {
        std::array<uint32_t, 256> table{};
        
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t crc = i;
            for (uint32_t j = 0; j < 8; ++j) {
                if (crc & 1) {
                    crc = (crc >> 1) ^ CRC32_POLYNOMIAL;
                } else {
                    crc >>= 1;
                }
            }
            table[i] = crc;
        }
        return table;
    }();

    return table.data();
}

uint32_t CRC32::calculate(const uint8_t* data, size_t length) {
    if (data == nullptr || length == 0) {
        return 0;
    }

    const uint32_t* table = get_lookup_table();
    uint32_t crc = 0xFFFFFFFFu;

    for (size_t i = 0; i < length; ++i) {
        uint8_t lookup_index = static_cast<uint8_t>((crc ^ data[i]) & 0xFF);
        crc = (crc >> 8) ^ table[lookup_index];
    }

    return crc ^ 0xFFFFFFFFu;
}

uint32_t CRC32::calculate(const std::vector<uint8_t>& buffer) {
    return calculate(buffer.data(), buffer.size());
}

}