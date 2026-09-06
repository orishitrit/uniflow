#include "udp_socket.hpp"

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>
#include <utility>

namespace uniflow {

UDPSocket::UDPSocket(const std::string& dest_ip, uint16_t dest_port){
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd < 0) {
        std::cerr << "Error creating socket" << std::endl;
        return;
    }

    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(dest_port);

    if(inet_pton(AF_INET, dest_ip.c_str(), &dest_addr.sin_addr) <= 0) {
        std::cerr << "Invalid address/ Address not supported" << std::endl;
        close_socket();
    }
}

UDPSocket::~UDPSocket() {
    close_socket();
}

UDPSocket::UDPSocket(UDPSocket&& other) noexcept
    : socket_fd(other.socket_fd), dest_addr(other.dest_addr) {
    other.socket_fd = -1;
}

UDPSocket& UDPSocket::operator=(UDPSocket&& other) noexcept {
    if(this != &other) {
        close_socket();
        socket_fd = other.socket_fd;
        dest_addr = other.dest_addr;
        other.socket_fd = -1;
    }

    return *this;
}

void UDPSocket::close_socket(){
    if(socket_fd >= 0) {
        close(socket_fd);
        socket_fd = -1;
    }
}

bool UDPSocket::is_valid() const {
    return socket_fd >= 0;
}

ssize_t UDPSocket::send(const uint8_t* data, size_t length) {
    if(!is_valid() || data == nullptr || length == 0) {
        std::cerr << "Socket is not valid" << std::endl;
        return -1;
    }

    ssize_t bytes_sent = sendto(socket_fd, data, length, 0, (struct sockaddr*)&dest_addr, sizeof(dest_addr));
    if(bytes_sent < 0) {
        std::cerr << "Error sending data" << std::endl;
    }

    return bytes_sent;
}

ssize_t UDPSocket::send(const std::vector<uint8_t>& buffer) {
    return send(buffer.data(), buffer.size());
}

}