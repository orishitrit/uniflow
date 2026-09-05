#include "../include/transmit.hpp"
#include <iostream>
#include <vector>

namespace uniflow{
TransmitNode::TransmitNode(uint32_t worker_id, const std::string& dest_ip, uint16_t udp_port, const std::string& uds_path)
    : worker_id(worker_id), udp_port(udp_port), reg_client(uds_path), udp_socket(dest_ip, udp_port) {}

bool TransmitNode::start(){
    if(!udp_socket.is_valid()){
        std::cerr << "[TransmitNode Error] Failed to create UDP socket." << std::endl;
        return false;
    }

    std::cout << "[TransmitNode] Connecting to registration server(master UDS)...\n";
    if(!reg_client.connect()){
        std::cerr << "[TransmitNode Error] Failed to connect to registration(UDS) server." << std::endl;
        return false;
    }

    if(!reg_client.register_worker(worker_id, udp_port)){
        std::cerr << "[TransmitNode Error] Failed to register worker with ID: " << worker_id << std::endl;
        return false;
    }

    std::cout << "[TransmitNode] Registered successfully! Worker ID: " 
              << worker_id << ", UDP Port: " << udp_port << std::endl;

    is_running = true;
    run_loop();

    return true;
}

void TransmitNode::stop(){
    is_running = false;
    reg_client.disconnect();
    std::cout << "[TransmitNode] Stopped." << std::endl;
}


void TransmitNode::run_loop(){
    std::vector<uint8_t> protobuf_data;

    while (is_running) {
        if (!reg_client.receive_message(protobuf_data)) { //Get chunk from dev 1 with UDS
            std::cout << "[TransmitNode] UDS connection closed or error. Stopping loop...\n";
            break;
        }

        if (protobuf_data.empty()) {
            continue;
        }

        uint32_t checksum = CRC32::calculate(protobuf_data); //CRC Calculation

        //build the complete packet for sending [4 bytes CRC32] + [Protobuf Data]
        std::vector<uint8_t> packet;
        packet.reserve(sizeof(uint32_t) + protobuf_data.size());

        //Adding the CRC at the beginning of the packet
        uint32_t checksum_net = htonl(checksum);
        const uint8_t* crc_bytes = reinterpret_cast<const uint8_t*>(&checksum_net);
        packet.insert(packet.end(), crc_bytes, crc_bytes + sizeof(checksum_net));

        // הוספת גוף ההודעה
        packet.insert(packet.end(), protobuf_data.begin(), protobuf_data.end());

        //Send the packet over UDP to the router
        ssize_t bytes_sent = udp_socket.send(packet);
        if (bytes_sent < 0) {
            std::cerr << "[TransmitNode Warning] Failed to send UDP packet\n";
        }
    }

    std::cout << "[TransmitNode] Transmission loop finished.\n";
}

}