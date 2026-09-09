#pragma once

#include <cstdint>
#include <vector>
#include <string>

namespace uniflow {
class UDSClient {
public:
    explicit UDSClient(std::string socket_path);
    ~UDSClient();

    UDSClient(const UDSClient&) = delete;
    UDSClient& operator=(const UDSClient&) = delete;

    UDSClient(UDSClient&& other) noexcept;
    UDSClient& operator=(UDSClient&& other) noexcept;

    bool connect_to_manager(int worker_id);

    bool send_chunk(const uint8_t* data, size_t length);
    bool send_chunk(const std::vector<uint8_t>& data);

    bool is_connected() const;
    void disconnect();

private:
    int socket_fd{-1};
    std::string socket_path;
};
}