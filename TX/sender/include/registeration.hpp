#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <sys/socket.h>
#include <sys/un.h>

namespace uniflow {

class RegistrationClient {
public:
    RegistrationClient(const std::string& socket_path);

    ~RegistrationClient();

    RegistrationClient(const RegistrationClient&) = delete;
    RegistrationClient& operator=(const RegistrationClient&) = delete;

    RegistrationClient(RegistrationClient&& other) noexcept;
    RegistrationClient& operator=(RegistrationClient&& other) noexcept;

    bool connect();
    bool register_worker(uint32_t worker_id, uint16_t udp_port);
    bool receive_message(std::vector<uint8_t>& buffer);

    bool is_connected() const;
    void disconnect();

private:
    std::string socket_path;
    int socket_fd{-1};

    bool read_exact(uint8_t* dest, size_t length);
    bool write_exact(const uint8_t* source, size_t length);
};

}