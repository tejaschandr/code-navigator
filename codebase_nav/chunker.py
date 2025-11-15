import re
from pathlib import Path

class CodeChunker:
    def chunk_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        chunks = []
        
        if filepath.suffix == '.py':
            chunks = self._chunk_python(content, filepath)
        elif filepath.suffix in {'.js', '.ts', '.jsx', '.tsx'}:
            chunks = self._chunk_javascript(content, filepath)
        else:
            chunks = self._chunk_fixed_size(content, filepath)
        
        return chunks
    
    def _chunk_python(self, content, filepath):
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_name = None
        indent_level = 0
        
        for i, line in enumerate(lines):
            if re.match(r'^(def |class )', line):
                if current_chunk:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'filepath': str(filepath),
                        'name': current_name,
                        'start_line': i - len(current_chunk) + 1,
                        'end_line': i
                    })
                
                current_chunk = [line]
                match = re.search(r'(def|class)\s+(\w+)', line)
                current_name = match.group(2) if match else 'unknown'
                indent_level = len(line) - len(line.lstrip())
            
            elif current_chunk:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else indent_level + 1
                
                if line_indent > indent_level or not line.strip():
                    current_chunk.append(line)
                else:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'filepath': str(filepath),
                        'name': current_name,
                        'start_line': i - len(current_chunk),
                        'end_line': i - 1
                    })
                    current_chunk = []
                    current_name = None
        
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'filepath': str(filepath),
                'name': current_name,
                'start_line': len(lines) - len(current_chunk),
                'end_line': len(lines)
            })
        
        if not chunks:
            chunks = [{
                'content': content,
                'filepath': str(filepath),
                'name': 'module',  
                'start_line': 1,
                'end_line': len(content.split('\n'))
            }]
        
        return chunks
    
    def _chunk_javascript(self, content, filepath):
        chunks = []
        lines = content.split('\n')
        
        function_pattern = r'(function\s+\w+|const\s+\w+\s*=\s*\(.*?\)\s*=>|export\s+(default\s+)?function)'
        
        current_chunk = []
        brace_count = 0
        in_function = False
        current_name = None
        
        for i, line in enumerate(lines):
            if re.search(function_pattern, line):
                if current_chunk and in_function:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'filepath': str(filepath),
                        'name': current_name,
                        'start_line': i - len(current_chunk),
                        'end_line': i - 1
                    })
                
                current_chunk = [line]
                in_function = True
                match = re.search(r'(function|const)\s+(\w+)', line)
                current_name = match.group(2) if match else 'anonymous'
                brace_count = line.count('{') - line.count('}')
            
            elif in_function:
                current_chunk.append(line)
                brace_count += line.count('{') - line.count('}')
                
                if brace_count == 0 and '{' in ''.join(current_chunk):
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'filepath': str(filepath),
                        'name': current_name,
                        'start_line': i - len(current_chunk) + 1,
                        'end_line': i
                    })
                    current_chunk = []
                    in_function = False
        
        if not chunks:
            chunks = self._chunk_fixed_size(content, filepath)
        
        return chunks
    
    def _chunk_fixed_size(self, content, filepath, chunk_size=500):
        """Fallback: fixed-size chunks with overlap"""
        lines = content.split('\n')
        chunks = []
        
        for i in range(0, len(lines), chunk_size - 50):
            chunk_lines = lines[i:i + chunk_size]
            chunks.append({
                'content': '\n'.join(chunk_lines),
                'filepath': str(filepath),
                'name': f'chunk_{i}',
                'start_line': i,
                'end_line': min(i + chunk_size, len(lines))
            })
        
        return chunks

if __name__ == "__main__":
    chunker = CodeChunker()
    chunks = chunker.chunk_file(Path("scanner.py"))
    
    print(f"Found {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"\n--- {chunk['name']} (lines {chunk['start_line']}-{chunk['end_line']}) ---")
        print(chunk['content'][:200] + "...")