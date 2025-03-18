// Copyright Epic Games, Inc. All Rights Reserved.

#include "UEPythonServer.h"
#include "HttpModule.h"
#include "HttpServerModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "Misc/OutputDeviceNull.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"

#define LOCTEXT_NAMESPACE "FUEPythonServerModule"
#define SERVER_PORT 9876

void FUEPythonServerModule::StartupModule()
{
    // This code will execute after your module is loaded into memory
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Module started"));
    
    StartHttpServer();
}

void FUEPythonServerModule::ShutdownModule()
{
    // This function may be called during shutdown to clean up your module
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Module shutting down"));
    
    StopHttpServer();
}

void FUEPythonServerModule::StartHttpServer()
{
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Starting HTTP server on port %d"), SERVER_PORT);
    
    FHttpServerModule& HttpServerModule = FModuleManager::LoadModuleChecked<FHttpServerModule>("HTTPServer");
    
    TSharedPtr<IHttpRouter> HttpRouter = HttpServerModule.GetHttpRouter();
    
    // Register route for Python execution
    HttpRouter->BindRoute(TEXT("/execute_python"), EHttpServerRequestVerbs::VERB_POST,
        [this](const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete) -> bool
        {
            FString PythonCode;
            if (Request.Body.IsValid())
            {
                PythonCode = FString(UTF8_TO_TCHAR(Request.Body.GetData()));
            }
            
            // Execute Python code
            FOutputDeviceNull Ar;
            FString Command = FString::Printf(TEXT("py %s"), *PythonCode);
            
            if (GEngine)
            {
                GEngine->Exec(nullptr, *Command, Ar);
                UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Executed Python code"));
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("UEPythonServer: GEngine is null"));
            }
            
            // Create response
            TSharedPtr<FJsonObject> ResponseObject = MakeShareable(new FJsonObject);
            ResponseObject->SetStringField(TEXT("status"), TEXT("success"));
            ResponseObject->SetStringField(TEXT("message"), TEXT("Python code executed"));
            
            FString ResponseString;
            TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResponseString);
            FJsonSerializer::Serialize(ResponseObject.ToSharedRef(), Writer);
            
            return OnComplete(FHttpServerResponse::Create(ResponseString, TEXT("application/json")));
        });
    
    // Start the server
    if (HttpRouter->StartServer(SERVER_PORT))
    {
        UE_LOG(LogTemp, Display, TEXT("UEPythonServer: HTTP server started successfully"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("UEPythonServer: Failed to start HTTP server"));
    }
}

void FUEPythonServerModule::StopHttpServer()
{
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Stopping HTTP server"));
    
    FHttpServerModule& HttpServerModule = FModuleManager::LoadModuleChecked<FHttpServerModule>("HTTPServer");
    HttpServerModule.StopAllListeners();
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FUEPythonServerModule, UEPythonServer) 