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
