#include <catch2/catch_test_macros.hpp>

#include "forscape_settings.h"
#include "forscape_settings_diff.h"

using namespace Forscape;

TEST_CASE( "Valid Diff Serialisation" ) {
    const std::string_view test_str = "UnusedVariable=Error,ScopeShadowing=Warn,TransposeT=Ignore";
    REQUIRE(SettingsDiff::isValidSerial(test_str));

    const SettingsDiff diff = SettingsDiff::fromString(test_str);
    std::string out;
    diff.writeString(out);
    REQUIRE(out == test_str);
}

TEST_CASE( "Invalid Diff Serialisation" ) {
    REQUIRE_FALSE(SettingsDiff::isValidSerial("UnusedVariable=EarlGrey"));
    REQUIRE_FALSE(SettingsDiff::isValidSerial("Chamomile=Error"));
    REQUIRE_FALSE(SettingsDiff::isValidSerial("UnusedVariable|Error"));
    REQUIRE_FALSE(SettingsDiff::isValidSerial("UnusedVariable=Error,"));
}

TEST_CASE( "Diff application" ) {
    Settings settings = Settings::getDefaults();
    REQUIRE(settings.getUnusedVariableOption() == UnusedVariableOption::WARN);

    settings.enterScope();
    settings.applyDiff(SettingsDiff::fromString("UnusedVariable=Error"));
    REQUIRE(settings.getUnusedVariableOption() == UnusedVariableOption::ERROR);

    settings.applyDiff(SettingsDiff::fromString("UnusedVariable=Ignore"));
    REQUIRE(settings.getUnusedVariableOption() == UnusedVariableOption::IGNORE);

    settings.leaveScope();
    REQUIRE(settings.getUnusedVariableOption() == UnusedVariableOption::WARN);
}

TEST_CASE( "Buffer trip" ) {
    Settings settings = Settings::getDefaults();
    REQUIRE(settings.getUnusedVariableOption() == UnusedVariableOption::WARN);

    SettingsDiff diff = SettingsDiff::fromString("UnusedVariable=Error");
    std::vector<size_t> totally_a_parse_node = {1, 2, 3};  // Some mock data in the buffer
    diff.writeToBuffer(totally_a_parse_node);
    REQUIRE(totally_a_parse_node.size() == 5);
    REQUIRE(totally_a_parse_node[3] == 1);

    settings.applyDiff(SettingsDiffView::fromBuffer(&totally_a_parse_node[3]));
    REQUIRE(settings.getUnusedVariableOption() == UnusedVariableOption::ERROR);
}
