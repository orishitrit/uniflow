#include "../include/udp_server.hpp"

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>
#include <utility>

namespace uniflow {
UDPListener::UDPListener(uint16_t listener_port) : port(listener_port) {
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd < 0) {
        std::cerr << "Failed to create socket" << std::endl;
        return;
    }

    //prevent "Address already in use" error when restarting the server
    int optval = 1;
    setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;//(0.0.0.0)
    server_addr.sin_port = htons(listener_port);  

    if(bind(socket_fd, reinterpret_cast<struct sockaddr*>(&server_addr), sizeof(server_addr)) < 0) {
        std::cerr << "Failed to bind socket to port " << listener_port << std::endl;
        close_socket();
    }
}

UDPListener::~UDPListener() {
    close_socket();
}

UDPListener::UDPListener(UDPListener&& other) noexcept
    : socket_fd(other.socket_fd), port(other.port), server_addr(other.server_addr) {
    other.socket_fd = -1;
}

UDPListener& UDPListener::operator=(UDPListener&& other) noexcept {
    if (this != &other) {
        close_socket();
        socket_fd = other.socket_fd;
        port = other.port;
        server_addr = other.server_addr;
        other.socket_fd = -1;
    }
    return *this;
}

void UDPListener::close_socket() {
    if(is_valid()) {
        close(socket_fd);
        socket_fd = -1;
    }
}

bool UDPListener::is_valid() {
    return socket_fd >= 0;
}

ssize_t UDPListener::receive(std::vector<uint8_t>& packet_buffer, size_t max_buffer_size) {
    if(!is_valid()) {
        std::cerr << "Socket is invalid" << std::endl;
        return -1;
    }

    packet_buffer.resize(max_buffer_size);
    struct sockaddr_in client_addr{};
    socklen_t client_len = sizeof(client_addr);

    ssize_t bytes_received = recvfrom(socket_fd, packet_buffer.data(), packet_buffer.size(),
        0, reinterpret_cast<struct sockaddr*>(&client_addr), &client_len);

    if (bytes_received >= 0) {
        packet_buffer.resize(static_cast<size_t>(bytes_received));
    } else {
        packet_buffer.clear();
    }

    return bytes_received;
}

}