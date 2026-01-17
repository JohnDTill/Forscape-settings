from collections import OrderedDict
import json
from math import ceil, log2
import os
from pathlib import Path
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
    inputs = [
        Path("settings_definition.json"),
        Path("codegen.py"),
    ]

    outputs = [
        Path("../src/forscape_settings.cpp"),
        Path("../include/forscape_settings.h"),
        Path("../src/forscape_settings_diff.cpp"),
        Path("../include/forscape_settings_diff.h"),
        Path("../src/forscape_settings_diff_dialog.ui")
    ]

    if all([path.is_file() for path in outputs]) and max([os.path.getmtime(path) for path in inputs]) < min([os.path.getmtime(path) for path in outputs]):
        return  # No sources changed
    
    print(
        f"Performing settings code generation (outputs exist: {all([path.is_file() for path in outputs])}, "
        f"last input change: {max([os.path.getmtime(path) for path in inputs])}, "
        f"last output change: {min([os.path.getmtime(path) for path in outputs if path.is_file()])})")

    settings_def = get_definition()
    options = OrderedDict(sorted(settings_def["options"].items()))
    settings = OrderedDict(sorted(settings_def["compiler_settings"].items()))
    errors = []

    max_options = max([len(setting["options"]) for setting in settings.values()])
    num_settings_bits = ceil(log2(len(settings)))
    num_options_bits = ceil(log2(max_options))
    setting_typedef = "uint8_t" if num_settings_bits <= 8 else "uint16_t"
    setting_option_pair_typedef = "uint8_t" if num_settings_bits + num_options_bits <= 8 else "uint16_t"

    settings_header = (
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
        "struct Settings;\n"
        "struct SettingsDiffView;\n"
        "\n"
        "typedef uint8_t SettingsOption;\n"
        "\n"
    )

    settings_src = (
        "#include \"forscape_settings.h\"\n"
        "\n"
        "#include <cassert>\n"
        "#include \"forscape_settings_diff.h\"\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
    )

    diff_header = (
        "#ifndef FORSCAPE_SETTINGS_DIFF_H\n"
        "#define FORSCAPE_SETTINGS_DIFF_H\n"
        "\n"
        "#include <stdint.h>\n"
        "#include <string>\n"
        "#include <string_view>\n"
        "#include <vector>\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
        "struct Settings;\n"
        "struct SettingsDiff;\n"
        "class SettingsDiffDialog;\n"
        "\n"
        "/// Immutable view of a diff to update settings\n"
        "struct SettingsDiffView {\n"
        "    /// Interpret a buffer as a SettingsDiffView.\n"
        "    /// This allows for reading a SettingsDiffView from a parse node.\n"
        "    static SettingsDiffView fromBuffer(const size_t* buffer) noexcept;\n"
        "\n"
        "private:\n"
        "    typedef uint8_t SettingsId;\n"
        "    typedef uint8_t SettingsOption;\n"
        "\n"
        "    size_t num_settings;\n"
        "    const std::pair<SettingsId, SettingsOption>* settings;\n"
        "\n"
        "    friend Settings;\n"
        "    friend SettingsDiff;\n"
        "};\n"
        "\n"
        "/// Specifications to override a subset of settings\n"
        "struct SettingsDiff {\n"
        "    /// Append a serialised representation of the SettingsDiff to a string.\n"
        "    void writeString(std::string& out) const;\n"
        "\n"
        "    /// Determine if a string is a valid serialised representation of a SettingsDiff.\n"
        "    static bool isValidSerial(std::string_view str) noexcept;\n"
        "\n"
        "    /// Deserialise a SettingsDiff from a string, writing errors for any invalidly specified settings.\n"
        "    /// Asserts if the argument is not valid serial.\n"
        "    static SettingsDiff fromString(std::string_view str);\n"
        "\n"
        "    /// Get a view of the diff.\n"
        "    /// This is invalidated when the diff changes.\n"
        "    SettingsDiffView view() const noexcept;\n"
        "\n"
        "    operator SettingsDiffView() const noexcept;\n"
        "\n"
        "    /// Write the diff to a buffer, which can be interpreted as a SettingsDiffView.\n"
        "    /// This allows for copying the diff to a parse node.\n"
        "    void writeToBuffer(std::vector<size_t>& buffer) const;\n"
        "\n"
        "private:\n"
        f"    typedef {setting_typedef} SettingsId;\n"
        "    typedef uint8_t SettingsOption;\n"
        "    std::vector<std::pair<SettingsId, SettingsOption>> updates;\n"
        "\n"
        "    friend SettingsDiffDialog;\n"
        "};\n"
        "\n"
        "}  // namespace Forscape\n"
        "\n"
        "#endif // FORSCAPE_SETTINGS_DIFF_H\n"
    )

    diff_src = (
        "#include \"forscape_settings_diff.h\"\n" \
        "\n"
        "#include <parallel_hashmap/phmap.h>\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
    )

    # Write compiler settings enums
    for compiler_setting, compiler_setting_vals in settings.items():
        settings_header += (
            f"/// {compiler_setting_vals['brief']}.\n"
            f"enum class {vartitle(compiler_setting)}Option : SettingsOption {{\n"
        )
        for option in compiler_setting_vals["options"]:
            settings_header += f"    {varupper(option)},"
            if option in options:
                settings_header += f"  ///< {options[option]['description']}"
            else:
                errors += f"Option {option} was not found (from setting {compiler_setting})"
            settings_header += "\n"
        settings_header += "};\n\n"

    # Write compiler settings struct
    settings_header += (
        "/// Locally-scoped compiler options which change the evaluation of Forscape code and IDE interactions\n"
        "struct Settings {\n"
        "    /// Get default settings before any user overrides\n"
        "    static const Settings& getDefaults() noexcept;\n"
        "\n"
        "    /// Mutate the settings in place with a diff\n"
        "    void applyDiff(const SettingsDiffView& diff);\n"
        "\n"
        "    /// Perform necessary bookkeeping when entering a new scope\n"
        "    void enterScope();\n"
        "\n"
        "    /// Revert any setting updates made in the scope\n"
        "    void leaveScope() noexcept;\n"
        "\n"
    )

    for compiler_setting, compiler_setting_vals in settings.items():
        settings_header += (
            f"    /// {compiler_setting_vals['brief']}.\n"
            f"    {vartitle(compiler_setting)}Option get{vartitle(compiler_setting)}Option() const noexcept;\n"
            "\n"
        )

    settings_header += (
        "\n"
        "private:\n"
        f"    static constexpr size_t NUM_COMPILER_SETTINGS = {len(settings)};\n"
        f"    typedef {setting_typedef} SettingsId;\n"
        "    std::array<SettingsId, NUM_COMPILER_SETTINGS> compiler_settings;\n"
        "    std::vector<size_t> num_settings_modified_per_scope;\n"
        "    std::vector<std::pair<SettingsId, SettingsOption>> modified_settings;\n"
        "\n"
        "    Settings(const std::array<SettingsId, NUM_COMPILER_SETTINGS>& settings) noexcept;\n"
        "    static const Settings DEFAULT_SETTINGS;\n"
        "\n"
        "    #ifndef NDEBUG\n"
        "    bool isScopeNested() const noexcept;\n"
        "    #endif\n"
        "};\n"
        "\n"
    )

    # Write default settings
    settings_src += (
        "Settings::Settings(const std::array<SettingsId, NUM_COMPILER_SETTINGS>& settings) noexcept\n"
        "    : compiler_settings(settings) {}\n"
        "\n"
        "const Settings Settings::DEFAULT_SETTINGS = {{\n"
    )
    for compiler_setting, compiler_setting_vals in settings.items():
        if compiler_setting_vals["default"] in compiler_setting_vals["options"]:
            settings_src += f"    static_cast<SettingsOption>({vartitle(compiler_setting)}Option::{varupper(compiler_setting_vals['default'])}),\n"
        else:
            errors += f"Default {compiler_setting_vals['default']} is not an option of {compiler_setting}"
    settings_src += "}};\n\n"

    settings_src += (
        "const Settings& Settings::getDefaults() noexcept {\n"
        "    return DEFAULT_SETTINGS;\n"
        "}\n"
        "\n"
        "void Settings::applyDiff(const SettingsDiffView& diff) {\n"
        "    for(size_t i = diff.num_settings; i-->0;){\n"
        "        const auto [setting_id, setting_value] = diff.settings[i];\n"
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
    for idx, (compiler_setting, compiler_setting_vals) in enumerate(settings.items()):
        settings_src += (
            f"{vartitle(compiler_setting)}Option Settings::get{vartitle(compiler_setting)}Option() const noexcept {{\n"
            f"    return static_cast<{vartitle(compiler_setting)}Option>(compiler_settings[{idx}]);\n"
            "}\n\n"
        )

    # Write diff serialisation
    diff_src += (
        f"typedef {setting_typedef} SettingsId;\n"
        "typedef uint8_t SettingsOption;\n"
        f"typedef {setting_option_pair_typedef} IdOptionPair;\n"
        "\n"
        "inline constexpr IdOptionPair optionToCode(SettingsId setting_id, SettingsOption option) noexcept {\n"
        f"    return setting_id | (option << {num_settings_bits});\n"
        "}\n"
        "\n"
        "void SettingsDiff::writeString(std::string& out) const {\n"
        "    bool subsequent = false;\n"
        "    for(const auto [setting_id, setting_value] : updates){\n"
        "        if(subsequent) out += ',';\n"
        "        subsequent = true;\n"
        "\n"
        "        switch(setting_id){\n"
    )
    for idx, compiler_setting in enumerate(settings_def["compiler_settings"]):
        diff_src += f"            case {idx}: out += \"{vartitle(compiler_setting)}\"; break;\n"
    diff_src += (
        "        }\n"
        "\n"
        "        out += '=';\n"
        "\n"
        "        switch(optionToCode(setting_id, setting_value)){\n"
    )
    for setting_id, compiler_setting_vals in enumerate(settings.values()):
        for option_id, option in enumerate(compiler_setting_vals["options"]):
            diff_src += (
                f"            case optionToCode({setting_id}, {option_id}): out += \"{vartitle(option)}\"; break;\n"
            )
    diff_src += (
        "        }\n"
        "    }\n"
        "}\n"
        "\n"
    )

    # Write diff deserialisation
    diff_src += (
        "static const phmap::flat_hash_map<std::string_view, std::pair<SettingsId, SettingsOption>> decoding_map {\n"
    )
    for setting_id, (compiler_setting, compiler_setting_vals) in enumerate(settings.items()):
        for option_id, option in enumerate(compiler_setting_vals["options"]):
            diff_src += f"    {{ \"{vartitle(compiler_setting)}={vartitle(option)}\", {{{setting_id},{option_id}}} }},\n"
    diff_src += "};\n\n"

    diff_src += (
        "bool SettingsDiff::isValidSerial(std::string_view str) noexcept {\n"
        "    size_t tail = str.size();\n"
        "    size_t index = tail-1;\n"
        "    for(;;) {\n"
        "        if(index == 0){\n"
        "            return decoding_map.find(str.substr(index, tail-index)) != decoding_map.cend();\n"
        "        }else if(str[index] == ','){\n"
        "            if(decoding_map.find(str.substr(index+1, tail-(index+1))) == decoding_map.cend()) return false;\n"
        "            tail = index;\n"
        "        }\n"
        "\n"
        "        index--;\n"
        "    }\n"
        "}\n"
        "\n"
    )

    diff_src += (
        "SettingsDiff SettingsDiff::fromString(std::string_view str){\n"
        "    SettingsDiff diff;\n"
        "\n"
        "    size_t index = 0;\n"
        "    while(index < str.size()){\n"
        "        const size_t start = index;\n"
        "        while(index < str.size() && str[index] != ',') index++;\n"
        "        const std::string_view setting_pair = str.substr(start, index-start);\n"
        "        assert(decoding_map.find(setting_pair) != decoding_map.cend());\n"
        "        diff.updates.push_back( decoding_map.find(setting_pair)->second );\n"
        "        index++;\n"
        "    }\n"
        "\n"
        "    return diff;\n"
        "}\n"
        "\n"
    )

    diff_src += (
        "SettingsDiffView SettingsDiff::view() const noexcept {\n"
        "    SettingsDiffView v;\n"
        "    v.num_settings = updates.size();\n"
        "    v.settings = updates.data();\n"
        "    return v;\n"
        "}\n"
        "\n"
        "SettingsDiff::operator SettingsDiffView() const noexcept {\n"
        "    return view();\n"
        "}\n"
        "\n"
    )

    diff_src += (
        "void SettingsDiff::writeToBuffer(std::vector<size_t>& buffer) const {\n"
        "    const size_t start = buffer.size();\n"
        "    const size_t num_setting_updates = updates.size();\n"
        "    const size_t num_setting_bytes = num_setting_updates * sizeof(std::pair<SettingsId, SettingsOption>);\n"
        "    const size_t num_setting_words = num_setting_bytes / sizeof(size_t) + num_setting_bytes % sizeof(size_t) != 0;\n"
        "    buffer.resize(start + 1 + num_setting_words);\n"
        "    buffer[start] = num_setting_updates;\n"
        "    std::memcpy(&buffer[start+1], updates.data(), num_setting_bytes);\n"
        "}\n"
        "\n"
    )

    diff_src += (
        "SettingsDiffView SettingsDiffView::fromBuffer(const size_t* buffer) noexcept {\n"
        "    SettingsDiffView v;\n"
        "    v.num_settings = *buffer;\n"
        "    v.settings = reinterpret_cast<const std::pair<SettingsId, SettingsOption>*>(buffer+1);\n"
        "    return v;\n"
        "}\n"
        "\n"
    )

    settings_header += (
        "}  // namespace Forscape\n"
        "\n"
        "#endif  // #ifndef FORSCAPE_SETTINGS_H\n"
    )

    if len(errors) != 0:
        msg = "#error The codegen process had errors\n"
        for error in errors:
            msg += error + "\n"
        settings_header = msg + '\n' + settings_header

    settings_src += (
        "}  // namespace Forscape\n"
    )

    diff_src += (
        "}  // namespace Forscape\n"
    )

    os.makedirs(os.path.dirname("../src/forscape_settings.cpp"), exist_ok=True)
    with open(f"../src/forscape_settings.cpp", "w", encoding="utf-8") as settings_src_file:
        settings_src_file.write(settings_src)

    os.makedirs(os.path.dirname("../include/forscape_settings.h"), exist_ok=True)
    with open(f"../include/forscape_settings.h", "w", encoding="utf-8") as settings_header_file:
        settings_header_file.write(settings_header)

    with open(f"../include/forscape_settings_diff.h", "w", encoding="utf-8") as diff_header_file:
        diff_header_file.write(diff_header)

    with open(f"../src/forscape_settings_diff.cpp", "w", encoding="utf-8") as diff_src_file:
        diff_src_file.write(diff_src)

    if len(errors) != 0:
        raise Exception(f"Codegen had errors: {errors}")


if __name__ == "__main__":
    main()
