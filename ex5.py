import sqlite3 
import requests
import subprocess
from typing import Protocol, Dict, Any, Optional, List
from pathlib import Path
from urllib.parse import urlparse
import contextlib
import logging

# 1. Define the Resource Protocol
class Resource(Protocol):
    def connect(self) -> bool:
        """Establish connection to the resource"""
        ...
    
    def query(self, command: str) -> Any:
        """Execute read operation"""
        ...
    
    def write(self, data: Any) -> bool:
        """Execute write operation"""
        ...
    
    def close(self) -> None:
        """Close the connection"""
        ...
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """Report what operations this resource supports"""
        ...
    
    def __enter__(self):
        """Context manager entry"""
        ...
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        ...

# 2. Implement Concrete Resources
class FileSystemResource:
    def __init__(self, uri: str):
        self.uri = uri
        self.path = Path(urlparse(uri).path)
        self._capabilities = {
            'read': True,
            'write': True,
            'execute': False
        }

    def connect(self) -> bool:
        return self.path.exists()

    def query(self, command: str) -> str:
        return self.path.read_text()

    def write(self, data: str) -> bool:
        self.path.write_text(data)
        return True

    def close(self) -> None:
        pass

    @property
    def capabilities(self) -> Dict[str, Any]:
        return self._capabilities

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class APIClientResource:
    def __init__(self, uri: str, api_key: Optional[str] = None):
        self.uri = uri
        self.api_key = api_key
        self.session = requests.Session()
        self._capabilities = {
            'read': True,
            'write': False,
            'execute': False
        }

    def connect(self) -> bool:
        try:
            resp = self.session.get(f"{self.uri}/ping")
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def query(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.uri}/{endpoint}"
        headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
        resp = self.session.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self.session.close()

    @property
    def capabilities(self) -> Dict[str, Any]:
        return self._
