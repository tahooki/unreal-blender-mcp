// Copyright Epic Games, Inc. All Rights Reserved.

#include "UEPythonServerEditor.h"
#include "SServerConfigPanel.h"
#include "UEPythonServer.h"
#include "Framework/Docking/TabManager.h"
#include "Widgets/Docking/SDockTab.h"
#include "LevelEditor.h"
#include "ToolMenus.h"
#include "Interfaces/IMainFrameModule.h"

static const FName UEPythonServerTabName("UEPythonServer");

#define LOCTEXT_NAMESPACE "FUEPythonServerEditorModule"

const FName FUEPythonServerEditorModule::PythonServerTabName("UEPythonServer");

void FUEPythonServerEditorModule::StartupModule()
{
	// Register the tab spawner
	RegisterTabSpawners();
	
	// Initialize status text
	StatusText = FText::FromString(TEXT("Server not running"));
	
	// Create toolbar extension
	if (IsRunningCommandlet() || IsRunningGame())
	{
		return;
	}
	
	// Register toolbar extension
	FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
	
	LevelEditorModule.GetToolBarExtensibilityManager()->AddExtender(
		MakeShared<FExtender>()->AddToolBarExtension(
			"Play",
			EExtensionHook::After,
			nullptr,
			FToolBarExtensionDelegate::CreateRaw(this, &FUEPythonServerEditorModule::AddToolbarExtension)
		)
	);
	
	// Refresh server status
	RefreshServerStatus();
}

void FUEPythonServerEditorModule::ShutdownModule()
{
	// Unregister tab spawner
	if (FGlobalTabmanager::Get()->HasTabSpawner(UEPythonServerTabName))
	{
		FGlobalTabmanager::Get()->UnregisterTabSpawner(UEPythonServerTabName);
	}
	
	// Stop server if running
	if (bIsServerRunning)
	{
		// Get the server module
		FUEPythonServerModule& ServerModule = FModuleManager::GetModuleChecked<FUEPythonServerModule>("UEPythonServer");
		ServerModule.StopServer();
	}
}

void FUEPythonServerEditorModule::RegisterTabSpawners()
{
	FGlobalTabmanager::Get()->RegisterNomadTabSpawner(
		UEPythonServerTabName,
		FOnSpawnTab::CreateRaw(this, &FUEPythonServerEditorModule::OnSpawnServerTab))
		.SetDisplayName(LOCTEXT("UEPythonServerTitle", "UE Python Server"))
		.SetMenuType(ETabSpawnerMenuType::Hidden);
}

TSharedRef<SDockTab> FUEPythonServerEditorModule::OnSpawnServerTab(const FSpawnTabArgs& SpawnTabArgs)
{
	// Create the config panel
	ConfigPanel = SNew(SServerConfigPanel);
	
	// Get the server module
	FUEPythonServerModule& ServerModule = FModuleManager::GetModuleChecked<FUEPythonServerModule>("UEPythonServer");
	
	// Set the current port
	ConfigPanel->SetPort(ServerPort);
	
	// Create the tab
	return SNew(SDockTab)
		.TabRole(ETabRole::NomadTab)
		[
			ConfigPanel.ToSharedRef()
		];
}

void FUEPythonServerEditorModule::AddToolbarExtension(FToolBarBuilder& Builder)
{
	Builder.AddSeparator();
	
	// Add the Python Server button
	Builder.AddToolBarButton(
		FUIAction(
			FExecuteAction::CreateRaw(this, &FUEPythonServerEditorModule::ToggleServer),
			FCanExecuteAction(),
			FGetActionCheckState()
		),
		NAME_None,
		GetToggleButtonText(),
		GetStatusText(),
		FSlateIcon(FEditorStyle::GetStyleSetName(), "ClassIcon.PythonScript"),
		EUserInterfaceActionType::Button
	);
}

FReply FUEPythonServerEditorModule::ToggleServer()
{
	// Get the server module
	FUEPythonServerModule& ServerModule = FModuleManager::GetModuleChecked<FUEPythonServerModule>("UEPythonServer");
	
	if (bIsServerRunning)
	{
		// Stop the server
		ServerModule.StopServer();
	}
	else
	{
		// Start the server
		ServerModule.StartServer(ServerPort);
	}
	
	// Update the server status
	RefreshServerStatus();
	
	// Update the config panel if it exists
	if (ConfigPanel.IsValid())
	{
		ConfigPanel->RefreshStatus();
	}
	
	return FReply::Handled();
}

void FUEPythonServerEditorModule::RefreshServerStatus()
{
	// Get the server module
	FUEPythonServerModule& ServerModule = FModuleManager::GetModuleChecked<FUEPythonServerModule>("UEPythonServer");
	
	// Update running state
	bIsServerRunning = ServerModule.IsServerRunning();
	
	// Update port
	if (bIsServerRunning)
	{
		ServerPort = ServerModule.GetServerPort();
	}
	
	// Update status text
	if (bIsServerRunning)
	{
		StatusText = FText::Format(
			FText::FromString(TEXT("Python Server: Running on port {0}")),
			FText::AsNumber(ServerPort)
		);
	}
	else
	{
		StatusText = FText::FromString(TEXT("Python Server: Not running"));
	}
}

FText FUEPythonServerEditorModule::GetStatusText() const
{
	return StatusText;
}

FSlateColor FUEPythonServerEditorModule::GetStatusTextColor() const
{
	if (bIsServerRunning)
	{
		return FSlateColor(FLinearColor(0.0f, 0.75f, 0.0f)); // Green for running
	}
	else
	{
		return FSlateColor(FLinearColor(0.75f, 0.0f, 0.0f)); // Red for stopped
	}
}

FText FUEPythonServerEditorModule::GetToggleButtonText() const
{
	return bIsServerRunning ? FText::FromString(TEXT("Stop Python Server")) : FText::FromString(TEXT("Start Python Server"));
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FUEPythonServerEditorModule, UEPythonServerEditor) 