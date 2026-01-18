from collections import OrderedDict
import json
from math import ceil, log2
import os
from pathlib import Path
import re
from textwrap import wrap
import xml.etree.ElementTree as ET


def get_definition():
    with open('settings_definition.json', encoding='utf-8') as settings_def_file:
        settings_def = json.load(settings_def_file)
        return settings_def
    

def grammatically_correct_title(val):
    return val.title(
        ).replace("On ", "on "
        ).replace("To ", "to ")


def to_snake(val):
    return val.strip().replace(' ', '_').replace('-', '_').lower()


def vartitle(val):
    return re.sub(r'\W+', '', val.title())


def generate_settings(root, settings):
    override_form = root.findall('.//layout[@name="overriddenFormLayout"]')[0]
    for child in list(override_form):
        override_form.remove(child)

    settings_form = root.findall('.//layout[@name="inheritedFormLayout"]')[0]
    for child in list(settings_form):
        settings_form.remove(child)

    for idx, (setting, setting_values) in enumerate(settings.items()):
        # Label
        label_item = ET.SubElement(settings_form, "item", {"row": f"{idx}", "column": "0"})
        label = ET.SubElement(label_item, "widget", {"class": "QLabel", "name": f"settingLabel{idx}"})
        label_tooltip = ET.SubElement(label, "property", {"name": "toolTip"})
        label_tooltip_str = ET.SubElement(label_tooltip, "string")
        label_tooltip_str.text = setting_values["brief"] + "\n\n" + '\n'.join(wrap(setting_values["long"], width=60)) + "\n\nCategories: " + str(setting_values["categories"])
        label_text = ET.SubElement(label, "property", {"name": "text"})
        label_text_str = ET.SubElement(label_text, "string")
        label_text_str.text = grammatically_correct_title(setting) + ": "

        # ComboBox
        box_item = ET.SubElement(settings_form, "item", {"row": f"{idx}", "column": "1"})
        box = ET.SubElement(box_item, "widget", {"class": "QComboBox", "name": f"settingComboBox{idx}"})
        for option in ["Inherit", *setting_values["options"]]:
            option_item = ET.SubElement(box, "item")
            option_text = ET.SubElement(option_item, "property", {"name": "text"})
            option_text_str = ET.SubElement(option_text, "string")
            option_text_str.text = grammatically_correct_title(option)


def generate_filters(root, filters):
    filter_layout = root.findall('.//layout[@name="filterLayout"]')[0]
    spacer = list(filter_layout)[-1]
    for child in list(filter_layout)[1:]:
        filter_layout.remove(child)

    for idx, filter in enumerate(filters):
        item = ET.SubElement(filter_layout, "item")
        widget = ET.SubElement(item, "widget", {"class": "QCheckBox", "name": f"filterCheckBox{idx}"})
        property = ET.SubElement(widget, "property", {"name": "text"})
        string = ET.SubElement(property, "string")
        string.text = filter

    filter_layout.append(spacer)


