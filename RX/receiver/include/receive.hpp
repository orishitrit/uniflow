#pragma once

#include "../include/udp_server.hpp"
#include "../include/uds_client.hpp"

#include <atomic>
#include <string>
#include <cstdint>

namespace uniflow {

class ReceiverNode {
public:
    ReceiverNode(int worker_id, uint16_t listen_port, const std::string& uds_path);
    ~ReceiverNode() = default;

    ReceiverNode(const ReceiverNode&) = delete;
    ReceiverNode& operator=(const ReceiverNode&) = delete;

    //init connection to session manager
    bool init();

    void run_loop();

    void stop();
private:
    int worker_id;
    uint16_t listen_port;
    std::string uds_path;

    UDPListener udp_listener;
    UDSClient uds_client;

    std::atomic<bool> is_running{false};
};
}