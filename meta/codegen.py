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
        "#include <stdint.h>\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
        "struct Settings;\n"
        "\n"
        "/// Get default settings before any user overrides\n"
        "const Settings& getDefaultSettings() noexcept;\n"
        "\n"
    )

    src = (
        "#include \"forscape_settings.h\"\n"
        "\n"
        "#include <array>\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
        f"constexpr size_t NUM_COMPILER_SETTINGS = {len(settings_def['compiler_settings'])};\n"
        "\n"
        "struct Settings {\n"
        "    std::array<uint8_t, NUM_COMPILER_SETTINGS> compiler_settings;\n"
        "};\n"
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
        header += "};\n"
        header += f"{vartitle(compiler_setting)}Option get{vartitle(compiler_setting)}Option(const Settings& settings) noexcept;\n\n"

    # Write default settings
    src += (
        "constexpr Settings DEFAULT_SETTINGS = {{\n"
    )
    for compiler_setting, compiler_setting_vals in settings_def["compiler_settings"].items():
        if compiler_setting_vals["default"] in compiler_setting_vals["options"]:
            src += f"    static_cast<uint8_t>({vartitle(compiler_setting)}Option::{varupper(compiler_setting_vals['default'])}),\n"
        else:
            errors += f"Default {compiler_setting_vals['default']} is not an option of {compiler_setting}"
    src += "}};\n\n"

    src += (
        "const Settings& getDefaultSettings() noexcept {\n"
        "    return DEFAULT_SETTINGS;\n"
        "}\n\n"
    )

    # Write getter functions
    for idx, (compiler_setting, compiler_setting_vals) in enumerate(settings_def["compiler_settings"].items()):
        src += (
            f"{vartitle(compiler_setting)}Option get{vartitle(compiler_setting)}Option(const Settings& settings) noexcept {{\n"
            f"    return static_cast<{vartitle(compiler_setting)}Option>(settings.compiler_settings[{idx}]);\n"
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