def write_source_files(settings, options, categories, setting_typedef, options_typedef):
    source_file = (
        "#include \"forscape_settings_diff_dialog.h\"\n"
        "#include \"ui_forscape_settings_diff_dialog.h\"\n"
        "\n"
        "#include \"forscape_settings.h\"\n"
        "#include \"forscape_settings_colour_palette.h\"\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
    )

    max_options = max([len(setting["options"]) for setting in settings.values()])

    # Constructor
    source_file += (
        "SettingsDiffDialog::SettingsDiffDialog(QWidget* parent)\n"
        "    : QDialog(parent), ui(new Ui::SettingsDiffDialog) {\n"
        "    ui->setupUi(this);\n"
        "\n"
    )
    for idx, setting_values in enumerate(settings.values()):
        source_file += f"    rows[{idx}].box = ui->settingComboBox{idx};\n"
        source_file += f"    rows[{idx}].label = ui->settingLabel{idx};\n"
        source_file += f"    rows[{idx}].categories = {{{','.join([str(categories[category.strip().title()]) for category in setting_values['categories']])}}};\n"
        # source_file += f"    ui->settingComboBox{idx}->setItemData(0, \"Maintain the previous setting.\", Qt::ToolTipRole);\n"
        for option_idx, option in enumerate(setting_values["options"]):
            option = options[option]
            tooltip = '\\n'.join(wrap(option['description'], width=60)).replace('"', '\\"')
            source_file += f"    ui->settingComboBox{idx}->setItemData({option_idx+1}, \"{{}}\", Qt::ToolTipRole);\n".format(tooltip)
    source_file += '\n'
    for idx, setting_values in enumerate(settings.values()):
        source_file += f"    connect(ui->settingComboBox{idx}, SIGNAL(currentIndexChanged(int)), this, SLOT(updateChosenSetting()));\n"

    source_file += (
        "\n"
        "    connect(ui->filterEdit, SIGNAL(textChanged(const QString&)), this, SLOT(updateFilters()));\n"
    )
    for idx in range(len(categories)):
        source_file += f"    connect(ui->filterCheckBox{idx}, SIGNAL(checkStateChanged(Qt::CheckState)), this, SLOT(updateFilters()));\n"
        source_file += f"    filters[{idx}] = ui->filterCheckBox{idx};\n"

    source_file += (
        "}\n"
        "\n"
    )

    # Palette update
    source_file += (
        "void SettingsDiffDialog::updatePalette() {\n"
        "    const SettingsPalettes& palette = getSettingsColourPalette();\n"
    )
    for setting_idx, setting_values in enumerate(settings.values()):
        for option_idx, option in enumerate(setting_values["options"]):
            colour = to_snake(options[option]["colour_role"])
            source_file += (
                f"    assert(palette.{colour}.foreground.alpha());  // Verify the palette was initialised\n"
                f"    assert(palette.{colour}.background.alpha());  // Verify the palette was initialised\n"
                f"    ui->settingComboBox{setting_idx}->setItemData({option_idx+1}, palette.{colour}.foreground, Qt::ItemDataRole::ForegroundRole);\n"
                f"    ui->settingComboBox{setting_idx}->setItemData({option_idx+1}, palette.{colour}.background, Qt::ItemDataRole::BackgroundRole);\n"
            )
    source_file += (
        "}\n"
        "\n"
    )

    # Maps
    source_file += (
        f"inline constexpr std::array<std::array<{options_typedef}, {max_options}>, {len(settings)}> option_local_to_global {{\n"
    )
    for setting_idx, setting_values in enumerate(settings.values()):
        source_file += f"    std::array<{options_typedef}, {max_options}>({{"
        for option_idx, option in enumerate(setting_values["options"]):
            source_file += f"{options[option]['index']},"
        source_file += "}),\n"
    source_file += "};\n\n"

    source_file += (
        f"template<{setting_typedef} setting>"
        f"inline constexpr {options_typedef} optionGlobalToLocal({options_typedef} global_option) noexcept {{\n"
        f"    if(option_local_to_global[setting][0] == global_option) return 0;\n"
    )
    for i in range(1, max_options-1):
        source_file += f"    else if(option_local_to_global[setting][{i}] == global_option) return {i};\n"
    source_file += (
        f"    assert(option_local_to_global[setting][{max_options-1}] == global_option);\n"
        f"    return {max_options-1};\n"
        "}\n"
        "\n"
    )

    source_file += (
        f"inline constexpr {options_typedef} optionGlobalToLocal({setting_typedef} setting, {options_typedef} global_option) noexcept {{\n"
        f"    if(option_local_to_global[setting][0] == global_option) return 0;\n"
    )
    for i in range(1, max_options-1):
        source_file += f"    else if(option_local_to_global[setting][{i}] == global_option) return {i};\n"
    source_file += (
        f"    assert(option_local_to_global[setting][{max_options-1}] == global_option);\n"
        f"    return {max_options-1};\n"
        "}\n"
        "\n"
    )

    # Inherited settings update
    source_file += (
        "void SettingsDiffDialog::updateInherited(const Settings& inherited) {\n"
    )
    for setting_idx, (setting, setting_values) in enumerate(settings.items()):
        source_file += (
            f"    const int inherited{setting_idx} = 1 + optionGlobalToLocal<{setting_idx}>(static_cast<int>(inherited.get{vartitle(setting)}Option()));\n"
            # f"    const QColor foreground_colour{setting_idx} = ui->settingComboBox{setting_idx}->itemData(inherited{setting_idx}, Qt::ItemDataRole::ForegroundRole).value<QColor>();\n"
            # f"    ui->settingComboBox{setting_idx}->setItemData(0, foreground_colour{setting_idx}.darker(110), Qt::ItemDataRole::ForegroundRole);\n"
            f"    const QColor background_colour{setting_idx} = ui->settingComboBox{setting_idx}->itemData(inherited{setting_idx}, Qt::ItemDataRole::BackgroundRole).value<QColor>();\n"
            f"    ui->settingComboBox{setting_idx}->setItemData(0, background_colour{setting_idx}.lighter(150), Qt::ItemDataRole::BackgroundRole);\n"
            f"    const QString tooltip{setting_idx} = \"Maintain the previous setting:\\n\" + \n"
            f"        ui->settingComboBox{setting_idx}->itemData(inherited{setting_idx}, Qt::ItemDataRole::ToolTipRole).toString();\n"
            f"    ui->settingComboBox{setting_idx}->setItemData(0, tooltip{setting_idx}, Qt::ItemDataRole::ToolTipRole);\n"
            f"    ui->settingComboBox{setting_idx}->setItemText(0, \"Inherit - \" + ui->settingComboBox{setting_idx}->itemText(inherited{setting_idx}));\n"
        )
    source_file += (
        "}\n"
        "\n"
    )

    source_file += (
        "}  // namespace Forscape\n"
    )

    with open(f"../src/forscape_settings_diff_dialog_codegen.cpp", "w", encoding="utf-8") as ui_src_file:
        ui_src_file.write(source_file)


