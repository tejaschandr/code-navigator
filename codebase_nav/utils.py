import hashlib
from pathlib import Path

def get_db_path(project_path):
    project_path = Path(project_path).resolve()
    
    path_hash = hashlib.md5(str(project_path).encode()).hexdigest()[:16]
    project_name = project_path.name
    
    db_dir = Path.home() / '.codebase-nav' / f"{project_name}-{path_hash}"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    return str(db_dir)