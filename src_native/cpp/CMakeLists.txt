cmake_minimum_required(VERSION 3.16)
project(ZiPackAccel LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(zipack_accel SHARED
    zipack_accel.cpp
    zipack_accel.h
)

target_include_directories(zipack_accel PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

if(WIN32)
    target_link_libraries(zipack_accel PRIVATE kernel32)
endif()