def write_header_file(settings, options, filters):
    header_file = (
        "#ifndef FORSCAPE_SETTING_DIFF_DIALOG_CODEGEN_H\n"
        "#define FORSCAPE_SETTING_DIFF_DIALOG_CODEGEN_H\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
    )

    header_file += (
        f"#define FORSCAPE_NUM_SETTINGS {len(settings)}\n"
        f"#define FORSCAPE_NUM_SETTING_FILTERS {len(filters)}\n"
        "\n"
    )

    header_file += (
        "}  // namespace Forscape\n"
        "\n"
        "#endif  // #ifndef FORSCAPE_SETTING_DIFF_DIALOG_CODEGEN_H\n"
    )

    with open(f"../include/forscape_settings_diff_dialog_codegen.h", "w", encoding="utf-8") as ui_src_file:
        ui_src_file.write(header_file)


def write_palette_header(colour_roles):
    header_file = (
        "#ifndef FORSCAPE_SETTING_COLOUR_PALETTE_H\n"
        "#define FORSCAPE_SETTING_COLOUR_PALETTE_H\n"
        "\n"
        "#include <QColor>\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
        "#ifndef NDEBUG\n"
        "#define DEBUG_INIT_SETTING_OPTION_PALETTE =QColor(0, 0, 0, 0)  /* Allow detection of unitialised palettes */\n"
        "#else\n"
        "#define DEBUG_INIT_SETTING_OPTION_PALETTE\n"
        "#endif\n"
        "\n"
        "/// Colours to use for each settings role\n"
        "struct SettingOptionPalette {\n"
        "    QColor foreground DEBUG_INIT_SETTING_OPTION_PALETTE;\n"
        "    QColor background DEBUG_INIT_SETTING_OPTION_PALETTE;\n"
        "};\n"
        "\n"
    )

    # Write colour definitions
    header_file += (
        "/// Colours of all settings\n"
        "struct SettingsPalettes {\n"
    )
    for colour_role in colour_roles:
        header_file += f"    SettingOptionPalette {colour_role};\n"
    header_file += (
        "};\n"
        "\n"
    )

    header_file += (
        "/// Change the colours used to display settings\n"
        "void setSettingsColourPalette(const SettingsPalettes& palette) noexcept;\n"
        "\n"
        "/// Get the colours used to display settings\n"
        "const SettingsPalettes& getSettingsColourPalette() noexcept;\n"
        "\n"
    )

    header_file += (
        "}  // namespace Forscape\n"
        "\n"
        "#endif  // #ifndef FORSCAPE_SETTING_COLOUR_PALETTE_H\n"
    )

    with open(f"../include/forscape_settings_colour_palette.h", "w", encoding="utf-8") as ui_src_file:
        ui_src_file.write(header_file)


def write_palette_source(settings, options):
    src = (
        "#include \"forscape_settings_colour_palette.h\"\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
        "static SettingsPalettes global_palette;\n"
        "\n"
    )

    src += (
        "void setSettingsColourPalette(const SettingsPalettes& palette) noexcept {\n"
        "    global_palette = palette;\n"
    )
    for setting_values in settings.values():
        for option in setting_values["options"]:
            colour = to_snake(options[option]["colour_role"])
            src += (
                f"    assert(palette.{colour}.foreground.alpha());  // Verify the palette was initialised\n"
                f"    assert(palette.{colour}.background.alpha());  // Verify the palette was initialised\n"
            )
    src += "}\n\n"

    src += (
        "const SettingsPalettes& getSettingsColourPalette() noexcept {\n"
        "    return global_palette;\n"
        "}\n\n"
    )

    src += (
        "}  // namespace Forscape\n"
    )

    with open("../src/forscape_settings_colour_palette.cpp", "w", encoding="utf-8") as ui_src_file:
        ui_src_file.write(src)


