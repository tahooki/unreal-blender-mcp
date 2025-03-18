#include "UEPythonServerEditor.h"
#include "UEPythonServerEditorStyle.h"
#include "UEPythonServerEditorCommands.h"
#include "LevelEditor.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Text/STextBlock.h"
#include "ToolMenus.h"

static const FName UEPythonServerTabName("UEPythonServer");

#define LOCTEXT_NAMESPACE "FUEPythonServerEditorModule"

void FUEPythonServerEditorModule::StartupModule()
{
    UE_LOG(LogTemp, Display, TEXT("UEPythonServerEditor: Starting module..."));
    
    // This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module
    
    FUEPythonServerEditorStyle::Initialize();
    FUEPythonServerEditorStyle::ReloadTextures();

    FUEPythonServerEditorCommands::Register();
    
    PluginCommands = MakeShareable(new FUICommandList);

    PluginCommands->MapAction(
        FUEPythonServerEditorCommands::Get().OpenPluginWindow,
        FExecuteAction::CreateRaw(this, &FUEPythonServerEditorModule::PluginButtonClicked),
        FCanExecuteAction());

    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FUEPythonServerEditorModule::RegisterMenus));
    
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner(UEPythonServerTabName, FOnSpawnTab::CreateRaw(this, &FUEPythonServerEditorModule::OnSpawnPluginTab))
        .SetDisplayName(LOCTEXT("FUEPythonServerTabTitle", "UE Python Server"))
        .SetMenuType(ETabSpawnerMenuType::Hidden);
}

void FUEPythonServerEditorModule::ShutdownModule()
{
    UE_LOG(LogTemp, Display, TEXT("UEPythonServerEditor: Shutting down module..."));
    
    // This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
    // we call this function before unloading the module.

    UToolMenus::UnRegisterStartupCallback(this);

    UToolMenus::UnregisterOwner(this);

    FUEPythonServerEditorStyle::Shutdown();

    FUEPythonServerEditorCommands::Unregister();

    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(UEPythonServerTabName);
}

TSharedRef<SDockTab> FUEPythonServerEditorModule::OnSpawnPluginTab(const FSpawnTabArgs& SpawnTabArgs)
{
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            // Put your tab content here!
            SNew(SBox)
            .HAlign(HAlign_Center)
            .VAlign(VAlign_Center)
            [
                SNew(STextBlock)
                .Text(LOCTEXT("WindowWidgetText", "UE Python Server is running on port 9876"))
            ]
        ];
}

void FUEPythonServerEditorModule::PluginButtonClicked()
{
    FGlobalTabmanager::Get()->TryInvokeTab(UEPythonServerTabName);
}

void FUEPythonServerEditorModule::RegisterMenus()
{
    // Owner will be used for cleanup in call to UToolMenus::UnregisterOwner
    FToolMenuOwnerScoped OwnerScoped(this);

    {
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
        {
            FToolMenuSection& Section = Menu->FindOrAddSection("WindowLayout");
            Section.AddMenuEntryWithCommandList(FUEPythonServerEditorCommands::Get().OpenPluginWindow, PluginCommands);
        }
    }

    {
        UToolMenu* ToolbarMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.LevelEditorToolBar");
        {
            FToolMenuSection& Section = ToolbarMenu->FindOrAddSection("Settings");
            {
                FToolMenuEntry& Entry = Section.AddEntry(FToolMenuEntry::InitToolBarButton(FUEPythonServerEditorCommands::Get().OpenPluginWindow));
                Entry.SetCommandList(PluginCommands);
            }
        }
    }
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FUEPythonServerEditorModule, UEPythonServerEditor) 