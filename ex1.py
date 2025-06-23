from abc import ABC, abstractmethod
import os
import json

#Protocol
class DataStore(ABC):
    
    @abstractmethod
    def store(self, key:str, value:str) -> bool:
        pass
    
    @abstractmethod
    def retrieve(self, key:str) -> str | None:
        pass
    
    @abstractmethod
    def delete(self, key:str) -> bool:
        pass
    
    @abstractmethod
    def list_keys(self) -> list[str]:
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        pass
    
    
    
    
    
    class FileStore(DataStore):
        def __init__(self, storage_dir: str="File_store"):
            self.storage_dir=storage_dir
            os.makedirs(storage_dir, exist_ok=True)
        
        def _get_file_path(self, key: str) -> str:
            return os.path.join(self.storage_dir, f"{key}.json")
        
       
        def store(self, key:str, value:str) -> bool:
            try: file_path = self._get_file_path(key)
            with open(file_path, 'w') as f: json.dump({"value": value}, f)
            except (IOError, OSError)
            return False
    

        def retrieve(self, key:str) -> str | None:
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None
        try: 
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data["value"]
        except (IOError, OSError, json.JSONDecodeError, KeyError):
            return None
    
        def delete(self, key: str) -> bool:
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except (IOError, OSError):
            return False
    

        def list_keys(self) -> list[str]:
        try:
            files = os.listdir(self.storage_dir)
            return [os.path.splitext(f)[0] for f in files if f.endswith('.json')]
        except (IOError, OSError):
            return []
    
    
        def is_healthy(self) -> bool:
        return os.path.exists(self.storage_dir) and os.access(self.storage_dir, os.W_OK)
        
        
        
    class MemoryStore(DataStore):
    """Implementation that stores data in memory."""
    
    def __init__(self):
        self._storage = {}
    
    def store(self, key: str, value: str) -> bool:
        self._storage[key] = value
        return True
    
    def retrieve(self, key: str) -> str | None:
        return self._storage.get(key, None)
    
    def delete(self, key: str) -> bool:
        if key not in self._storage:
            return False
        del self._storage[key]
        return True
    
    def list_keys(self) -> list[str]:
        return list(self._storage.keys())
    
    def is_healthy(self) -> bool:
        # Memory store is always healthy
        return True


class DatabaseStore(DataStore):

    def __init__(self):
        self._tables = {
            "data": {}  # Simulating a database table with a dictionary
        }
    
    def store(self, key: str, value: str) -> bool:
        self._tables["data"][key] = value
        return True
    
    def retrieve(self, key: str) -> str | None:
        return self._tables["data"].get(key, None)
    
    def delete(self, key: str) -> bool:
        if key not in self._tables["data"]:
            return False
        del self._tables["data"][key]
        return True
    
    def list_keys(self) -> list[str]:
        return list(self._tables["data"].keys())
    
    def is_healthy(self) -> bool:
        # Database is healthy if our "tables" exist
        return "data" in self._tables    
    
