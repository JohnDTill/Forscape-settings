#ifndef FORSCAPE_SETTINGS_DIFF_H
#define FORSCAPE_SETTINGS_DIFF_H

#include <stdint.h>
#include <string>
#include <string_view>
#include <vector>

namespace Forscape {

struct Settings;

struct SettingsDiff {
    /// Append a serialised representation of the SettingsDiff to a string
    void writeString(std::string& out) const;

    /// Deserialise a SettingsDiff from a string, writing errors for any invalidly specified settings
    static SettingsDiff fromString(std::string_view str, std::string& err_out);

private:
    std::vector<std::pair<uint8_t, uint8_t>> updates;
    friend Settings;
};

}  // namespace Forscape

#endif // FORSCAPE_SETTINGS_DIFF_H
