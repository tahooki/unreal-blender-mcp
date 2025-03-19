// Copyright Epic Games, Inc. All Rights Reserved.

#include "UEPythonServer.h"
#include "HttpServerModule.h"
#include "IHttpRouter.h"
#include "HttpServerResponse.h"
#include "HttpServerRequest.h"
#include "HttpPath.h"
#include "Json.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformProcess.h"
#include "Misc/CString.h"

// Add the Python script plugin includes
#include "PythonScriptPlugin.h"
#include "PyGenUtil.h"
#include "PyCore.h"

#define LOCTEXT_NAMESPACE "FUEPythonServerModule"

// Implement module interface
void FUEPythonServerModule::StartupModule()
{
	UE_LOG(LogTemp, Log, TEXT("UEPythonServer module starting up"));
}

void FUEPythonServerModule::ShutdownModule()
{
	if (bIsServerRunning)
	{
		StopServer();
	}
	UE_LOG(LogTemp, Log, TEXT("UEPythonServer module shutting down"));
}

bool FUEPythonServerModule::StartServer(uint32 Port)
{
	if (bIsServerRunning)
	{
		UE_LOG(LogTemp, Warning, TEXT("UEPythonServer already running on port %d"), ServerPort);
		return false;
	}
	
	ServerPort = Port;
	
	// Get HTTP server module
	FHttpServerModule& HttpServerModule = FModuleManager::LoadModuleChecked<FHttpServerModule>("HTTPServer");
	
	// Create router
	HttpRouter = HttpServerModule.GetHttpRouter(ServerPort);
	
	// Register endpoints
	RegisterEndpoints();
	
	// Start HTTP server
	if (!HttpServerModule.StartAllListeners())
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to start HTTP server on port %d"), ServerPort);
		return false;
	}
	
	bIsServerRunning = true;
	UE_LOG(LogTemp, Log, TEXT("UEPythonServer started on port %d"), ServerPort);
	return true;
}

void FUEPythonServerModule::StopServer()
{
	if (!bIsServerRunning)
	{
		return;
	}
	
	// Get HTTP server module
	FHttpServerModule& HttpServerModule = FModuleManager::LoadModuleChecked<FHttpServerModule>("HTTPServer");
	
	// Unregister endpoints
	if (HttpRouter.IsValid())
	{
		HttpRouter->UnbindRoute(ExecuteEndpointHandle);
		HttpRouter->UnbindRoute(StatusEndpointHandle);
	}
	
	// Stop HTTP server
	HttpServerModule.StopAllListeners();
	
	bIsServerRunning = false;
	UE_LOG(LogTemp, Log, TEXT("UEPythonServer stopped"));
}

bool FUEPythonServerModule::IsServerRunning() const
{
	return bIsServerRunning;
}

