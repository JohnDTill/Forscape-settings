#ifndef FORSCAPE_SETTINGS_DIFF_DIALOG_H
#define FORSCAPE_SETTINGS_DIFF_DIALOG_H

#include <QDialog>

// TODO:
//   * Visualise the combination of SettingsDiff and Settings (all the Settings gives you is inherited values)
//   * Allow editing with filter options and search

// TODO: method to draw and report size of a diff as it will be shown in the Construct

class SettingsDiffDialog : public QDialog {
public:
    SettingsDiffDialog(QWidget* parent = nullptr);
    ~SettingsDiffDialog();
};

#endif // FORSCAPE_SETTINGS_DIFF_DIALOG_H
