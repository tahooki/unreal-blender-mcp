// Copyright Epic Games, Inc. All Rights Reserved.

#include "SServerConfigPanel.h"
#include "UEPythonServer.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Input/SNumericEntryBox.h"
#include "Widgets/Layout/SBox.h"
#include "EditorStyleSet.h"
#include "Modules/ModuleManager.h"

void SServerConfigPanel::Construct(const FArguments& InArgs)
{
	// Initialize status text
	StatusText = FText::FromString(TEXT("Server not running"));
	
	// Get current server status
	RefreshStatus();
	
	// Create the UI
	ChildSlot
	[
		SNew(SVerticalBox)
		
		// Title
		+SVerticalBox::Slot()
		.AutoHeight()
		.Padding(5.0f)
		[
			SNew(STextBlock)
			.Text(FText::FromString(TEXT("UE Python Server Configuration")))
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 14))
		]
		
		// Port Configuration
		+SVerticalBox::Slot()
		.AutoHeight()
		.Padding(5.0f)
		[
			SNew(SHorizontalBox)
			
			+SHorizontalBox::Slot()
			.AutoWidth()
			.VAlign(VAlign_Center)
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(STextBlock)
				.Text(FText::FromString(TEXT("Server Port:")))
			]
			
			+SHorizontalBox::Slot()
			.AutoWidth()
			.VAlign(VAlign_Center)
			[
				SNew(SNumericEntryBox<uint32>)
				.Value(this, &SServerConfigPanel::GetPort)
				.OnValueCommitted(this, &SServerConfigPanel::OnPortTextCommitted)
				.AllowSpin(true)
				.MinValue(1024)
				.MaxValue(65535)
				.MinSliderValue(1024)
				.MaxSliderValue(65535)
			]
		]
		
		// Status and Controls
		+SVerticalBox::Slot()
		.AutoHeight()
		.Padding(5.0f)
		[
			SNew(SHorizontalBox)
			
			+SHorizontalBox::Slot()
			.AutoWidth()
			.VAlign(VAlign_Center)
			.Padding(0.0f, 0.0f, 5.0f, 0.0f)
			[
				SNew(STextBlock)
				.Text(FText::FromString(TEXT("Status:")))
			]
			
			+SHorizontalBox::Slot()
			.AutoWidth()
			.VAlign(VAlign_Center)
			[
				SNew(STextBlock)
				.Text(this, &SServerConfigPanel::GetStatusText)
				.ColorAndOpacity(this, &SServerConfigPanel::GetStatusTextColor)
			]
			
			+SHorizontalBox::Slot()
			.FillWidth(1.0f)
			.HAlign(HAlign_Right)
			[
				SNew(SButton)
				.Text(this, &SServerConfigPanel::GetToggleButtonText)
				.OnClicked(this, &SServerConfigPanel::OnToggleServer)
			]
		]
		
		// Info Section
		+SVerticalBox::Slot()
		.AutoHeight()
		.Padding(5.0f)
		[
			SNew(SBorder)
			.BorderImage(FEditorStyle::GetBrush("ToolPanel.GroupBorder"))
			.Padding(5.0f)
			[
				SNew(SVerticalBox)
				
				+SVerticalBox::Slot()
				.AutoHeight()
				.Padding(2.0f)
				[
					SNew(STextBlock)
					.Text(FText::FromString(TEXT("The UE Python Server allows external applications to execute Python code within Unreal Engine.")))
					.AutoWrapText(true)
				]
				
				+SVerticalBox::Slot()
				.AutoHeight()
				.Padding(2.0f)
				[
					SNew(STextBlock)
					.Text(FText::FromString(TEXT("API Endpoint: http://localhost:<port>/execute")))
					.AutoWrapText(true)
				]
				
				+SVerticalBox::Slot()
				.AutoHeight()
				.Padding(2.0f)
				[
					SNew(STextBlock)
					.Text(FText::FromString(TEXT("Request Format: { \"code\": \"python_code_here\" }")))
					.AutoWrapText(true)
				]
			]
		]
	];
}

void SServerConfigPanel::OnPortTextCommitted(const FText& InText, ETextCommit::Type CommitType)
{
	if (CommitType == ETextCommit::OnEnter || CommitType == ETextCommit::OnUserMovedFocus)
	{
		// Parse the port value
		uint32 NewPort = FCString::Atoi(*InText.ToString());
		
		// Validate port range
		if (NewPort >= 1024 && NewPort <= 65535)
		{
			Port = NewPort;
		}
	}
}

bool SServerConfigPanel::OnPortTextIsValid(const FText& InText, FText& OutErrorMessage)
{
	// Parse the port value
	uint32 NewPort = FCString::Atoi(*InText.ToString());
	
	// Validate port range
	if (NewPort < 1024 || NewPort > 65535)
	{
		OutErrorMessage = FText::FromString(TEXT("Port must be between 1024 and 65535"));
		return false;
	}
	
	return true;
}

FText SServerConfigPanel::GetPortText() const
{
	return FText::AsNumber(Port);
}

FReply SServerConfigPanel::OnToggleServer()
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
		ServerModule.StartServer(Port);
	}
	
	// Refresh status
	RefreshStatus();
	
	return FReply::Handled();
}

FText SServerConfigPanel::GetToggleButtonText() const
{
	return bIsServerRunning ? FText::FromString(TEXT("Stop Server")) : FText::FromString(TEXT("Start Server"));
}

FText SServerConfigPanel::GetStatusText() const
{
	return StatusText;
}

FSlateColor SServerConfigPanel::GetStatusTextColor() const
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

void SServerConfigPanel::RefreshStatus()
{
	// Get the server module
	FUEPythonServerModule& ServerModule = FModuleManager::GetModuleChecked<FUEPythonServerModule>("UEPythonServer");
	
	// Update running state
	bIsServerRunning = ServerModule.IsServerRunning();
	
	// Update status text
	if (bIsServerRunning)
	{
		StatusText = FText::Format(
			FText::FromString(TEXT("Running on port {0}")),
			FText::AsNumber(ServerModule.GetServerPort())
		);
	}
	else
	{
		StatusText = FText::FromString(TEXT("Not running"));
	}
} 