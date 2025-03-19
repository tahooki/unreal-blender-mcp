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
	// This is a placeholder implementation - we'll need to parse the JSON, execute the Python code,
	// and return the result in the complete implementation
	
	// Create JSON response
	TSharedPtr<FJsonObject> ResponseObj = MakeShared<FJsonObject>();
	ResponseObj->SetStringField("status", "success");
	ResponseObj->SetStringField("message", "Execute endpoint called - this is a placeholder implementation");
	
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
	
	// Convert JSON to string
	FString ResponseBody;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResponseBody);
	FJsonSerializer::Serialize(ResponseObj.ToSharedRef(), Writer);
	
	// Send response
	OnComplete(FHttpServerResponse::Create(ResponseBody, TEXT("application/json")));
}

FString FUEPythonServerModule::ExecutePythonCode(const FString& Code)
{
	// This is a placeholder implementation - in the complete implementation,
	// we'll execute the Python code using Unreal's Python API
	return TEXT("Python code execution not implemented yet");
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FUEPythonServerModule, UEPythonServer) 