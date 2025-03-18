// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "Http.h"

class UEPYTHONSERVER_API FUEPythonServerModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    /** Starts the HTTP server */
    void StartHttpServer();
    
    /** Stops the HTTP server */
    void StopHttpServer();
}; 