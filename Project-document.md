# 프로젝트 설계서: unreal-blender-mcp

## 1. 프로젝트 개요

- **목표:**
Claude나 ChatGPT와 같은 AI 에이전트를 통해 MCP 서버와 연동하여, 언리얼과 블렌더를 원격에서 컨트롤할 수 있도록 지원합니다. 이 프로젝트는 [blender-mcp](https://github.com/ahujasid/blender-mcp.git)를 확장하여 Unreal Engine 지원을 추가합니다.
- **주요 산출물:**
    1. 언리얼 플러그인: Python 코드를 실행하여 Unreal Engine을 제어
    2. 블렌더 애드온: 기존 blender-mcp 애드온을 활용
    3. 통합 MCP 서버: AI 에이전트와의 통신 및 두 플랫폼 연동
- **개발 언어:**
모든 컴포넌트는 Python으로 개발됩니다.
- **핵심 원칙:**
    - 이중 플랫폼 지원: 하나의 MCP 서버를 통해 Blender와 Unreal Engine 모두 제어
    - AI 에이전트 통합: Claude, ChatGPT 등 AI 모델과 원활한 연동
    - 확장된 API: 두 플랫폼의 기능을 원활하게 활용할 수 있는 통합 API
    - Blender 기능 유지: PolyHaven 에셋, Hyper3D Rodin 모델 생성 등 기존 blender-mcp의 모든 기능 지원

---

## 2. 시스템 아키텍처 개요

- **중심 모듈:** MCP 서버
    - SSE(Server-Sent Events) 기반으로 AI 에이전트와 실시간 통신
    - Langchain 라이브러리를 활용하여 상태 저장, 문서 활용 및 장기 기억 기능 제공
- **엣지 모듈:** 언리얼 플러그인과 블렌더 애드온
    - 각각 포트 8500(언리얼)과 8400(블렌더)에서 POST 요청을 받아 Python 코드를 실행
    - 실행 결과와 예외를 명확하게 리턴하며, 시스템 크래쉬를 방지하는 방어 코드를 내장

**통신 흐름:**

```
[AI 에이전트] <--SSE--> [MCP 서버(포트 8300)] 
                           |
                           |--HTTP--> [Blender 애드온(포트 8400)]
                           |
                           |--HTTP--> [Unreal 플러그인(포트 8500)]
```

**통신 흐름 요약:**

1. AI 에이전트는 MCP 서버에 명령 및 실행할 코드 요청 전송
2. MCP 서버는 요청을 분석한 후, 해당 명령을 언리얼 플러그인 또는 블렌더 애드온에 전달하는 함수 호출을 진행
3. 각 플러그인은 POST 요청을 통해 전달된 코드를 안전하게 실행하고 결과 및 오류 정보를 MCP 서버에 전달
4. MCP 서버는 Langchain을 활용하여 상태 관리 및 작업 히스토리를 갱신하고, AI 에이전트에 결과를 반환

---

## 3. 구성 요소 상세 설계

### 3.1. 언리얼 플러그인

- **기능 및 역할:**
    - 외부(주로 MCP 서버)로부터 POST 방식으로 전달된 Python 코드를 실행
    - 실행 결과와 발생한 예외를 명확히 리턴
    - 시스템 크래쉬를 방지하는 안전장치 및 방어 코드를 구현
- **포트:** 8500
- **개발 언어 및 프레임워크:**
    - C++ 및 Python(Unreal Engine의 Python API 활용)
- **주요 기능:**
    - `/execute` 엔드포인트:
        - 요청 데이터로 실행할 Python 코드 수신
        - 안전한 코드 실행 (try-except, sandbox 또는 제한된 실행 환경 고려)
        - 실행 결과와 오류 메시지 기록 및 반환
- **안정성 및 예외 처리:**
    - 코드 실행 전 입력값 검증
    - 실행 중 발생하는 모든 예외를 캡쳐하여 로그 및 응답 메시지에 포함
    - 크래쉬 방지를 위한 타임아웃 및 리소스 제한 설정

**구현 참고사항:**
- UEPythonServer 폴더의 코드를 참고하여 구현
- 핵심 구성요소:
  - UEPythonServer.uplugin: 플러그인 메타데이터 정의
  - Source/UEPythonServer: C++ 구현 코드가 포함된 디렉토리
  - HTTP 서버 구현을 통해 POST 요청으로 Python 코드 실행
  - GEngine->Exec 함수를 사용하여 언리얼 엔진 내에서 Python 명령 실행
  - JSON 형식으로 응답 반환

### 3.2. 블렌더 애드온

- **기능 및 역할:**
    - Blender 환경 내에서 동작하며, MCP 서버로부터 POST 방식으로 전달된 Python 코드를 실행
    - 실행 결과와 오류 메시지를 UI 혹은 로그를 통해 명확히 제공
    - Blender 내 안정성을 보장하기 위한 방어 코드 적용
- **포트:** 8400 (기존 blender-mcp의 7777에서 변경)
- **개발 언어 및 API:**
    - Python (Blender의 내장 Python API 활용)
- **주요 기능:**
    - 소켓 서버 구현:
        - 실행할 Python 코드를 JSON 형식으로 수신
        - 안전하게 코드를 실행하며, Blender의 상태나 작업환경에 영향을 최소화
        - 결과 및 오류를 포맷팅하여 반환
    - 기존 blender-mcp의 기능 유지:
        - PolyHaven 에셋 다운로드 및 적용
        - Hyper3D Rodin을 이용한 3D 모델 생성
        - 오브젝트 생성, 수정, 삭제 등 기본 기능
- **안정성 및 예외 처리:**
    - Blender 환경과의 충돌을 방지하기 위해 별도 스레드나 비동기 처리 고려
    - 실행 전후 상태 롤백이나 안전장치 적용
    - 에러 발생 시, 상세한 에러 로그와 함께 사용자에게 알림

**구현 참고사항:**
- blender-mcp 폴더의 코드를 기반으로 구현
- 핵심 구성요소:
  - addon.py: 블렌더 애드온의 주요 구현 코드
  - 소켓 서버(포트 7777에서 8400으로 변경)를 통한 JSON 형식의 명령 처리
  - 주요 지원 기능:
    - get_scene_info: 현재 씬 정보 반환
    - get_object_info: 특정 오브젝트 정보 반환
    - create_object: 새 오브젝트 생성
    - modify_object: 기존 오브젝트 수정
    - delete_object: 오브젝트 삭제
    - set_material: 머티리얼 설정
    - execute_code: 임의의 Python 코드 실행
  - UI 패널을 통한 서버 시작/중지 기능

### 3.3. MCP 서버

- **기능 및 역할:**
    - AI 에이전트와 실시간 통신을 위한 SSE 서버 구현
    - 언리얼 플러그인과 블렌더 애드온에 호출할 함수들을 미리 정의하여, AI가 수행할 작업을 명확하게 지정
    - Langchain 라이브러리를 활용하여 상태 관리, 문서 전처리 및 장기 기억 기능 제공
- **포트:** 8300
- **개발 언어 및 프레임워크:**
    - Python (FastAPI 및 SSE 지원 라이브러리 사용)
- **주요 기능:**
    - **SSE 통신:**
        - `/stream` 엔드포인트를 통해 AI 에이전트와 실시간 메시지 주고받기
    - **블렌더 호출 함수:**
        - 기존 blender-mcp의 모든 기능 지원
        - 블렌더 연결 관리를 위한 BlenderConnection 클래스 활용
    - **언리얼 호출 함수:**
        - BlenderConnection 클래스를 상속받아 UnrealConnection 클래스 구현
        - Unreal Engine과의 통신을 위한 HTTP 클라이언트 구현
    - **Langchain 통합:**
        - 작업 히스토리 저장, 문서 분석, 장기 기억 기능
        - 사용자 정의 프롬프트를 커스터마이징할 수 있는 인터페이스 제공
- **안정성 및 예외 처리:**
    - 각 호출 함수에 대해 입력값 검증 및 예외 처리 구현
    - Langchain 관련 동작에서 발생하는 오류를 캡쳐하여 로그 및 재시도 로직 적용
    - 네트워크 통신 오류 및 SSE 연결 유지에 대한 재연결 로직 적용

**구현 참고사항:**
- blender-mcp/src/blender_mcp/server.py 파일을 기반으로 구현
- 핵심 구성요소:
  - FastMCP 클래스를 활용한 서버 구현
  - 블렌더 연결 관리를 위한 BlenderConnection 클래스를 확장
  - 언리얼 연결 관리를 위한 UnrealConnection 클래스 구현
  - 도구(tools) 정의:
    - 블렌더 관련: get_scene_info, create_object, set_material 등 기존 기능 유지
    - 언리얼 관련: 새로운 도구 함수 추가 (레벨 생성, 에셋 임포트 등)
  - 프롬프트(prompts) 정의로 AI 에이전트에게 명령 예시 제공
  - 연결 관리 및 오류 처리 로직

---

## 4. API 및 인터페이스 정의

### 4.1. 언리얼 플러그인 API (포트 8500)

- **Endpoint:** `/execute`
- **HTTP Method:** POST
- **Request Body 예시:**
    
    ```json
    {
      "code": "print('Hello Unreal')"
    }
    ```
    
- **Response 예시:**
    
    ```json
    {
      "result": "Hello Unreal",
      "error": null
    }
    ```
    
- **주요 고려사항:**
    - 입력 코드의 유효성 검사 및 샌드박스 환경에서의 실행
    - 실행 시간 제한 및 리소스 소비 제한 적용

### 4.2. 블렌더 애드온 API (포트 8400)

- **소켓 통신 방식:**
- **Request 예시:**
    
    ```json
    {
      "type": "execute_code",
      "params": {
        "code": "bpy.ops.mesh.primitive_cube_add()"
      }
    }
    ```
    
- **Response 예시:**
    
    ```json
    {
      "status": "success",
      "result": {
        "message": "Code executed successfully"
      }
    }
    ```
    
- **주요 고려사항:**
    - Blender 내부 상태와의 상호작용 시 충돌 방지
    - UI에 결과 표시하거나, 로그 파일에 기록하는 방법 구현

### 4.3. MCP 서버 API (포트 8300)

- **SSE Endpoint:** `/stream`
    - AI 에이전트와의 실시간 메시지 송수신
- **도구 함수 인터페이스:**
    - **블렌더 관련 도구:**
        - `get_scene_info()`: 현재 씬 정보 반환
        - `get_object_info(object_name)`: 특정 오브젝트 정보 반환
        - `create_object(type, name, location, rotation, scale)`: 새 오브젝트 생성
        - `modify_object(name, location, rotation, scale, visible)`: 오브젝트 수정
        - `set_material(object_name, material_name, color)`: 머티리얼 설정
        - `execute_blender_code(code)`: 임의의 Python 코드 실행
    - **언리얼 관련 도구:**
        - `create_unreal_level()`: 새 레벨 생성
        - `import_to_unreal(file_path)`: 에셋 임포트
        - `setup_character_controller()`: 캐릭터 컨트롤러 설정
        - `execute_unreal_code(code)`: 임의의 Python 코드 실행
- **Langchain 관련 인터페이스:**
    - 문서 전처리, 메모리 저장 및 검색 함수
    - 사용자 정의 프롬프트 커스터마이징 기능

---

## 5. 데이터 흐름 및 통신 구조

1. **AI 에이전트 → MCP 서버:**
    - 에이전트가 특정 작업(예: "Unreal에서 새 레벨 생성")에 대한 명령을 SSE 채널을 통해 전송
2. **MCP 서버 내부 처리:**
    - 명령어 파싱 후, 해당 작업을 수행하기 위해 정의된 도구 함수 실행
    - Langchain을 통해 필요한 문서나 메모리 정보를 조회하여, 작업 정확도 향상
3. **MCP 서버 → 언리얼/블렌더 플러그인:**
    - 블렌더의 경우: 소켓 통신을 통해 명령 전달
    - 언리얼의 경우: HTTP 요청을 통해 코드 전달
4. **언리얼/블렌더 플러그인 → MCP 서버:**
    - 코드 실행 결과 또는 에러 메시지를 반환
5. **MCP 서버 → AI 에이전트:**
    - 최종 실행 결과 및 상태 정보를 SSE를 통해 전송

---

## 6. 개발 환경 및 의존성

- **Python 버전:** 3.10 이상
- **웹 프레임워크:** FastAPI (SSE 지원 포함)
- **Langchain:** 문서 처리 및 메모리 기능 구현을 위한 라이브러리
- **Blender:** 3.0 이상
- **Unreal Engine:** 5.0 이상
- **패키지 관리자:** uv
- **추가 라이브러리:** Logging, Exception Handling, Socket 통신, HTTP 클라이언트

**프로젝트 구조:**
```
unreal-blender-mcp/
├── blender-mcp/
│   ├── addon.py (블렌더 애드온, 포트 8400으로 수정)
│   ├── src/
│   │   └── blender_mcp/
│   │       └── server.py (소켓 서버 구현)
├── UEPythonServer/ (언리얼 플러그인)
│   ├── UEPythonServer.uplugin
│   ├── Source/
│   │   └── UEPythonServer/
│   │       └── (C++ 소스 코드)
│   └── Content/
├── src/
│   └── unreal_blender_mcp/
│       ├── __init__.py
│       ├── server.py (통합 MCP 서버)
│       ├── blender_connection.py (블렌더 연결 관리)
│       ├── unreal_connection.py (언리얼 연결 관리)
│       └── langchain_integration.py (Langchain 통합)
├── main.py (MCP 서버 시작 스크립트)
├── pyproject.toml (프로젝트 의존성 정의)
└── README.md
```

---

## 7. 설치 및 실행 절차

### 7.1. 사전 요구 사항

- Python 3.10 이상 설치
- Blender 3.0 이상 설치
- Unreal Engine 5.0 이상 설치
- uv 패키지 매니저 설치:
  - Mac: `brew install uv`
  - Windows: PowerShell에서 `irm https://astral.sh/uv/install.ps1 | iex` 실행

### 7.2. MCP 서버 설치

1. 저장소 클론: `git clone https://github.com/[username]/unreal-blender-mcp.git`
2. 디렉토리 이동: `cd unreal-blender-mcp`
3. 가상 환경 생성: `uv venv`
4. 패키지 설치: `uv pip install -e .`

### 7.3. 블렌더 애드온 설치

1. `blender-mcp/addon.py` 파일을 준비
2. Blender 실행
3. Edit > Preferences > Add-ons로 이동
4. "Install..." 클릭 후 준비한 `addon.py` 파일 선택
5. "Interface: Blender MCP" 체크박스 활성화

### 7.4. 언리얼 플러그인 설치

1. `UEPythonServer` 폴더를 Unreal 프로젝트의 Plugins 폴더로 복사
2. Unreal Engine 실행
3. Edit > Plugins에서 "UEPythonServer" 플러그인 활성화
4. 엔진 재시작

### 7.5. AI 에이전트 설정

#### Claude 연동:
Claude for Desktop의 설정 파일에 다음 내용 추가:
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

#### Cursor 연동:
Cursor Settings > MCP에서 다음 명령어 추가:
```
uvx unreal-blender-mcp
```

---

## 8. 보안 및 안정성 강화 방안

- **안전한 코드 실행:**
    - 입력 코드에 대한 샌드박스 실행 환경 제공 (제한된 네임스페이스, 타임아웃 설정)
    - 민감한 시스템 함수 접근 제한
- **예외 처리 및 로깅:**
    - 모든 함수와 API에서 try-except 블록 적용 및 상세 로그 기록
    - 크래시 복구 메커니즘 구현
- **네트워크 보안:**
    - 로컬 네트워크 외부에서의 접근 제한
    - 필요 시 SSL/TLS 암호화 적용
- **리소스 관리:**
    - 코드 실행 시 메모리 및 CPU 사용량 제한
    - 무한 루프나 과도한 리소스 사용 방지 로직 적용
- **작업 백업:**
    - 중요 작업 전 자동 백업 기능 구현 권장
    - 복구 지점 생성 기능 고려

---

## 9. 향후 확장 및 유지보수

- **확장성:**
    - API 버전 관리 시스템 도입으로 하위 호환성 보장
    - 새로운 도구 함수 추가를 위한 표준화된 인터페이스 제공
    - 모듈 간 인터페이스 문서화를 통해 향후 유지보수 용이성 확보
- **향후 기능 확장:**
    - 추가 3D 플랫폼 지원 (Maya, 3ds Max 등)
    - 실시간 협업 기능 (여러 AI 에이전트의 동시 작업 조율)
    - 자동화된 워크플로우 템플릿 제공
- **성능 최적화:**
    - 대용량 데이터 전송 시 스트리밍 메커니즘 개선
    - 병렬 처리를 통한 동시 작업 요청 처리 효율화
- **모니터링:**
    - 각 모듈별 상태 모니터링 및 에러 리포팅 시스템 구축
    - 사용 통계 및 성능 분석 도구 통합

---

## 10. 개발 워크플로우

프로젝트는 다음과 같은 단계적 개발 절차를 따릅니다:

### 10.1. 개발 단계

1. **프로젝트 셋업 및 환경 구성**
   - 프로젝트 구조 설정, 의존성 관리, 개발 환경 구성
   - 기본 설정 파일 및 저장소 초기화

2. **MCP 서버 코어 개발**
   - SSE 서버 기능 구현
   - API 구조 설계 및 구현
   - Langchain 기능 통합

3. **블렌더 애드온 통합**
   - 기존 blender-mcp 애드온 수정
   - 필요한 엔드포인트 및 기능 구현
   - MCP 서버와의 통신 테스트

4. **언리얼 엔진 플러그인 개발**
   - UEPythonServer 플러그인 구조 생성
   - HTTP 서버 구현
   - Python 코드 실행 기능 개발
   - MCP 서버와의 통신 테스트

5. **통합 및 엔드투엔드 테스트**
   - 모든 구성 요소 간 완전한 통신 흐름 테스트
   - 다양한 시나리오에서의 기능 검증
   - 성능 최적화 및 문제 해결

6. **AI 에이전트 통합**
   - Claude/ChatGPT 사용을 위한 시스템 구성
   - AI 에이전트용 도구 함수 정의
   - AI 주도 워크플로우 테스트

7. **문서화 및 개선**
   - 사용자 및 개발자 문서 완성
   - 오류 처리 및 예외 상황 개선
   - 릴리스 준비

### 10.2. 개발 원칙

- **모듈식 테스트**: 각 구성 요소는 통합 전에 독립적으로 테스트 가능해야 함
- **지속적 통합**: 구성 요소의 정기적인 통합 테스트
- **문서 기반 개발**: 코드와 함께 문서 작성
- **보안 우선**: 처음부터 보안 조치 구현
- **사용자 경험**: 전체 개발 과정에서 최종 사용자(AI 에이전트) 경험 고려

### 10.3. 개발 추적

각 개발 단계의 진행 상황은 `workflow/` 디렉토리의 마크다운 파일에 자세히 기록되며, 개발 로그는 `workflow/development-log.md`에서 관리됩니다. 각 단계가 완료될 때마다 마일스톤을 기록하고 진행 상황을 업데이트합니다.

---

## 결론

unreal-blender-mcp 프로젝트는 AI 에이전트가 언리얼 엔진과 블렌더를 효과적으로 제어할 수 있는 통합된 인터페이스를 제공합니다. 기존 blender-mcp 프로젝트의 기능을 확장하여 언리얼 엔진 지원을 추가함으로써, 단일 MCP 서버를 통해 두 강력한 3D 플랫폼을 동시에 활용할 수 있게 되었습니다.

이 설계서에 기반하여 개발된 시스템은 3D 제작 워크플로우의 다양한 단계를 AI의 도움으로 자동화할 수 있게 해주며, Blender에서 모델링한 에셋을 Unreal Engine으로 손쉽게 전환하는 등의 통합 작업을 가능하게 합니다.

보안과 안정성에 중점을 두고 설계되었으며, 각 모듈이 독립적으로 동작하면서도 하나의 시스템으로 통합되어 효율적인 작업 환경을 제공합니다.