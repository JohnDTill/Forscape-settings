#include "forscape_q_settings_diff.h"

#include <cassert>
#include "forscape_settings_info.hpp"

namespace Forscape {

size_t QSettingsDiff::size() const noexcept {
    return updates.size();
}

uint8_t QSettingsDiff::maxSettingChars() const noexcept {
    uint8_t max_chars = 0;
    for(const auto update : updates)
        max_chars = std::max(max_chars, static_cast<uint8_t>(setting_text[update.first].size()));

    return max_chars;
}

uint8_t QSettingsDiff::maxOptionChars() const noexcept {
    uint8_t max_chars = 0;
    for(const auto update : updates)
        max_chars = std::max(max_chars, static_cast<uint8_t>(option_text[update.second].size()));

    return max_chars;
}

QString QSettingsDiff::getSettingText(size_t row) const {
    return setting_text[updates[row].first];
}

QString QSettingsDiff::getOptionText(size_t row) const {
    return option_text[updates[row].second];
}

QString QSettingsDiff::getIdTooltip(size_t row) const {
    return setting_tooltips[updates[row].first];
}

QString QSettingsDiff::getOptionTooltip(size_t row) const {
    return option_tooltips[updates[row].second];
}

const SettingOptionPalette& QSettingsDiff::getPalette(size_t row) const noexcept {
    return rowPalette(updates[row].second);
}

}  // namespace Forscape
