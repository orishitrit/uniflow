#pragma once

#include "../include/registeration.hpp"
#include "../include/udp_socket.hpp"
#include "../include/crc.hpp"

#include <string>
#include <cstdint>
#include <atomic>

namespace uniflow {
    
class TransmitNode {
public:
    TransmitNode(uint32_t worker_id, const std::string& dest_ip, uint16_t udp_port, const std::string& uds_path);

    ~TransmitNode() = default;

    TransmitNode(const TransmitNode&) = delete;
    TransmitNode& operator=(const TransmitNode&) = delete;

    bool start();

    void stop();

private:
    uint32_t worker_id;
    uint16_t udp_port;

    RegistrationClient reg_client;
    UDPSocket udp_socket;
    std::atomic<bool> is_running{false};

    void run_loop();
};

}
