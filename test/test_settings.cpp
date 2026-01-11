#include <catch2/catch_test_macros.hpp>

#include "forscape_settings.h"

using namespace Forscape;

TEST_CASE( "Defaults" ) {
    const Settings& default_settings = getDefaultSettings();
    REQUIRE(getUnusedVariableOption(default_settings) == UnusedVariableOption::WARN);
    REQUIRE(getTransposeTOption(default_settings) == TransposeTOption::WARN);
    REQUIRE(getScopeShadowingOption(default_settings) == ScopeShadowingOption::IGNORE);
    REQUIRE(getImplicitSymbolDeclarationOption(default_settings) == ImplicitSymbolDeclarationOption::ERROR);
}
