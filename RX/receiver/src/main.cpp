#include "receive.hpp"
#include <iostream>
#include <csignal>
#include <cstdlib>
#include <memory>

namespace {
    std::unique_ptr<uniflow::ReceiverNode> receive_node = nullptr;
}

void signal_handler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        std::cout << "\n[RX Main] Shutdown signal received. Gracefully stopping RX Node..." << std::endl;
        if (receive_node) {
            receive_node->stop();
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <worker_id> <listen_port> <uds_path>" << std::endl;
        std::cerr << "Example: " << argv[0] << " 1 8001 /tmp/uniflow_rx_master.sock" << std::endl;
        return 1;
    }

    //arguments: worker id, listen port, uds path
    try{
        int worker_id = std::stoi(argv[1]);
        uint16_t listen_port = static_cast<uint16_t>(std::stoi(argv[2]));
        std::string path = argv[3];

        std::cout << "---------------------------" << std::endl;
        std::cout << " Starting Receiver Node" << std::endl;
        std::cout << " Worker ID  : " << worker_id << std::endl;
        std::cout << " UDP Port   : " << listen_port << std::endl;
        std::cout << " UDS Path   : " << path << std::endl;
        std::cout << "---------------------------" << std::endl;

        //for ctrl + c shutdown
        std::signal(SIGINT, signal_handler);
        std::signal(SIGTERM, signal_handler);

        receive_node = std::make_unique<uniflow::ReceiverNode>(worker_id, listen_port, path);
        
        if(!receive_node->init()){
            std::cerr << "[RX Main] ReceiverNode failed to initialize." << std::endl;
            return 1;
        }
    }
    catch (const std::exception& e) {
        std::cerr << "[RX Main Exception] " << e.what() << "\n";
        return 1;
    }

    std::cout << "[RX Main] Receiver exited cleanly.\n";
    return 0;
}