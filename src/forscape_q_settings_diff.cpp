#include "forscape_q_settings_diff.h"

#include <cassert>
#include "forscape_settings_info.hpp"

namespace Forscape {

size_t QSettingsDiff::size() const noexcept {
    return updates.size();
}

std::pair<uint8_t, uint8_t> QSettingsDiff::maxChars() const noexcept {
    std::pair<uint8_t, uint8_t> max_chars = {0, 0};
    for(const auto update : updates){
        const std::pair<uint8_t, uint8_t> chars = charCount(update.first, update.second);
        max_chars.first = std::max(max_chars.first, chars.first);
        max_chars.second = std::max(max_chars.second, chars.second);
    }

    return max_chars;
}

QSettingsDiffRow QSettingsDiff::getRowInfo(size_t index) const noexcept {
    assert(index < size());
    const auto update = updates[index];
    return rowInfo(update.first, update.second);
}

const QString& QSettingsDiff::getIdTooltip(size_t index) const noexcept {
    assert(index < size());
    return setting_tooltips[updates[index].first];
}

const QString& QSettingsDiff::getOptionTooltip(size_t index) const noexcept {
    assert(index < size());
    const auto update = updates[index];
    return optionTooltip(update.first, update.second);
}

QSettingsDiffRow::QSettingsDiffRow(const QString& setting, const QString& option, const SettingOptionPalette& option_palette) noexcept
    : setting(setting), option(option), option_palette(option_palette) {}

}  // namespace Forscape
