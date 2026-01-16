import json
from textwrap import wrap
import xml.etree.ElementTree as ET


def get_definition():
    with open('settings_definition.json', encoding='utf-8') as settings_def_file:
        settings_def = json.load(settings_def_file)
        return settings_def
    

def grammatically_correct_title(val):
    return val.title(
        ).replace("On", "on"
        ).replace("To", "to")


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
        label_text_str.text = setting.strip().title() + ": "

        # ComboBox
        box_item = ET.SubElement(settings_form, "item", {"row": f"{idx}", "column": "1"})
        box = ET.SubElement(box_item, "widget", {"class": "QComboBox", "name": f"settingComboBox{idx}"})
        for option in ["Inherit", *setting_values["options"]]:
            option_item = ET.SubElement(box, "item")
            option_text = ET.SubElement(option_item, "property", {"name": "text"})
            option_text_str = ET.SubElement(option_text, "string")
            option_text_str.text = grammatically_correct_title(option)


def generate_filters(root, settings):
    filters = set()
    for setting_values in settings.values():
        for category in setting_values["categories"]:
            filters.add(category.strip().title())
    filters = sorted(list(filters))

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

def main():
    settings_def = get_definition()
    options = settings_def["options"]
    settings = settings_def["compiler_settings"]

    ui = ET.parse('forscape_settings_diff_dialog.ui')
    root = ui.getroot()

    generate_settings(root, settings)
    generate_filters(root, settings)

    ET.indent(ui, space=" ", level=0)
    ui.write("../src/forscape_settings_diff_dialog.ui", encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    main()
