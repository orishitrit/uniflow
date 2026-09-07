#include "../include/receive.hpp"
#include "../include/crc.hpp"

#include <iostream>
#include <vector>
#include <cstring>
#include <arpa/inet.h>
namespace uniflow {
ReceiverNode::ReceiverNode(int worker_id, uint16_t listen_port, const std::string& uds_path)
        : worker_id(worker_id), listen_port(listen_port), uds_path(uds_path), udp_listener(listen_port), uds_client(uds_path) {}

bool ReceiverNode::init() {
    if (!udp_listener.is_valid()) {
        std::cerr << "[ReceiveNode] Failed to initialize UDP listener on port " << listen_port << std::endl;
        return false;
    }

    std::cout << "[ReceiveNode] Connecting to session manager at " << uds_path << "..." << std::endl;
    if (!uds_client.connect_to_manager(worker_id)) {
        std::cerr << "[ReceiveNode] Failed to connect to Session Manager." << std::endl;
        return false;
    }

    std::cout << "[ReceiveNode] Successfully initialized Worker ID: " << worker_id 
              << " | Listening Port: " << listen_port << std::endl;

  return true;
}


void ReceiverNode::run_loop(){
    is_running = true;

    std::vector<uint8_t> rx_buffer;

    std::cout << "[ReceiveNode] RX Worker " << worker_id << " entering main execution loop...\n";

    while(is_running){
        //block and receive incoming UDP packets
        ssize_t bytes_received = udp_listener.receive(rx_buffer);
        if (bytes_received < 0) {
            if (!is_running) break;
            std::cerr << "[ReceiveNode] Error receiving UDP packet." << std::endl;
            continue;
        }

        if(static_cast<size_t>(bytes_received) < sizeof(uint32_t)){
            std::cerr << "[ReceiveNode Warning] Received runt packet (" << bytes_received 
                      << " bytes). Dropping packet.\n";
            continue;
        }

        //Extract 4 byte CRC32 header
        uint32_t received_crc;
        std::memcpy(&received_crc, rx_buffer.data(), sizeof(uint32_t));
        uint32_t expected_crc = ntohl(received_crc);

        //Isolate Payload
        const uint8_t* payload_data = rx_buffer.data() + sizeof(uint32_t);
        size_t payload_size = bytes_received - sizeof(uint32_t);

        //verify CRC
        if(!CRC32::verify(payload_data, payload_size, expected_crc)){
            uint32_t calculated_crc = CRC32::calculate(payload_data, payload_size);
            std::cerr << "[ReceiveNode Error] CRC Mismatch! Expected: 0x" << std::hex << expected_crc 
                      << ", Calculated: 0x" << calculated_crc << std::dec << ". Packet dropped!\n";

          continue;
        }

        //Send payload to session manager
        if(!uds_client.send_chunk(payload_data, payload_size)){
            std::cerr << "[ReceiveNode Error] Failed to send payload to Session Manager\n";
            continue;
        }
    }
    
    std::cout << "[ReceiveNode] RX Processing loop stopped." << std::endl;
}

void ReceiverNode::stop() {
    is_running = false;
    udp_listener.close_socket();
    uds_client.disconnect();
}

}