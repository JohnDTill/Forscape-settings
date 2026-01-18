#ifndef FORSCAPE_Q_SETTINGS_DIFF_H
#define FORSCAPE_Q_SETTINGS_DIFF_H

#include "forscape_settings_diff.h"
#include "forscape_settings_colour_palette.h"
class QColor;
class QString;

namespace Forscape {

/// SettingsDiff which exposes information necessary for visualising a diff construct
class QSettingsDiff : public SettingsDiff {
public:
    size_t size() const noexcept;
    uint8_t maxSettingChars() const noexcept;
    uint8_t maxOptionChars() const noexcept;
    QString getSettingText(size_t row) const;
    QString getOptionText(size_t row) const;
    QString getIdTooltip(size_t row) const;
    QString getOptionTooltip(size_t row) const;
    const SettingOptionPalette& getPalette(size_t row) const noexcept;
};

}  // namespace Forscape

#endif // FORSCAPE_Q_SETTINGS_DIFF_H
