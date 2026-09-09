#include "../include/uds_client.hpp"

#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <iostream>
#include <utility>
#include <cstring>


namespace uniflow {
UDSClient::UDSClient(std::string path) : socket_path(std::move(path)) {}

UDSClient::~UDSClient() {
    disconnect();
}

UDSClient::UDSClient(UDSClient&& other) noexcept
    : socket_path(std::move(other.socket_path)), socket_fd(other.socket_fd) {
    other.socket_fd = -1;
}

UDSClient& UDSClient::operator=(UDSClient&& other) noexcept {
    if (this != &other) {
        disconnect();
        socket_path = std::move(other.socket_path);
        socket_fd = other.socket_fd;
        other.socket_fd = -1;
    }
    return *this;
}

bool UDSClient::connect_to_manager(int worker_id) {
    socket_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (socket_fd < 0) {
        std::cerr << "[RX UDSClient] Failed to create socket\n";
        return false;
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, socket_path.c_str(), sizeof(addr.sun_path) - 1);

    if(connect(socket_fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        std::cerr << "[RX UDSClient] Failed to connect to manager\n";
        disconnect();
        return false;
    }

    std::string ident_msg = "RX_WORKER:" + std::to_string(worker_id);
    if (!send_chunk(reinterpret_cast<const uint8_t*>(ident_msg.data()), ident_msg.size())) {
        std::cerr << "[RX UDSClient] Failed to send worker identification" << std::endl;
        disconnect();
        return false;
    }

    return true;
}


bool UDSClient::is_connected() const {
    return socket_fd >= 0;
}

void UDSClient::disconnect() {
    if (socket_fd >= 0) {
        close(socket_fd);
        socket_fd = -1;
    }
}

bool UDSClient::send_chunk(const uint8_t* data, size_t length) {
    if (!is_connected() || data == nullptr || length == 0) {
        return false;
    }

    uint32_t payload_size_net = htonl(static_cast<uint32_t>(length));
    
    //Send 4 byte header
    if (write(socket_fd, &payload_size_net, sizeof(payload_size_net)) != sizeof(payload_size_net)) {
        std::cerr << "[RX UDSClient] Failed to send length header" << std::endl;
        return false;
    }

    //Send chunk payload
    ssize_t bytes_sent = write(socket_fd, data, length);
    if (bytes_sent < 0 || static_cast<size_t>(bytes_sent) != length) {
        std::cerr << "[RX UDSClient] Failed to send full payload" << std::endl;
        return false;
    }

    return true;
}

bool UDSClient::send_chunk(const std::vector<uint8_t>& data) {
    return send_chunk(data.data(), data.size());
}

}