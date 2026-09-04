#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <cstddef>
#include <netinet/in.h>

namespace uniflow {
class UDPSocket {
public:
    UDPSocket(const std::string& dest_ip, uint16_t dest_port);
    ~UDPSocket();

    UDPSocket(const UDPSocket&) = delete;
    UDPSocket& operator=(const UDPSocket&) = delete;

    UDPSocket(UDPSocket&& other) noexcept;
    UDPSocket& operator=(UDPSocket&& other) noexcept;

    ssize_t send(const uint32_t* data, size_t length);
    ssize_t send(const std::vector<uint32_t>& buffer);

    bool is_valid() const;

private:
    int socket_fd;
    struct sockaddr_in dest_addr{};

    void close_socket();
};

}