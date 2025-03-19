// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "HttpServerModule.h"
#include "IHttpRouter.h"

class UEPYTHONSERVER_API FUEPythonServerModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	/**
	 * Starts the HTTP server on the specified port
	 * @param Port The port to run the server on
	 * @return True if the server started successfully
	 */
	bool StartServer(uint32 Port = 8500);

	/**
	 * Stops the HTTP server
	 */
	void StopServer();

	/**
	 * Checks if the server is currently running
	 * @return True if the server is running
	 */
	bool IsServerRunning() const;
	
	/**
	 * Gets the port the server is running on
	 * @return The port number
	 */
	uint32 GetServerPort() const { return ServerPort; }
	
private:
	/** The HTTP server instance */
	TSharedPtr<IHttpRouter> HttpRouter;
	
	/** Flag indicating if the server is running */
	bool bIsServerRunning = false;
	
	/** The port the server is running on */
	uint32 ServerPort = 8500;
	
	/** Handle for the Python code execution endpoint */
	FHttpRequestHandler ExecuteEndpointHandle;
	
	/** Handle for the status endpoint */
	FHttpRequestHandler StatusEndpointHandle;
	
	/**
	 * Registers the HTTP endpoints
	 */
	void RegisterEndpoints();
	
	/**
	 * Handles the execute endpoint request
	 */
	void HandleExecuteRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
	
	/**
	 * Handles the status endpoint request
	 */
	void HandleStatusRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
	
	/**
	 * Executes Python code in the Unreal Engine
	 * @param Code The Python code to execute
	 * @return Result of the execution
	 */
	FString ExecutePythonCode(const FString& Code);
}; 