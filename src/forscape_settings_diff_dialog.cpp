#include "forscape_settings_diff_dialog.h"
#include "ui_forscape_settings_diff_dialog.h"

SettingsDiffDialog::SettingsDiffDialog(QWidget* parent)
    : QDialog(parent), ui(new Ui::SettingsDiffDialog) {
    ui->setupUi(this);
}

SettingsDiffDialog::~SettingsDiffDialog() {
    delete ui;
}
