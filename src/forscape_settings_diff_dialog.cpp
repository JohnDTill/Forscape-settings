#include "forscape_settings_diff_dialog.h"
#include "ui_forscape_settings_diff_dialog.h"

namespace Forscape {

SettingsDiffDialog::SettingsDiffDialog(QWidget* parent)
    : QDialog(parent), ui(new Ui::SettingsDiffDialog) {
    ui->setupUi(this);

    // TODO: setup the setting option tooltips
    // combo_box->setItemData(0, "Maintain the previous setting", Qt::ToolTipRole);
    // for(int i = 0; i < NUM_WARNING_LEVELS; i++)
    //     combo_box->setItemData(i+1, warning_descriptions[i].data(), Qt::ToolTipRole);
}

SettingsDiffDialog::~SettingsDiffDialog() {
    delete ui;
}

/*
    if(instance == nullptr) instance = new SettingsDialog;

    //Set colour coding
    background_colour[0] = instance->palette().color(QPalette::ColorRole::Base);
    background_colour[1+NO_WARNING] = Typeset::getColour(Typeset::COLOUR_HIGHLIGHTSECONDARY);
    background_colour[1+WARN] = Typeset::getColour(Typeset::COLOUR_WARNINGBACKGROUND);
    background_colour[1+ERROR] = Typeset::getColour(Typeset::COLOUR_ERRORBACKGROUND);
    text_colour[0] = instance->palette().color(QPalette::ColorRole::Text);
    text_colour[1+NO_WARNING] = Typeset::getColour(Typeset::COLOUR_TEXT);
    text_colour[1+WARN] = Typeset::getColour(Typeset::COLOUR_ID);
    text_colour[1+ERROR] = Typeset::getColour(Typeset::COLOUR_ID);
    for(QComboBox* combo_box : combo_boxes){
        for(int i = 0; i < NUM_WARNING_LEVELS+1; i++){
            combo_box->setItemData(i, background_colour[i], Qt::ItemDataRole::BackgroundRole);
            combo_box->setItemData(i, text_colour[i], Qt::ItemDataRole::ForegroundRole);
        }
    }

    //Set active index for each entry
    for(QComboBox* combo_box : combo_boxes){
        combo_box->setFocus();
        combo_box->setCurrentIndex(0);
    }
    for(const Code::Settings::Update& update : settings){
        combo_boxes[update.setting_id]->setFocus();
        combo_boxes[update.setting_id]->setCurrentIndex( update.prev_value + 1 );
    }

    const auto user_response = instance->exec();
    if(user_response != QDialog::Accepted) return false;

    std::vector<Code::Settings::Update> altered_settings;
    populateSettingsFromForm(altered_settings);

    return (altered_settings.size() != settings.size()) ||
           !std::equal(settings.begin(), settings.end(), altered_settings.begin());
*/

void SettingsDiffDialog::updateChosenSetting() {
    // QComboBox* combo_box = debug_cast<QComboBox*>(focusWidget());  // TODO
    QComboBox* combo_box = reinterpret_cast<QComboBox*>(focusWidget());
    const auto current_index = combo_box->currentIndex();

    //EVENTUALLY: this hack may not be necessary
    // combo_box->setStyleSheet("QComboBox { background: " + background_colour[current_index].name() + "; }");

    // TODO: update palette
    QPalette palette = combo_box->palette();
    // palette.setColor(combo_box->backgroundRole(), background_colour[current_index]);
    // palette.setColor(QPalette::ColorRole::Text, text_colour[current_index]);
    combo_box->setPalette(palette);

    // TODO: any tooltip update

    setFocus();
}

}  // namespace Forscape
