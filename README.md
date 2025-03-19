# unreal-blender-mcp

## 프로젝트 개요

unreal-blender-mcp는 AI 에이전트(Claude, ChatGPT 등)를 통해 Unreal Engine과 Blender를 MCP(Model Context Protocol) 서버로 원격 제어할 수 있는 통합 솔루션입니다. 이 프로젝트는 [blender-mcp](https://github.com/ahujasid/blender-mcp.git)를 확장하여 Unreal Engine 지원을 추가합니다.

### 주요 구성 요소

1. **Unreal Engine 플러그인**: Python 코드를 실행하여 Unreal Engine을 제어
2. **Blender 애드온**: 기존 blender-mcp 애드온을 활용
3. **통합 MCP 서버**: AI 에이전트와의 통신 및 두 플랫폼 연동

### 핵심 기능

- **이중 플랫폼 지원**: 하나의 MCP 서버를 통해 Blender와 Unreal Engine 모두 제어
- **AI 에이전트 통합**: Claude, ChatGPT 등 AI 모델과 원활한 연동
- **확장된 API**: 두 플랫폼의 기능을 원활하게 활용할 수 있는 통합 API
- **Blender 기능 유지**: PolyHaven 에셋, Hyper3D Rodin 모델 생성 등 기존 blender-mcp의 모든 기능 지원

## 시스템 아키텍처

### 통신 흐름

```
[AI 에이전트] <--SSE--> [MCP 서버(포트 8300)] 
                           |
                           |--HTTP--> [Blender 애드온(포트 8400)]
                           |
                           |--HTTP--> [Unreal 플러그인(포트 8500)]
```

### 포트 구성

- **MCP 서버**: 8300 포트 (AI 에이전트와 통신)
- **Blender 애드온**: 8400 포트 (MCP 서버로부터 명령 수신)
- **Unreal 플러그인**: 8500 포트 (MCP 서버로부터 명령 수신)

## 설치 방법

### 사전 요구 사항

- Python 3.10 이상
- Blender 3.0 이상
- Unreal Engine 5.0 이상
- uv 패키지 매니저

#### UV 설치

**Mac의 경우:**
```bash
brew install uv
```

**Windows의 경우:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
set Path=C:\Users\[사용자명]\.local\bin;%Path%
```

### 1. MCP 서버 설치

```bash
git clone https://github.com/[your-repo]/unreal-blender-mcp.git
cd unreal-blender-mcp
uv venv
uv pip install -e .
```

### 2. Blender 애드온 설치

1. `blender-mcp/addon.py` 파일을 다운로드
2. Blender 실행
3. Edit > Preferences > Add-ons로 이동
4. "Install..." 클릭 후 다운로드한 `addon.py` 선택
5. "Interface: Blender MCP" 옆의 체크박스 활성화

### 3. Unreal 플러그인 설치

1. `UEPythonServer` 폴더를 Unreal 프로젝트의 Plugins 폴더로 복사
2. Unreal Engine 실행
3. Edit > Plugins에서 "UEPythonServer" 플러그인 활성화
4. 엔진 재시작

### 4. AI 에이전트 설정

#### Claude 연동

Claude for Desktop의 설정 파일(claude_desktop_config.json)에 다음 내용 추가:

```json
{
    "mcpServers": {
        "unreal-blender": {
            "command": "uvx",
            "args": [
                "unreal-blender-mcp"
            ]
        }
    }
}
```

#### Cursor 연동

Cursor Settings > MCP에서 다음 명령어 추가:

```
uvx unreal-blender-mcp
```

## 사용 방법

### 연결 시작하기

1. **Blender 연결**:
   - Blender의 3D View 사이드바(N키)에서 "BlenderMCP" 탭 열기
   - "Connect to Claude" 클릭

2. **Unreal 연결**:
   - Unreal Editor에서 Window > UEPythonServer 메뉴 선택
   - "Start Server" 버튼 클릭

3. **AI 에이전트에서 사용**:
   - Claude/ChatGPT에서 MCP 서버가 활성화되었는지 확인
   - 블렌더 또는 언리얼 명령 실행 요청

### 예제 명령

**Blender 명령 예시:**
- "Create a low poly scene in Blender with a dragon guarding a pot of gold"
- "Create a beach scene in Blender using HDRIs and textures from Poly Haven"
- "Generate a 3D model of a garden gnome in Blender using Hyper3D"

**Unreal 명령 예시:**
- "Create a new level in Unreal with a basic landscape"
- "Import the 3D model from Blender to Unreal"
- "Set up a basic character controller in Unreal"

**통합 명령 예시:**
- "Create a character in Blender, then export and import it into Unreal"
- "Design an environment in Blender and recreate it in Unreal with proper lighting"

## 기술 세부 사항

### 블렌더 연동

- 기존 [blender-mcp](https://github.com/ahujasid/blender-mcp.git)의 소켓 서버를 기반으로 구현
- 기존 기능 유지(PolyHaven, Hyper3D Rodin 등 포함)
- 포트 번호를 7777에서 8400으로 변경

### 언리얼 연동

- UEPythonServer를 기반으로 구현된 HTTP 서버
- GEngine->Exec 함수를 통한 Python 명령 실행
- 포트 번호 8500 사용

### MCP 서버

- Blender 및 Unreal 서버와의 통신을 관리
- BlenderConnection 클래스를 상속받아 UnrealConnection 클래스 구현
- SSE(Server-Sent Events)를 통한 AI 에이전트와의 실시간 통신
- Langchain 활용 상태 관리 및 기억 기능

## 문제 해결

- **연결 문제**: 각 플러그인의 서버가 실행 중인지 확인하고, 방화벽 설정을 확인하세요.
- **타임아웃 오류**: 복잡한 요청은 여러 단계로 나누어 실행해보세요.
- **Poly Haven 문제**: 이미지 다운로드 권한 및 경로를 확인하세요.
- **재시작 시도**: 문제가 지속되면 Blender, Unreal, 그리고 MCP 서버를 모두 재시작해보세요.

## 보안 고려사항

- `execute_blender_code`와 `execute_unreal_code` 도구는 임의의 코드를 실행할 수 있으므로 주의하세요.
- 중요한 작업 전에는 항상 프로젝트를 저장하세요.
- 프로덕션 환경에서는 코드 실행 제한을 고려하세요.

## 기여하기

기여는 언제나 환영합니다! Pull Request를 제출해주세요.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 면책 조항

이 프로젝트는 Blender 또는 Unreal Engine의 공식 제품이 아닌 서드파티 통합입니다.