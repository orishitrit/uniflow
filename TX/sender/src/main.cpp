#include "../include/transmit.hpp"

#include <iostream>
#include <memory>
#include <string>
#include <csignal>

namespace {
    uniflow::TransmitNode* g_node_ptr = nullptr;

    void signal_handler(int signal) {
        if (signal == SIGINT || signal == SIGTERM) {
            std::cout << "\n[Main] Shutdown signal received. Stopping sender...\n";
            if (g_node_ptr != nullptr) {
                g_node_ptr->stop();
            }
        }
    }
}

int main(int argc, char* argv[]) {
    if(argc < 5){
        return 1;
    }

    //argumets: worker id, dest ip, udp port, uds path
    try{
        uint32_t worker_id = static_cast<uint32_t>(std::stoul(argv[1]));
        std::string dest_ip = argv[2];
        uint16_t udp_port = static_cast<uint16_t>(std::stoul(argv[3]));
        std::string uds_path = argv[4];

        std::cout << "---------------------------\n";
        std::cout << " Starting Sender Node\n";
        std::cout << " Worker ID: " << worker_id << "\n";
        std::cout << " Target IP: " << dest_ip << "\n";
        std::cout << " UDP Port : " << udp_port << "\n";
        std::cout << " UDS Path : " << uds_path << "\n";
        std::cout << "---------------------------\n";

        uniflow::TransmitNode transmitter(worker_id, dest_ip, udp_port, uds_path);
        g_node_ptr = &transmitter;

        std::signal(SIGINT, signal_handler);
        std::signal(SIGTERM, signal_handler);

        if(!transmitter.start()){
            std::cerr << "[Main Error] TransmitNode failed to start.\n";
            return 1;
        }
    }
    catch (const std::exception& e) {
        std::cerr << "[Main Exception] " << e.what() << "\n";
        return 1;
    }
    
    std::cout << "[Main] Sender exited cleanly.\n";

    return 0;
}