#pragma once

#include <vector>
#include <cstdint>
#include <sys/types.h>
#include <netinet/in.h>
#include <string>

namespace uniflow {
class UDPListener {
public:
    explicit UDPListener(uint16_t listener_port);

    ~UDPListener();

    UDPListener(const UDPListener&) = delete;
    UDPListener& operator=(const UDPListener&) = delete;

    UDPListener(UDPListener&& other) noexcept;
    UDPListener& operator=(UDPListener&& other) noexcept;

    bool is_valid();

    ssize_t receive(std::vector<uint8_t>& packet_buffer, size_t max_buffer_size = 65535);

    void close_socket();

private:
    int socket_fd{-1};
    uint16_t port{0};
    sockaddr_in server_addr{};
};

}