def write_info(settings, options, colour_roles, setting_typedef, options_typedef):
    src = (
        "#include <QString>\n"
        "\n"
        "#include \"forscape_settings_colour_palette.h\"\n"
        "\n"
        "namespace Forscape {\n"
        "\n"
    )

    src += (
        f"typedef {setting_typedef} SettingsId;\n"
        f"typedef {options_typedef} SettingsOption;\n"
        "\n"
        f"inline constexpr std::array<QLatin1StringView, {len(settings)}> setting_text {{\n"
    )
    for setting in settings:
        src += f"    QLatin1StringView(\"{grammatically_correct_title(setting)}\"),\n"
    src += "};\n\n"

    src += f"inline constexpr std::array<QLatin1StringView, {len(options)}> option_text {{\n"
    for option in options:
        src += f"    QLatin1StringView(\"{grammatically_correct_title(option)}\"),\n"
    src += "};\n\n"

    src += (
        "const SettingOptionPalette& rowPalette(SettingsOption option) noexcept {\n"
        "    switch(option){\n"
    )
    for option_idx, (option, option_vals) in enumerate(options.items()):
        src += (
            f"        case {option_idx}: return getSettingsColourPalette().{to_snake(option_vals['colour_role'])};\n"
        )
    src += (
        "    }\n"
        "}\n"
        "\n"
    )

    # Setting ID tooltip
    src += (
        f"inline constexpr std::array<QLatin1StringView, {len(settings)}> setting_tooltips {{\n"
    )
    for setting_vals in settings.values():
        tooltip = setting_vals['brief'].replace('"', '\\"')
        src += f"    QLatin1StringView(\"{tooltip}\"),\n"
    src += "};\n\n"

    # Option tooltip
    src += (
        f"inline constexpr std::array<QLatin1StringView, {len(options)}> option_tooltips {{\n"
    )
    for option in options.values():
        tooltip = '\\n'.join(wrap(option['description'], width=60)).replace('"', '\\"')
        src += f"    QLatin1StringView(\"{tooltip}\"),\n"
    src += "};\n\n"

    src += (
        "}  // namespace Forscape\n"
    )

    with open("../src/forscape_settings_info.hpp", "w", encoding="utf-8") as ui_src_file:
        ui_src_file.write(src)


def main():
    inputs = [
        Path("forscape_settings_diff_dialog.ui"),
        Path("settings_definition.json"),
        Path("codegen_ui.py"),
    ]

    outputs = [
        Path("../src/forscape_settings_diff_dialog_codegen.cpp"),
        Path("../include/forscape_settings_diff_dialog_codegen.h"),
        Path("../src/forscape_settings_diff_dialog.ui"),
        Path("../src/forscape_settings_colour_palette.cpp"),
        Path("../include/forscape_settings_colour_palette.h"),
        Path("../src/forscape_settings_info.hpp"),
    ]

    if all([path.is_file() for path in outputs]) and max([os.path.getmtime(path) for path in inputs]) < min([os.path.getmtime(path) for path in outputs]):
        print("Skipping settings UI code generation since outputs are more recent than source files")
        return

    settings_def = get_definition()
    options = OrderedDict(sorted(settings_def["options"].items()))
    settings = OrderedDict(sorted(settings_def["compiler_settings"].items()))

    num_settings_bits = ceil(log2(len(settings)))
    num_options_bits = ceil(log2(len(options)))
    setting_typedef = "uint8_t" if num_settings_bits <= 8 else "uint16_t"
    options_typedef = "uint8_t" if num_options_bits <= 8 else "uint16_t"

    for idx, option in enumerate(options):
        options[option]["index"] = idx

    filters = set()
    for setting_values in settings.values():
        for category in setting_values["categories"]:
            filters.add(category.strip().title())
    filters = {filter: idx for idx, filter in enumerate(sorted(list(filters)))}

    colour_roles = set()
    for option_vals in options.values():
        colour_roles.add(to_snake(option_vals["colour_role"]))

    ui = ET.parse('forscape_settings_diff_dialog.ui')
    root = ui.getroot()

    generate_settings(root, settings)
    generate_filters(root, filters)

    ET.indent(ui, space=" ", level=0)
    ui.write("../src/forscape_settings_diff_dialog.ui", encoding="UTF-8", xml_declaration=True)

    write_source_files(settings, options, filters, setting_typedef, options_typedef)
    write_header_file(settings, options, filters)
    write_palette_header(colour_roles)
    write_palette_source(settings, options)
    write_info(settings, options, colour_roles, setting_typedef, options_typedef)


if __name__ == "__main__":
    main()
