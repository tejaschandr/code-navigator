import os
from pathlib import Path

class CodeScanner:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.extensions = {
        '.py', '.js', '.ts', '.tsx', '.jsx',  # Current
        '.java', '.cpp', '.c', '.h', '.hpp',  # Current
        '.go', '.rs', '.rb', '.php',          # Popular languages
        '.swift', '.kt', '.scala',            # Mobile/JVM
        '.sql', '.sh', '.yaml', '.yml',       # Config/scripts
        '.md', '.txt'                          # Documentation
        } # will add testing for md and txt later, need more robust descriptions and chunking for those
        self.skip_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'build', '.next'} # Will add others later

    def scan(self):
        files = []

        for root, dirs, filenames in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]

            for filename in filenames:
                filepath = Path(root) / filename
                if filepath.suffix in self.extensions:
                    files.append(filepath)
        return files
if __name__ == "__main__":
    scanner = CodeScanner(".")
    files = scanner.scan()

    print(f"Found {len(files)} code files:")
    for f in files[:5]:
        print(f"  - {f}")


