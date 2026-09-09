cmake_minimum_required(VERSION 3.10)
project(uniflow_receiver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

file(GLOB SOURCES "src/*.cpp")

add_executable(receiver ${SOURCES})

find_package(Threads REQUIRED)
target_link_libraries(receiver PRIVATE Threads::Threads)