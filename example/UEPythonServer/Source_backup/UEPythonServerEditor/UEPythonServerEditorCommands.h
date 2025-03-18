#pragma once

#include "CoreMinimal.h"
#include "Framework/Commands/Commands.h"
#include "UEPythonServerEditorStyle.h"

class FUEPythonServerEditorCommands : public TCommands<FUEPythonServerEditorCommands>
{
public:
    FUEPythonServerEditorCommands()
        : TCommands<FUEPythonServerEditorCommands>(TEXT("UEPythonServerEditor"), NSLOCTEXT("Contexts", "UEPythonServerEditor", "UEPythonServer Plugin"), NAME_None, FUEPythonServerEditorStyle::GetStyleSetName())
    {
    }

    // TCommands<> interface
    virtual void RegisterCommands() override;

public:
    TSharedPtr<FUICommandInfo> OpenPluginWindow;
}; 