"""
Extended Server for unreal-blender-mcp

This module extends the original BlenderMCP server from blender-mcp to provide
additional functionality while maintaining compatibility with upstream updates.
"""

import sys
import os
import importlib.util
import logging
from typing import Dict, Any, Optional, Union, List, AsyncIterator
import json
import asyncio
import time
from fastapi import FastAPI
import uvicorn

# Set up logger
logger = logging.getLogger("ExtendedBlenderMCPServer")

# 더미 클래스를 모듈 레벨에서 정의
class DummyBlenderConnection:
    def __init__(self, host='localhost', port=8401):
        self.host = host
        self.port = port
        self.extended_features_enabled = False
        self.is_connected = False
        logger.warning("Using dummy BlenderConnection")
    
    def connect(self):
        """시도하지만 항상 실패하는 연결 메서드"""
        logger.warning("Dummy connect called")
        self.last_error = "Dummy connection does not actually connect"
        return False
        
    def disconnect(self):
        """아무것도 하지 않는 종료 메서드"""
        logger.warning("Dummy disconnect called")
        
    def send_command(self, command_type, params=None):
        """안전한 더미 응답을 반환하는 명령 메서드"""
        logger.warning(f"Dummy send_command called: {command_type}")
        
        if command_type == "get_scene_info":
            return {
                "objects": [],
                "active_object": None,
                "mode": "OBJECT",
                "stats": {
                    "total_objects": 0,
                    "total_vertices": 0,
                    "total_faces": 0
                },
                "dummy": True
            }
        elif command_type == "get_object_info":
            return {
                "error": "Object not found in dummy connection",
                "dummy": True
            }
        elif command_type == "get_version_info":
            return {
                "version": "0.0.0",
                "dummy": True
            }
        
        return {
            "error": "Dummy BlenderConnection does not support real commands",
            "command": command_type,
            "dummy": True
        }

# blender-mcp 모듈과 클래스들을 저장할 변수
mcp = None
BlenderConnection = None
get_blender_connection = None
server_module = None

