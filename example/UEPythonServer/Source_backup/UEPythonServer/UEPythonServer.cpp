#include "UEPythonServer.h"
#include "HttpModule.h"
#include "HttpServerModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "Misc/OutputDeviceNull.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"

#define SERVER_PORT 9876

void FUEPythonServerModule::StartupModule()
{
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Starting module..."));
    StartHttpServer();
}

void FUEPythonServerModule::ShutdownModule()
{
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Shutting down module..."));
    StopHttpServer();
}

void FUEPythonServerModule::StartHttpServer()
{
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Initializing HTTP Server..."));
    
    FHttpModule& HttpModule = FHttpModule::Get();
    HttpModule.CreateHttpRouter();

    // HTTP 요청을 처리하는 엔드포인트 등록
    HttpModule.GetHttpRouter()->BindRoute("/execute_python", EHttpServerRequestVerbs::VERB_POST,
        [this](const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete) -> bool
        {
            FString PythonCode;
            if (Request.Body.IsValid())
            {
                PythonCode = FString(UTF8_TO_TCHAR(Request.Body.GetData()));
            }

            // Python 코드 실행
            FOutputDeviceNull Ar;
            FString Command = FString::Printf(TEXT("py %s"), *PythonCode);
            GEngine->Exec(nullptr, *Command, Ar);

            // HTTP 응답 생성
            TSharedPtr<FJsonObject> ResponseObject = MakeShareable(new FJsonObject);
            ResponseObject->SetStringField("result", "Python 실행 완료");

            FString ResponseString;
            TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ResponseString);
            FJsonSerializer::Serialize(ResponseObject.ToSharedRef(), Writer);

            UE_LOG(LogTemp, Display, TEXT("UEPythonServer: Executed Python code"));

            auto Response = FHttpServerResponse::Create(ResponseString, TEXT("application/json"));
            OnComplete(MoveTemp(Response));
            return true;
        });

    if (HttpModule.GetHttpRouter()->StartServer(SERVER_PORT))
    {
        UE_LOG(LogTemp, Display, TEXT("UEPythonServer: HTTP Server Started on port %d"), SERVER_PORT);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("UEPythonServer: Failed to start HTTP Server on port %d"), SERVER_PORT);
    }
}

void FUEPythonServerModule::StopHttpServer()
{
    FHttpModule& HttpModule = FHttpModule::Get();
    HttpModule.GetHttpRouter()->StopServer();
    UE_LOG(LogTemp, Display, TEXT("UEPythonServer: HTTP Server Stopped"));
}

IMPLEMENT_MODULE(FUEPythonServerModule, UEPythonServer) 