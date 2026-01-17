# Forscape-Settings

![Screenshot of settings dialog](doc/settings_dialog_screenshot.png?raw=true "Taste the rainbow")

This is something fairly specific, split off to make Forscape development easier. I want numeric computation to be natural and use
standard syntax, without a lot of explicit type information or type suffix characters cluttering things up. I want the same for
symbolic computation. For example there is a fundamental decision between interpreting `√(2)` as a symbolic expression requiring an AST,
or as merely an operation on a float resulting in `1.414214`. I want to keep IDE interaction natural by making typing optional,
so `√(sym(2))` or `√(2.0f)` aren't my preferred solution. That neccesitates some way of specifying how the current environment interprets things.

This could be done with a construct- e.g. *things in this block will be interpreted under a symbolic context*. I feel like that's
limiting and not granular enough, so my thought for now is to make the compiler settings lexically scoped, with a construct
that changes the settings. You can interact with a settings-update construct using a form dialog, which will display all
available settings and their options.

I don't know if that's a great solution; it's definitely an experiment. It's unclear how often you'll wish you could define settings at a project level, or pass settings information to library functions.

The reason for this repo is that while the ideas aren't terribly complicated, it is enough complexity that following and reasoning about the settings logic is difficult amongst all the clutter of the Forscape repo. The settings are an independent mechanism, so separating them out is easy.

[![C++ Tests](https://github.com/JohnDTill/Forscape-settings/actions/workflows/cpp_integration_tests.yml/badge.svg)](https://github.com/JohnDTill/Forscape-settings/actions/workflows/cpp_integration_tests.yml)

## License

This example repo is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