# blender-mcp 모듈을 찾는 향상된 방법
try:
    # 1. 직접 import 시도
    try:
        from blender_mcp.server import mcp, BlenderConnection, get_blender_connection
        logger.info("Successfully imported blender_mcp directly")
    except ImportError:
        logger.info("Direct import failed, trying alternative methods")
        
        # 2. 프로젝트 경로에서 blender-mcp 찾기
        possible_paths = []
        
        # 현재 파일 기준 상대 경로
        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # 프로젝트 루트 추정
        
        # 가능한 경로들
        possible_paths.extend([
            # 기존 방식
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'blender-mcp'),
            # 프로젝트 루트 옆에 있는 경우
            os.path.join(base_dir, 'blender-mcp'),
            # 형제 디렉토리로 있는 경우
            os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'blender-mcp'),
            # 시스템 파이썬 경로에 설치된 경우
            None  # importlib.util.find_spec('blender_mcp')으로 찾음
        ])
        
        # 설치된 파이썬 패키지에서 찾기
        try:
            import site
            site_packages = site.getsitepackages()
            for site_dir in site_packages:
                possible_paths.append(os.path.join(site_dir, 'blender-mcp'))
                possible_paths.append(os.path.join(site_dir, 'blender_mcp'))
        except Exception as e:
            logger.warning(f"Error getting site-packages: {str(e)}")
        
        # venv/virtualenv 환경 확인
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            try:
                venv_site_packages = os.path.join(sys.prefix, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
                possible_paths.append(os.path.join(venv_site_packages, 'blender-mcp'))
                possible_paths.append(os.path.join(venv_site_packages, 'blender_mcp'))
            except Exception as e:
                logger.warning(f"Error getting venv site-packages: {str(e)}")
        
        # 각 경로 시도
        server_path = None
        for path in possible_paths:
            if path is None:
                # importlib로 모듈 찾기
                try:
                    spec = importlib.util.find_spec('blender_mcp.server')
                    if spec and spec.origin:
                        server_path = spec.origin
                        logger.info(f"Found blender_mcp.server via importlib: {server_path}")
                        break
                except Exception as e:
                    logger.debug(f"Error finding spec: {str(e)}")
                continue
                
            if not os.path.exists(path):
                continue
                
            # src 디렉토리 찾기
            src_path = os.path.join(path, 'src')
            if not os.path.exists(src_path):
                src_path = path  # src가 없는 경우
                
            # server.py 찾기
            potential_server_path = os.path.join(src_path, 'blender_mcp', 'server.py')
            if os.path.exists(potential_server_path):
                server_path = potential_server_path
                logger.info(f"Found server.py at: {server_path}")
                
                # 모듈 import를 위해 경로 추가
                if path not in sys.path:
                    sys.path.append(path)
                if src_path not in sys.path:
                    sys.path.append(src_path)
                    
                break
        
        # 찾은 서버 모듈 로드
        if server_path:
            try:
                spec = importlib.util.spec_from_file_location("blender_mcp.server", server_path)
                server_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(server_module)
                
                # 필요한 클래스와 함수 참조
                mcp = server_module.mcp
                BlenderConnection = server_module.BlenderConnection
                get_blender_connection = server_module.get_blender_connection
                logger.info("Successfully loaded BlenderMCP server module")
            except Exception as e:
                logger.error(f"Error loading server module from {server_path}: {str(e)}")
                raise
        else:
            raise ImportError("Could not find blender_mcp.server module in any location")
            
except Exception as e:
    logger.error(f"Failed to import blender_mcp: {str(e)}")
    
    # 더미 mcp 객체
    class DummyMCP:
        def tool(self):
            def decorator(func):
                return func
            return decorator
            
        async def start(self, host, port):
            logger.warning(f"Dummy MCP server start called on {host}:{port}")
    
    mcp = DummyMCP()
    
    def get_blender_connection():
        return DummyBlenderConnection()

# Custom extended connection class that inherits from original
class ExtendedBlenderConnection(BlenderConnection):
    """Extended version of BlenderConnection with additional functionality."""
    
    def __init__(self, host: str = "localhost", port: int = 8401):
        """
        Initialize an extended Blender connection.
        
        Args:
            host: Host where Blender is running
            port: Port where the Blender addon server is listening
        """
        super().__init__(host, port)
        self.extended_features_enabled = False
    
    def connect(self) -> bool:
        """Connect and check for extended features support"""
        # 연결 시도 횟수 증가
        max_retries = 3
        retry_delay = 1.0  # 초 단위
        
        for retry in range(max_retries):
            try:
                if super().connect():
                    # 연결 성공 후 확장 기능 지원 확인
                    try:
                        # 먼저 기본 명령으로 테스트
                        logger.info(f"Testing connection with get_scene_info command")
                        self.send_command("get_scene_info", {})
                        
                        # 확장 기능 확인
                        try:
                            logger.info(f"Testing extended features with get_version_info command")
                            result = self.send_command("get_version_info", {})
                            self.extended_features_enabled = "extended_version" in result
                        except Exception as e:
                            # 확장 명령이 실패하면 기본 기능만 지원하는 것으로 간주
                            logger.info(f"Extended feature check failed: {str(e)}")
                            self.extended_features_enabled = False
                        
                        if self.extended_features_enabled:
                            logger.info(f"Connected to extended Blender addon v{result['extended_version']}")
                        else:
                            logger.info("Connected to standard Blender addon (no extended features)")
                        return True
                    except Exception as e:
                        # 만약 명령 실행이 실패해도 연결은 성공한 것으로 간주
                        logger.info(f"Connection established but command failed: {str(e)}")
                        self.extended_features_enabled = False
                        return True
                
                # 연결 실패, 재시도
                if retry < max_retries - 1:
                    logger.warning(f"Connection attempt {retry+1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Connection error on attempt {retry+1}: {str(e)}")
                if retry < max_retries - 1:
                    logger.warning(f"Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
        
        return False
    
    def send_extended_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command that's only available in the extended addon"""
        if not self.extended_features_enabled:
            raise Exception("Extended features not available in connected Blender addon")
        return self.send_command(command_type, params)

# Create global extended connection variable
_extended_blender_connection = None

def get_extended_blender_connection():
    """Get or create a persistent extended Blender connection"""
    global _extended_blender_connection
    
    # If we have an existing connection, check if it's still valid
    if _extended_blender_connection is not None:
        try:
            # Test the connection with a simple command
            result = _extended_blender_connection.send_command("get_scene_info")
            logger.info("Reusing existing Blender connection")
            return _extended_blender_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing extended connection is no longer valid: {str(e)}")
            try:
                _extended_blender_connection.disconnect()
            except Exception as sub_e:
                logger.warning(f"Error while disconnecting: {str(sub_e)}")
            finally:
                _extended_blender_connection = None
    
    # Create a new connection if needed
    if _extended_blender_connection is None:
        ports_to_try = [8401]
        connected = False
        exception_info = ""
        
        for port in ports_to_try:
            try:
                logger.info(f"Attempting to connect to Blender on port {port}")
                connection = ExtendedBlenderConnection(host="localhost", port=port)
                if connection.connect():
                    logger.info(f"Successfully connected to Blender on port {port}")
                    _extended_blender_connection = connection
                    connected = True
                    break
                else:
                    logger.warning(f"Failed to connect on port {port}")
            except Exception as e:
                error_msg = f"Error connecting to Blender on port {port}: {str(e)}"
                logger.warning(error_msg)
                exception_info += f"{error_msg}\n"
        
        if not connected:
            logger.error("Failed to connect to Blender on any port")
            _extended_blender_connection = None
            raise Exception(f"Could not connect to Blender. Make sure the Blender addon is running on port 8401 or 9876.\nErrors:\n{exception_info}")
    
    return _extended_blender_connection

# Define additional tools using the original MCP server as a base
@mcp.tool()
def extended_scene_info(ctx) -> str:
    """
    Get enhanced scene information with additional details not available in the standard addon.
    This tool uses the extended Blender addon functionality if available.
    """
    try:
        blender = get_extended_blender_connection()
        
        # If extended features are available, use them
        if blender.extended_features_enabled:
            result = blender.send_extended_command("get_version_info", {})
            extended_info = {
                "extended_info_available": True,
                "extended_version": result.get("extended_version", "unknown"),
                "scene_info": blender.send_command("get_scene_info")
            }
            return json.dumps(extended_info, indent=2)
        else:
            # Fall back to standard scene info
            result = blender.send_command("get_scene_info")
            return json.dumps({
                "extended_info_available": False,
                "scene_info": result
            }, indent=2)
    except Exception as e:
        logger.error(f"Error getting extended scene info: {str(e)}")
        return f"Error getting extended scene info: {str(e)}"

@mcp.tool()
def extended_command_example(ctx, param1: str = "", param2: int = 0) -> str:
    """
    Example of a tool that uses the extended Blender addon's custom commands.
    This tool will only work if the Blender addon has the extended functionality.
    
    Parameters:
    - param1: A string parameter
    - param2: An integer parameter
    """
    try:
        blender = get_extended_blender_connection()
        
        # Check if extended features are available
        if not blender.extended_features_enabled:
            return "This tool requires the extended Blender addon. Please install and enable it."
        
        # Call the extended command
        result = blender.send_extended_command("extended_command_example", {
            "param1": param1,
            "param2": param2
        })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error executing extended command: {str(e)}")
        return f"Error executing extended command: {str(e)}"

# Extended server class that enhances the original server
class ExtendedBlenderMCPServer:
    """
    Extended version of the BlenderMCP server with additional tools and features.
    """
    
    def __init__(self):
        """Initialize the extended server."""
        self.mcp = mcp
        self.app = FastAPI()
        
        # Register any additional configuration or setup here
        logger.info("Extended BlenderMCP server initialized")
    
    def register_additional_tools(self):
        """Register additional tools not defined in this module."""
        # This method can be used to dynamically register more tools
        pass
    
    async def start(self, host: str = "0.0.0.0", port: int = 8400):
        """Start the extended server."""
        logger.info(f"Starting extended BlenderMCP server on {host}:{port}")
        
        # Register any additional tools
        self.register_additional_tools()
        
        # Configure the server
        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()

async def run_extended_server(host: str = "0.0.0.0", port: int = 8400):
    """Run the extended MCP server."""
    server = ExtendedBlenderMCPServer()
    
    try:
        await server.start(host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise

# Allow direct execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_extended_server() 