void FUEPythonServerModule::RegisterEndpoints()
{
	if (!HttpRouter.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("Cannot register endpoints - HTTP router is invalid"));
		return;
	}
	
	// Register execute endpoint
	FHttpPath ExecutePath("/execute");
	ExecuteEndpointHandle = HttpRouter->BindRoute(
		ExecutePath,
		EHttpServerRequestVerbs::VERB_POST,
		[this](const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
		{
			this->HandleExecuteRequest(Request, OnComplete);
		});
	
	// Register status endpoint
	FHttpPath StatusPath("/status");
	StatusEndpointHandle = HttpRouter->BindRoute(
		StatusPath,
		EHttpServerRequestVerbs::VERB_GET,
		[this](const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
		{
			this->HandleStatusRequest(Request, OnComplete);
		});
}

void FUEPythonServerModule::HandleExecuteRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
	UE_LOG(LogTemp, Log, TEXT("Received execute request"));
	
	// Create JSON response object
	TSharedPtr<FJsonObject> ResponseObj = MakeShared<FJsonObject>();
	
	// Parse request body
	FString RequestBody = UTF8_TO_TCHAR(Request.Body.GetData());
	TSharedPtr<FJsonObject> RequestObj;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(RequestBody);
	
	if (!FJsonSerializer::Deserialize(Reader, RequestObj))
	{
		// Failed to parse JSON
		ResponseObj->SetStringField("status", "error");
		ResponseObj->SetStringField("message", "Invalid JSON request");
		
		// Convert JSON to string and send response
		FString ResponseBody;
		TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResponseBody);
		FJsonSerializer::Serialize(ResponseObj.ToSharedRef(), Writer);
		
		OnComplete(FHttpServerResponse::Create(ResponseBody, TEXT("application/json")));
		return;
	}
	
	// Get the Python code from the request
	FString Code;
	if (!RequestObj->TryGetStringField("code", Code))
	{
		// Code parameter is missing
		ResponseObj->SetStringField("status", "error");
		ResponseObj->SetStringField("message", "Missing 'code' parameter");
		
		// Convert JSON to string and send response
		FString ResponseBody;
		TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResponseBody);
		FJsonSerializer::Serialize(ResponseObj.ToSharedRef(), Writer);
		
		OnComplete(FHttpServerResponse::Create(ResponseBody, TEXT("application/json")));
		return;
	}
	
	// Execute the Python code
	FString Result = ExecutePythonCode(Code);
	
	// Set the response
	ResponseObj->SetStringField("status", "success");
	ResponseObj->SetStringField("result", Result);
	
	// Convert JSON to string
	FString ResponseBody;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResponseBody);
	FJsonSerializer::Serialize(ResponseObj.ToSharedRef(), Writer);
	
	// Send response
	OnComplete(FHttpServerResponse::Create(ResponseBody, TEXT("application/json")));
}

void FUEPythonServerModule::HandleStatusRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
	// Create JSON response
	TSharedPtr<FJsonObject> ResponseObj = MakeShared<FJsonObject>();
	ResponseObj->SetStringField("status", "running");
	ResponseObj->SetStringField("version", "0.1.0");
	ResponseObj->SetNumberField("port", ServerPort);
	
	// Add Python availability info
	bool bIsPythonAvailable = FPythonScriptPlugin::Get()->IsPythonAvailable();
	ResponseObj->SetBoolField("python_available", bIsPythonAvailable);
	
	// Convert JSON to string
	FString ResponseBody;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResponseBody);
	FJsonSerializer::Serialize(ResponseObj.ToSharedRef(), Writer);
	
	// Send response
	OnComplete(FHttpServerResponse::Create(ResponseBody, TEXT("application/json")));
}

FString FUEPythonServerModule::ExecutePythonCode(const FString& Code)
{
	// Check if Python is available
	if (!FPythonScriptPlugin::Get()->IsPythonAvailable())
	{
		UE_LOG(LogTemp, Error, TEXT("Python is not available"));
		return TEXT("Error: Python is not available in this Unreal Engine instance");
	}
	
	// Create a string to capture output
	FString OutputString;
	
	// Redirect stdout to capture output
	FPyObjectPtr StdoutRedirect = FPythonScriptPlugin::Get()->RedirectPythonOutput([&OutputString](const FString& InString) {
		OutputString += InString;
		UE_LOG(LogTemp, Log, TEXT("Python output: %s"), *InString);
	});
	
	// Execute the Python code
	bool bSuccess = false;
	{
		// Use a Python script module's scope to execute the code
		FPythonScriptPlugin::Get()->ExecPythonString(
			Code, 
			/* OutResult */ nullptr, 
			/* OutError */ nullptr, 
			/* InPythonModule */ FString("__main__"),
			/* InLocalContext */ nullptr,
			/* bStopOnError */ true,
			/* bSilent */ false,
			/* OutSuccess */ &bSuccess
		);
	}
	
	// Reset stdout redirection
	StdoutRedirect.Reset();
	
	if (!bSuccess)
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to execute Python code"));
		return FString::Printf(TEXT("Error executing Python code. Output: %s"), *OutputString);
	}
	
	return OutputString;
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FUEPythonServerModule, UEPythonServer) 