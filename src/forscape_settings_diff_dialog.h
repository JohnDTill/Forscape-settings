#ifndef FORSCAPE_SETTINGS_DIFF_DIALOG_H
#define FORSCAPE_SETTINGS_DIFF_DIALOG_H

#include <QDialog>

namespace Ui {
class SettingsDiffDialog;
}

class SettingsDiffDialog : public QDialog {

public:
    explicit SettingsDiffDialog(QWidget* parent = nullptr);
    ~SettingsDiffDialog();

private:
    Ui::SettingsDiffDialog* ui;
};

#endif // FORSCAPE_SETTINGS_DIFF_DIALOG_H
