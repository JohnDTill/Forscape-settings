#include "forscape_settings_diff_dialog.h"
#include "ui_forscape_settings_diff_dialog.h"

#include "forscape_settings_diff.h"

namespace Forscape {

SettingsDiffDialog* SettingsDiffDialog::instance = nullptr;

int SettingsDiffDialog::exec(const Settings& inherited, SettingsDiff& diff, const SettingsPalettes& palette) {
    SettingsDiffDialog& dialog = getDialog();
    dialog.updatePalette(palette);
    dialog.updateInherited(inherited);
    dialog.updateDiff(diff);

    const auto user_response = dialog.exec();
    if(user_response != QDialog::Accepted) return user_response;

    diff.updates.clear();
    for(size_t i = 0; i < dialog.rows.size(); i++){
        const auto row = dialog.rows[i];
        const auto index = row.box->currentIndex();
        if(index != 0) diff.updates.push_back({i, index-1});
    }

    return user_response;
}

SettingsDiffDialog& SettingsDiffDialog::getDialog() {
    if(instance == nullptr) instance = new SettingsDiffDialog;
    return *instance;
}

SettingsDiffDialog::~SettingsDiffDialog() {
    delete ui;
}

void SettingsDiffDialog::updateDiff(const SettingsDiff& diff) {
    for(const auto entry : diff.updates){
        const auto& row = rows[entry.first];
        row.box->setCurrentIndex(entry.second + 1);
    }

    for(const auto row : rows) {
        row.box->setToolTip(row.box->itemData(row.box->currentIndex(), Qt::ItemDataRole::ToolTipRole).toString());

        QPalette palette = row.box->palette();

        const QColor background = row.box->itemData(row.box->currentIndex(), Qt::ItemDataRole::BackgroundRole).value<QColor>();
        // The commented line is not effective on all platforms; use style sheet
        // palette.setColor(row.box->backgroundRole(), background);
        row.box->setStyleSheet("QComboBox { background: " + background.name() + "; }");

        const QColor foreground = row.box->itemData(row.box->currentIndex(), Qt::ItemDataRole::ForegroundRole).value<QColor>();
        palette.setColor(QPalette::ColorRole::Text, foreground);

        row.box->setPalette(palette);
    }
}

void SettingsDiffDialog::updateChosenSetting() {
    QComboBox* combo_box = reinterpret_cast<QComboBox*>(sender());
    const auto current_index = combo_box->currentIndex();

    combo_box->setToolTip(combo_box->itemData(combo_box->currentIndex(), Qt::ItemDataRole::ToolTipRole).toString());

    QPalette palette = combo_box->palette();

    const QColor background = combo_box->itemData(combo_box->currentIndex(), Qt::ItemDataRole::BackgroundRole).value<QColor>();
    // The commented line is not effective on all platforms; use style sheet
    // palette.setColor(row.box->backgroundRole(), background);
    combo_box->setStyleSheet("QComboBox { background: " + background.name() + "; }");

    const QColor foreground = combo_box->itemData(combo_box->currentIndex(), Qt::ItemDataRole::ForegroundRole).value<QColor>();
    palette.setColor(QPalette::ColorRole::Text, foreground);

    combo_box->setPalette(palette);

    size_t index = 0;
    ui->inheritedFormLayout->insertRow(index++, ui->overriddenLabel);
    for(const auto row : rows){
        if(row.box->currentIndex() == 0) continue;
        ui->inheritedFormLayout->insertRow(index++, row.label, row.box);
        index++;
    }
    ui->inheritedFormLayout->insertRow(index++, ui->inheritedLabel);
    for(const auto row : rows){
        if(row.box->currentIndex() != 0) continue;
        ui->inheritedFormLayout->insertRow(index++, row.label, row.box);
        index++;
    }
}

void SettingsDiffDialog::updateFilters() {
    for(const auto row : rows){
        row.box->setVisible(true);
        row.label->setVisible(true);
    }

    const QString search_term = ui->filterEdit->text();
    if(!search_term.isEmpty()){
        for(const auto row : rows){
            const bool contains_term = row.label->text().contains(search_term, Qt::CaseInsensitive);
            row.box->setVisible(contains_term);
            row.label->setVisible(contains_term);
        }
    }

    for(size_t i = 0; i < filters.size(); i++){
        const QCheckBox* filter = filters[i];
        if(!filter->isChecked()) continue;

        for(const auto row : rows){
            const bool contains_category = row.categories.cend() !=
                std::find(row.categories.cbegin(), row.categories.cend(), i);
            if(contains_category) continue;
            row.box->setVisible(false);
            row.label->setVisible(false);
        }
    }
}

}  // namespace Forscape
