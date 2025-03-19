// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Input/Reply.h"

/**
 * Server configuration panel widget
 */
class SServerConfigPanel : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(SServerConfigPanel)
	{}
	SLATE_END_ARGS()

	/** Constructs this widget */
	void Construct(const FArguments& InArgs);
	
	/** Update port number from the text box */
	void OnPortTextCommitted(const FText& InText, ETextCommit::Type CommitType);
	
	/** Validate port input - ensure it's a valid port number */
	bool OnPortTextIsValid(const FText& InText, FText& OutErrorMessage);
	
	/** Get the current port text */
	FText GetPortText() const;
	
	/** Toggle server state (start/stop) */
	FReply OnToggleServer();
	
	/** Get the toggle button text */
	FText GetToggleButtonText() const;
	
	/** Get the current server status text */
	FText GetStatusText() const;
	
	/** Get the color for the status text */
	FSlateColor GetStatusTextColor() const;
	
	/** Refresh status from the server module */
	void RefreshStatus();
	
	/** Get current port setting */
	uint32 GetPort() const { return Port; }
	
	/** Set current port setting */
	void SetPort(uint32 InPort) { Port = InPort; }
	
private:
	/** The current port to use */
	uint32 Port = 8500;
	
	/** Flag indicating if server is running */
	bool bIsServerRunning = false;
	
	/** Current status text */
	FText StatusText;
}; 