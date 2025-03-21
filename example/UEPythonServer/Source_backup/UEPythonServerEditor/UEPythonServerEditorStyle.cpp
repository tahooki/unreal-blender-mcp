#include "UEPythonServerEditorStyle.h"
#include "Styling/SlateStyleRegistry.h"
#include "Framework/Application/SlateApplication.h"
#include "Slate/SlateGameResources.h"
#include "Interfaces/IPluginManager.h"
#include "Styling/SlateStyleMacros.h"

#define RootToContentDir Style->RootToContentDir

TSharedPtr<FSlateStyleSet> FUEPythonServerEditorStyle::StyleInstance = nullptr;

void FUEPythonServerEditorStyle::Initialize()
{
    if (!StyleInstance.IsValid())
    {
        StyleInstance = Create();
        FSlateStyleRegistry::RegisterSlateStyle(*StyleInstance);
    }
}

void FUEPythonServerEditorStyle::Shutdown()
{
    FSlateStyleRegistry::UnRegisterSlateStyle(*StyleInstance);
    ensure(StyleInstance.IsUnique());
    StyleInstance.Reset();
}

FName FUEPythonServerEditorStyle::GetStyleSetName()
{
    static FName StyleSetName(TEXT("UEPythonServerEditorStyle"));
    return StyleSetName;
}

const FVector2D Icon16x16(16.0f, 16.0f);
const FVector2D Icon20x20(20.0f, 20.0f);
const FVector2D Icon40x40(40.0f, 40.0f);

TSharedRef<FSlateStyleSet> FUEPythonServerEditorStyle::Create()
{
    TSharedRef<FSlateStyleSet> Style = MakeShareable(new FSlateStyleSet("UEPythonServerEditorStyle"));
    Style->SetContentRoot(IPluginManager::Get().FindPlugin("UEPythonServer")->GetBaseDir() / TEXT("Resources"));

    Style->Set("UEPythonServerEditor.OpenPluginWindow", new IMAGE_BRUSH(TEXT("ButtonIcon_40x"), Icon40x40));
    Style->Set("UEPythonServerEditor.OpenPluginWindow.Small", new IMAGE_BRUSH(TEXT("ButtonIcon_16x"), Icon16x16));

    return Style;
}

void FUEPythonServerEditorStyle::ReloadTextures()
{
    if (FSlateApplication::IsInitialized())
    {
        FSlateApplication::Get().GetRenderer()->ReloadTextureResources();
    }
}

const ISlateStyle& FUEPythonServerEditorStyle::Get()
{
    return *StyleInstance;
} 