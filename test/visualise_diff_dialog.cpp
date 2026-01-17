#include "forscape_settings_diff_dialog.h"

#include "forscape_settings.h"
#include "forscape_settings_diff.h"

#include <QApplication>
#include <iostream>

int main(int argc, char* argv[]){
    QApplication application(argc, argv);

    Forscape::Settings settings = Forscape::Settings::getDefaults();
    Forscape::SettingsDiff diff = Forscape::SettingsDiff::fromString(
        "UnusedVariable=Error,ScopeShadowing=Warn,TransposeT=Ignore,IrrationalConversion=FullSymbolic");

    Forscape::SettingsPalettes palette;
    palette.allow.background = QColor("limegreen");
    palette.allow.foreground = QColor("black");
    palette.semi_allow.background = QColor("mediumspringgreen");
    palette.semi_allow.foreground = QColor("black");
    palette.error.background = QColor("tomato");
    palette.error.foreground = QColor("white");
    palette.ignore.background = QColor("gainsboro");
    palette.ignore.foreground = QColor("black");
    palette.warn.background = QColor("orange");
    palette.warn.foreground = QColor("black");

    Forscape::SettingsDiffDialog::exec(settings, diff, palette);

    std::string diff_str;
    diff.writeString(diff_str);
    std::cout << "Diff on exit: " << diff_str << std::endl;

    return 0;
}
