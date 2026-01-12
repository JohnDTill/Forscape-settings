#include <catch2/catch_test_macros.hpp>

#include "forscape_settings.h"

using namespace Forscape;

TEST_CASE( "Defaults" ) {
    const Settings& default_settings = Settings::getDefaults();
    REQUIRE(default_settings.getUnusedVariableOption() == UnusedVariableOption::WARN);
    REQUIRE(default_settings.getTransposeTOption() == TransposeTOption::WARN);
    REQUIRE(default_settings.getScopeShadowingOption() == ScopeShadowingOption::IGNORE);
    REQUIRE(default_settings.getImplicitSymbolDeclarationOption() == ImplicitSymbolDeclarationOption::ERROR);
}
