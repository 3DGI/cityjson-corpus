cmake_minimum_required(VERSION 3.20)

project(cjlib_native_benchmark LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CJLIB_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../../cjlib" CACHE PATH "Path to the cjlib repository")
set(CJLIB_FFI_INCLUDE_DIR "${CJLIB_ROOT}/ffi/cpp/include" CACHE PATH "Path to cjlib C++ wrapper headers")
set(CJLIB_FFI_CORE_INCLUDE_DIR "${CJLIB_ROOT}/ffi/core/include" CACHE PATH "Path to generated cjlib C ABI headers")

if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
  set(CJLIB_FFI_CORE_SHARED_LIB "${CJLIB_ROOT}/target/release/libcjlib_ffi_core.dylib" CACHE FILEPATH "Built cjlib ffi shared library")
elseif(WIN32)
  set(CJLIB_FFI_CORE_SHARED_LIB "${CJLIB_ROOT}/target/release/cjlib_ffi_core.dll" CACHE FILEPATH "Built cjlib ffi shared library")
else()
  set(CJLIB_FFI_CORE_SHARED_LIB "${CJLIB_ROOT}/target/release/libcjlib_ffi_core.so" CACHE FILEPATH "Built cjlib ffi shared library")
endif()

if(NOT EXISTS "${CJLIB_FFI_INCLUDE_DIR}/cjlib/cjlib.hpp")
  message(FATAL_ERROR "Missing cjlib C++ wrapper header at ${CJLIB_FFI_INCLUDE_DIR}/cjlib/cjlib.hpp")
endif()

if(NOT EXISTS "${CJLIB_FFI_CORE_INCLUDE_DIR}/cjlib/cjlib.h")
  message(FATAL_ERROR "Missing generated C ABI header at ${CJLIB_FFI_CORE_INCLUDE_DIR}/cjlib/cjlib.h")
endif()

if(NOT EXISTS "${CJLIB_FFI_CORE_SHARED_LIB}")
  message(FATAL_ERROR "Missing cjlib ffi shared library at ${CJLIB_FFI_CORE_SHARED_LIB}")
endif()

add_library(cjlib_ffi_core SHARED IMPORTED GLOBAL)
set_target_properties(cjlib_ffi_core PROPERTIES IMPORTED_LOCATION "${CJLIB_FFI_CORE_SHARED_LIB}")

add_executable(cjlib_native_benchmark main.cpp)
target_include_directories(
  cjlib_native_benchmark
  PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}"
    "${CJLIB_FFI_INCLUDE_DIR}"
    "${CJLIB_FFI_CORE_INCLUDE_DIR}"
)
target_link_libraries(cjlib_native_benchmark PRIVATE cjlib_ffi_core)

get_filename_component(CJLIB_FFI_CORE_LIB_DIR "${CJLIB_FFI_CORE_SHARED_LIB}" DIRECTORY)
set_target_properties(cjlib_native_benchmark PROPERTIES BUILD_RPATH "${CJLIB_FFI_CORE_LIB_DIR}")
