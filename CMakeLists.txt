cmake_minimum_required(VERSION 3.10)

# Set compiler to gcc
set(CMAKE_C_COMPILER "gcc-9")
set(CMAKE_CXX_COMPILER "g++-9")

project(lercLib C CXX)

file(GLOB SOURCES "src/LercLib/*.cpp" "src/LercLib/Lerc1Decode/*.cpp") 

include_directories( 
	include
)

add_library(lercLib STATIC
             ${SOURCES}
			)
target_link_libraries(lercLib)