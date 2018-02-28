cmake_minimum_required(VERSION 2.8.6)
project (zyre_listener)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
########################################################################
# LIBZMQ dependency
########################################################################
find_package(libzmq REQUIRED)
IF (LIBZMQ_FOUND)
    include_directories(${LIBZMQ_INCLUDE_DIRS})
    list(APPEND LIBS ${LIBZMQ_LIBRARIES})
ELSE (LIBZMQ_FOUND)
    message( FATAL_ERROR "libzmq not found." )
ENDIF (LIBZMQ_FOUND)

########################################################################
# CZMQ dependency
########################################################################
find_package(czmq REQUIRED)
IF (CZMQ_FOUND)
    include_directories(${CZMQ_INCLUDE_DIRS})
    list(APPEND LIBS ${CZMQ_LIBRARIES})
ELSE (CZMQ_FOUND)
    message( FATAL_ERROR "czmq not found." )
ENDIF (CZMQ_FOUND)

########################################################################
# Zyre dependency
########################################################################
find_package(zyre REQUIRED)
IF (ZYRE_FOUND)
    include_directories(${ZYRE_INCLUDE_DIRS})
    list(APPEND LIBS ${ZYRE_LIBRARIES})
ELSE (ZYRE_FOUND)
    message( FATAL_ERROR "zyre not found." )
ENDIF (ZYRE_FOUND)

include_directories(
  include/
)

pkg_check_modules(JSONCPP jsoncpp)
link_libraries(${JSONCPP_LIBRARIES})

add_executable(zyre_listener
  src/extern/zyre/event.cpp
  src/extern/zyre/node.cpp
  src/extern/zyre/exception.cpp
  src/zyre_listener.cpp
  src/zyre_listener_main.cpp
)

target_link_libraries(zyre_listener
  zmq
  ${LIBS}
  ${JSONCPP_LIBRARIES}
)

target_compile_features(zyre_listener PRIVATE cxx_range_for)
