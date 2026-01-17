#ifndef FORSCAPE_SETTINGS_DIFF_DIALOG_H
#define FORSCAPE_SETTINGS_DIFF_DIALOG_H

#include <QDialog>
#include "forscape_settings_diff_dialog_codegen.h"

namespace Ui {
class SettingsDiffDialog;
}

class QCheckBox;
class QComboBox;
class QLabel;

namespace Forscape {

struct Settings;
struct SettingsDiff;

class SettingsDiffDialog : public QDialog {
    Q_OBJECT

public:
    static int exec(const Settings& inherited, SettingsDiff& diff);

    static SettingsDiffDialog& getDialog();

private:
    static SettingsDiffDialog* instance;
    explicit SettingsDiffDialog(QWidget* parent = nullptr);
    ~SettingsDiffDialog();

    void updatePalette();
    void updateInherited(const Settings& inherited);
    void updateDiff(const SettingsDiff& diff);

private slots:
    void updateChosenSetting();
    void updateFilters();

private:
    Ui::SettingsDiffDialog* ui;

    struct RowInfo {
        QLabel* label;
        QComboBox* box;
        std::vector<uint8_t> categories;
    };
    std::array<RowInfo, FORSCAPE_NUM_SETTINGS> rows;
    #undef FORSCAPE_NUM_SETTINGS

    std::array<QCheckBox*, FORSCAPE_NUM_SETTING_FILTERS> filters;
    #undef FORSCAPE_NUM_SETTING_FILTERS
};

}  // namespace Forscape

#endif // FORSCAPE_SETTINGS_DIFF_DIALOG_H
