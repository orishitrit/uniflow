#include "../include/registeration.hpp"

#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <iostream>
#include <cstring>
#include <arpa/inet.h>

namespace uniflow {

RegistrationClient::RegistrationClient(const std::string& socket_path)
    : socket_path(socket_path) {}


RegistrationClient::~RegistrationClient(){
    disconnect();
}

RegistrationClient::RegistrationClient(RegistrationClient&& other) noexcept
    : socket_path(std::move(other.socket_path)), socket_fd(other.socket_fd) {
    other.socket_fd = -1;
}

RegistrationClient& RegistrationClient::operator=(RegistrationClient&& other) noexcept {
    if (this != &other) {
        disconnect();
        socket_path = std::move(other.socket_path);
        socket_fd = other.socket_fd;
        other.socket_fd = -1;
    }
    return *this;
}

bool RegistrationClient::connect(){
    if(is_connected()){
        return true;
    }

    socket_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (socket_fd < 0) {
        std::cerr << "Error creating socket: " << strerror(errno) << std::endl;
        return false;
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path.c_str(), sizeof(addr.sun_path) - 1);

    if (::connect(socket_fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        std::cerr << "Error connecting to socket: " << strerror(errno) << std::endl;
        disconnect();
        return false;
    }

    return true;
}

void RegistrationClient::disconnect() {
    if (socket_fd >= 0) {
        close(socket_fd);
        socket_fd = -1;
    }
}

bool RegistrationClient::is_connected() const {
    return socket_fd >= 0;
}

bool RegistrationClient::write_exact(const uint8_t* source, size_t length) {
    size_t total_written = 0;
    while (total_written < length) {
        ssize_t written = ::write(socket_fd, source + total_written, length - total_written);
        if (written <= 0) {
            return false;
        }
        total_written += written;
    }
    return true;
}

bool RegistrationClient::read_exact(uint8_t* destination, size_t length) {
    size_t total_read = 0;
    while (total_read < length) {
        ssize_t bytes_read = ::read(socket_fd, destination + total_read, length - total_read);
        if (bytes_read <= 0) {
            return false;
        }
        total_read += bytes_read;
    }
    return true;
}


bool RegistrationClient::register_worker(uint32_t worker_id, uint16_t udp_port) {
    if (!is_connected()) {
        return false;
    }

    std::string reg_msg = "REGISTER:" + std::to_string(worker_id) + ":" + std::to_string(udp_port);
    
    uint32_t msg_size = htonl(static_cast<uint32_t>(reg_msg.size()));
    
    if (!write_exact(reinterpret_cast<const uint8_t*>(&msg_size), sizeof(msg_size))) {
        return false;
    }

    return write_exact(reinterpret_cast<const uint8_t*>(reg_msg.data()), reg_msg.size());
}

bool RegistrationClient::receive_message(std::vector<uint8_t>& buffer) {
    if (!is_connected()) {
        return false;
    }

    uint32_t msg_length_net = 0;
    if (!read_exact(reinterpret_cast<uint8_t*>(&msg_length_net), sizeof(msg_length_net))) {
        return false;
    }

    uint32_t msg_length = ntohl(msg_length_net);

    buffer.resize(msg_length);

    return read_exact(buffer.data(), msg_length);
}

}