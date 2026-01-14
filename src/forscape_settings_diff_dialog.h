#ifndef FORSCAPE_SETTINGS_DIFF_DIALOG_H
#define FORSCAPE_SETTINGS_DIFF_DIALOG_H

#include <QDialog>

namespace Ui {
class SettingsDiffDialog;
}

namespace Forscape {

struct Settings;
struct SettingsDiff;

class SettingsDiffDialog : public QDialog {
    Q_OBJECT

public:
    explicit SettingsDiffDialog(QWidget* parent = nullptr);
    ~SettingsDiffDialog();

    // TODO: make a way to change the settings
    static void show(const Settings& inherited, SettingsDiff& diff, size_t some_colour_info);

private slots:
    void updateChosenSetting();

private:
    Ui::SettingsDiffDialog* ui;
};

}  // namespace Forscape

#endif // FORSCAPE_SETTINGS_DIFF_DIALOG_H
