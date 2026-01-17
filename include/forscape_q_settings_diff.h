#ifndef FORSCAPE_Q_SETTINGS_DIFF_H
#define FORSCAPE_Q_SETTINGS_DIFF_H

#include "forscape_settings_diff.h"
#include "forscape_settings_colour_palette.h"
class QColor;
class QString;

namespace Forscape {

struct QSettingsDiffRow {
    const QString& setting;
    const QString& option;
    const SettingOptionPalette& option_palette;

    QSettingsDiffRow(
        const QString& setting, const QString& option, const SettingOptionPalette& option_palette) noexcept;
};

/// SettingsDiff which exposes information necessary for visualising a diff construct
class QSettingsDiff : public SettingsDiff {
public:
    size_t size() const noexcept;
    std::pair<uint8_t, uint8_t> maxChars() const noexcept;
    QSettingsDiffRow getRowInfo(size_t index) const noexcept;
    const QString& getIdTooltip(size_t index) const noexcept;
    const QString& getOptionTooltip(size_t index) const noexcept;
};

}  // namespace Forscape

#endif // FORSCAPE_Q_SETTINGS_DIFF_H
