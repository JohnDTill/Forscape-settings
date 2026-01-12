cmake_minimum_required(VERSION 3.5)

project(ForscapeSettings VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(INC ${CMAKE_CURRENT_SOURCE_DIR}/include)
set(SRC ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(META ${CMAKE_CURRENT_SOURCE_DIR}/meta)
include_directories(${INC})

set(GEN_FILES
    ${SRC}/forscape_settings.cpp
    ${INC}/forscape_settings.h
    ${SRC}/forscape_settings_diff.cpp
    ${SRC}/forscape_settings_diff.h)

set(SRC_FILES
    ${GEN_FILES})

add_library(ForscapeSettingsLib SHARED ${SRC_FILES})

add_custom_target(
    codegen ALL
    COMMAND python3 codegen.py
    WORKING_DIRECTORY ${META}
    BYPRODUCTS ${GEN_FILES}
    COMMENT "Performing codegen"
)
add_dependencies(ForscapeSettingsLib codegen)

set_target_properties(ForscapeSettingsLib PROPERTIES VERSION ${PROJECT_VERSION})
set_target_properties(ForscapeSettingsLib PROPERTIES SOVERSION ${PROJECT_VERSION_MAJOR})
set_target_properties(ForscapeSettingsLib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

add_library(Forscape::Settings ALIAS ForscapeSettingsLib)
target_include_directories(ForscapeSettingsLib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Qt layer
find_package(QT NAMES Qt5 Qt6 COMPONENTS Widgets REQUIRED)
find_package(Qt${QT_VERSION_MAJOR} COMPONENTS Widgets REQUIRED)

set(QT_FILES
    ${SRC}/forscape_settings_diff_dialog.cpp
    ${SRC}/forscape_settings_diff_dialog.h)
add_library(QtForscapeSettingsLib SHARED ${QT_FILES})
target_link_libraries(QtForscapeSettingsLib PUBLIC
    Qt${QT_VERSION_MAJOR}::Widgets
    ForscapeSettingsLib)

# Testing setup
if(PROJECT_IS_TOP_LEVEL)
find_package(Catch2 CONFIG REQUIRED)
enable_testing()
add_executable(Tests
    test/test_settings.cpp)
target_include_directories(Tests PUBLIC src)
target_link_libraries(Tests PRIVATE ForscapeSettingsLib Catch2::Catch2WithMain)
add_test(NAME Tests COMMAND Tests)
endif(PROJECT_IS_TOP_LEVEL)
