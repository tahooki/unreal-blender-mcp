// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "Widgets/Docking/SDockTab.h"

class FUEPythonServerEditorModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;
	
	/** Adds menu extension to the Level Editor toolbar */
	void AddToolbarExtension(FToolBarBuilder& Builder);
	
	/** Toggle server state (start/stop) */
	FReply ToggleServer();
	
	/** Refresh server status */
	void RefreshServerStatus();
	
	/** Get the current status text */
	FText GetStatusText() const;
	
	/** Get the color for the status text */
	FSlateColor GetStatusTextColor() const;
	
	/** Get the toggle button text */
	FText GetToggleButtonText() const;
	
	/** Open the server settings tab */
	TSharedRef<SDockTab> OnSpawnServerTab(const FSpawnTabArgs& SpawnTabArgs);
	
private:
	/** Track whether server is running */
	bool bIsServerRunning = false;
	
	/** Current port setting */
	uint32 ServerPort = 8500;
	
	/** Current status text */
	FText StatusText;
	
	/** Server configuration panel */
	TSharedPtr<class SServerConfigPanel> ConfigPanel;
	
	/** Register the tab spawners */
	void RegisterTabSpawners();
	
	/** The Python Server tab ID */
	static const FName PythonServerTabName;
}; 