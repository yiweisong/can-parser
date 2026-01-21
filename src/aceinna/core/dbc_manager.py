import cantools
import os
from typing import Dict, Optional

class DBCManager:
    _cache: Dict[str, cantools.database.Database] = {}

    @classmethod
    def load_dbc(cls, dbc_path: str) -> Optional[cantools.database.Database]:
        """
        Load a DBC file. Uses caching to avoid reloading the same file.
        """
        if not dbc_path:
            return None
            
        if dbc_path in cls._cache:
            return cls._cache[dbc_path]
        
        if not os.path.exists(dbc_path):
             raise FileNotFoundError(f"DBC file not found: {dbc_path}")
             
        try:
            db = cantools.database.load_file(dbc_path)
            cls._cache[dbc_path] = db
            return db
        except Exception as e:
            print(f"Error loading DBC file {dbc_path}: {e}")
            raise e
