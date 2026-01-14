#include "forscape_settings_diff_dialog.h"

#include <QApplication>

int main(int argc, char* argv[]){
    QApplication a(argc, argv);

    Forscape::SettingsDiffDialog dialog;
    dialog.exec();

    const auto code = a.exec();

    return code;
}
