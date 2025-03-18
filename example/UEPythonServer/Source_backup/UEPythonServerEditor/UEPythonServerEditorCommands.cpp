#include "UEPythonServerEditorCommands.h"

#define LOCTEXT_NAMESPACE "FUEPythonServerEditorModule"

void FUEPythonServerEditorCommands::RegisterCommands()
{
    UI_COMMAND(OpenPluginWindow, "UE Python Server", "Open the UE Python Server window", EUserInterfaceActionType::Button, FInputChord());
}

#undef LOCTEXT_NAMESPACE 