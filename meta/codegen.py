import json
import os
import re

def get_definition():
    with open('settings_definition.json', encoding='utf-8') as settings_def_file:
        settings_def = json.load(settings_def_file)
        return settings_def
    

def varupper(val):
    return re.sub(r'\W+', '', val.strip().replace(' ', '_')).upper()

def vartitle(val):
    return re.sub(r'\W+', '', val.title())    


def main():
    settings_def = get_definition()
    options = settings_def["options"]
    errors = []

    header = (
        "#ifndef FORSCAPE_SETTINGS_H\n"
        "#define FORSCAPE_SETTINGS_H\n"
        "\n"
        "#include <array>\n"
        "#include <stddef.h>\n"
        "#include <stdint.h>\n"
        "#include <vector>\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
        "/// Locally-scoped compiler options which change the evaluation of Forscape code and IDE interactions\n"
        "struct Settings;\n"
        "\n"
        "/// Specifications to override a subset of settings\n"
        "struct SettingsDiff;\n"
        "\n"
    )

    src = (
        "#include \"forscape_settings.h\"\n"
        "\n"
        "#include <cassert>\n"
        "#include \"forscape_settings_diff.h\"\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
    )

    # Write compiler settings enums
    for compiler_setting, compiler_setting_vals in settings_def["compiler_settings"].items():
        header += (
            f"/// {compiler_setting_vals['brief']}.\n"
            f"enum class {vartitle(compiler_setting)}Option : uint8_t {{\n"
        )
        for option in compiler_setting_vals["options"]:
            header += f"    {varupper(option)},"
            if option in options:
                header += f"  ///< {options[option]['description']}"
            else:
                errors += f"Option {option} was not found (from setting {compiler_setting})"
            header += "\n"
        header += "};\n\n"

    # Write compiler settings struct
    header += (
        f"constexpr size_t NUM_COMPILER_SETTINGS = {len(settings_def['compiler_settings'])};\n"
        "\n"
        "struct Settings {\n"
        "    /// Get default settings before any user overrides\n"
        "    static const Settings& getDefaults() noexcept;\n"
        "\n"
        "    /// Mutate the settings in place with a diff\n"
        "    void applyDiff(const SettingsDiff& diff);\n"
        "\n"
        "    /// Perform necessary bookkeeping when entering a new scope\n"
        "    void enterScope();\n"
        "\n"
        "    /// Revert any setting updates made in the scope\n"
        "    void leaveScope() noexcept\n;"
        "\n"
    )

    for compiler_setting, compiler_setting_vals in settings_def["compiler_settings"].items():
        header += (
            f"    /// {compiler_setting_vals['brief']}.\n"
            f"    {vartitle(compiler_setting)}Option get{vartitle(compiler_setting)}Option() const noexcept;\n"
            "\n"
        )

    header += (
        "\n"
        "private:\n"
        "    std::array<uint8_t, NUM_COMPILER_SETTINGS> compiler_settings;\n"
        "    std::vector<size_t> num_settings_modified_per_scope;\n"
        "    std::vector<std::pair<uint8_t, uint8_t>> modified_settings;\n"
        "\n"
        "    Settings(const std::array<uint8_t, NUM_COMPILER_SETTINGS>& settings) noexcept;\n"
        "    static const Settings DEFAULT_SETTINGS;\n"
        "\n"
        "    #ifndef NDEBUG\n"
        "    bool isScopeNested() const noexcept;\n"
        "    #endif\n"
        "};\n"
        "\n"
    )

    # Write default settings
    src += (
        "Settings::Settings(const std::array<uint8_t, NUM_COMPILER_SETTINGS>& settings) noexcept\n"
        "    : compiler_settings(settings) {}\n"
        "\n"
        "const Settings Settings::DEFAULT_SETTINGS = {{\n"
    )
    for compiler_setting, compiler_setting_vals in settings_def["compiler_settings"].items():
        if compiler_setting_vals["default"] in compiler_setting_vals["options"]:
            src += f"    static_cast<uint8_t>({vartitle(compiler_setting)}Option::{varupper(compiler_setting_vals['default'])}),\n"
        else:
            errors += f"Default {compiler_setting_vals['default']} is not an option of {compiler_setting}"
    src += "}};\n\n"

    src += (
        "const Settings& Settings::getDefaults() noexcept {\n"
        "    return DEFAULT_SETTINGS;\n"
        "}\n"
        "\n"
        "void Settings::applyDiff(const SettingsDiff& diff) {\n"
        "    for(const auto [setting_id, setting_value] : diff.updates) {\n"
        "        modified_settings.push_back({setting_id, compiler_settings[setting_id]});\n"
        "        compiler_settings[setting_id] = setting_value;\n"
        "    }\n"
        "}\n"
        "\n"
        "void Settings::enterScope() {\n"
        "    num_settings_modified_per_scope.push_back(modified_settings.size());\n"
        "}\n"
        "\n"
        "void Settings::leaveScope() noexcept {\n"
        "    assert(isScopeNested());\n"
        "    const size_t num_settings_modified = num_settings_modified_per_scope.back();\n"
        "    num_settings_modified_per_scope.pop_back();\n"
        "    for(size_t i = modified_settings.size(); i --> num_settings_modified;){\n"
        "        const auto [setting_id, setting_value] = modified_settings[i];\n"
        "        compiler_settings[setting_id] = setting_value;\n"
        "    }\n"
        "    modified_settings.resize(num_settings_modified);\n"
        "}\n"
        "\n"
        "#ifndef NDEBUG\n"
        "bool Settings::isScopeNested() const noexcept {\n"
        "    return !num_settings_modified_per_scope.empty();\n"
        "}\n"
        "#endif\n"
        "\n"
    )

    # Write getter functions
    for idx, (compiler_setting, compiler_setting_vals) in enumerate(settings_def["compiler_settings"].items()):
        src += (
            f"{vartitle(compiler_setting)}Option Settings::get{vartitle(compiler_setting)}Option() const noexcept {{\n"
            f"    return static_cast<{vartitle(compiler_setting)}Option>(compiler_settings[{idx}]);\n"
            "}\n\n"
        )

    header += (
        "}  // namespace Forscape\n"
        "\n"
        "#endif  // #ifndef FORSCAPE_SETTINGS_H\n"
    )

    if len(errors) != 0:
        msg = "#error The codegen process had errors\n"
        for error in errors:
            msg += error + "\n"
        header = msg + '\n' + header

    src += (
        "}  // namespace Forscape\n"
    )

    os.makedirs(os.path.dirname("../src/forscape_settings.cpp"), exist_ok=True)
    with open(f"../src/forscape_settings.cpp", "w", encoding="utf-8") as src_file:
        src_file.write(src)

    os.makedirs(os.path.dirname("../include/forscape_settings.h"), exist_ok=True)
    with open(f"../include/forscape_settings.h", "w", encoding="utf-8") as header_file:
        header_file.write(header)

    if len(errors) != 0:
        raise Exception(f"Codegen had errors: {errors}")


if __name__ == "__main__":
    main()
