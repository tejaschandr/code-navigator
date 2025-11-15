#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from .indexer import CodeIndexer
from .query import CodeNavigator
from .utils import get_db_path

def main():
    parser = argparse.ArgumentParser(description="Navigate codebases with AI")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    index_parser = subparsers.add_parser('index', help='Index a codebase')
    index_parser.add_argument('path', nargs='?', default='.', help='Path to codebase (default: current directory)')
    
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('question', nargs='+', help='Your question')
    ask_parser.add_argument('--codebase', '-c', default='.', help='Path to indexed codebase')
    
    chat_parser = subparsers.add_parser('chat', help='Interactive chat mode')
    chat_parser.add_argument('--codebase', '-c', default='.', help='Path to indexed codebase')

    clean_parser = subparsers.add_parser('clean', help='Delete index for a codebase')
    clean_parser.add_argument('path', nargs='?', default='.', help='Path to codebase')
    clean_parser.add_argument('--all', action='store_true', help='Delete all indexes')

    list_parser = subparsers.add_parser('list', help='List all indexed projects')
    
    stats_parser = subparsers.add_parser('stats', help='Show index statistics')
    stats_parser.add_argument('--codebase', '-c', default='.', help='Path to indexed codebase')
    
    args = parser.parse_args()
    
    if args.command == 'index':
        target_path = Path(args.path).resolve()
        db_path = get_db_path(target_path)
        
        print(f" Indexing: {target_path}")
        print(f" Database: {db_path}")
        
        indexer = CodeIndexer(db_path=str(db_path))
        indexer.index_repository(str(target_path))
    
    elif args.command == 'ask':
        codebase_path = Path(args.codebase).resolve()
        db_path = get_db_path(codebase_path)
        
        if not Path(db_path).exists():
            print(f" No index found at {codebase_path}")
            print(f"   Run: cn index {codebase_path}")
            sys.exit(1)
        
        question = ' '.join(args.question)
        nav = CodeNavigator(db_path=str(db_path))
        nav.ask(question)
    
    elif args.command == 'chat':
        codebase_path = Path(args.codebase).resolve()
        db_path = get_db_path(codebase_path)
        
        if not Path(db_path).exists():
            print(f" No index found at {codebase_path}")
            print(f"   Run: cn index {codebase_path}")
            sys.exit(1)
        
        nav = CodeNavigator(db_path=str(db_path))
        
        print("=" * 60)
        print(f"Codebase Navigator - {codebase_path.name}")
        print("=" * 60)
        print(f"Indexed chunks: {nav.collection.count()}")
        print("\nAsk questions (or 'quit' to exit)")
        print("=" * 60)
        
        while True:
            question = input("\n You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            nav.ask(question)
    
    elif args.command == 'stats':
        codebase_path = Path(args.codebase).resolve()
        db_path = get_db_path(codebase_path)
        
        if not Path(db_path).exists():
            print(f"No index found at {codebase_path}")
            sys.exit(1)
        
        indexer = CodeIndexer(db_path=str(db_path))
        indexer.get_stats()

    elif args.command == "list":
        global_dir = Path.home() / '.codebase-nav'
    
        if not global_dir.exists() or not list(global_dir.iterdir()):
            print("No indexed projects found")
            return
        
        print("Indexed Projects:\n")
        
        for index_dir in sorted(global_dir.iterdir()):
            if index_dir.is_dir():
                size = sum(f.stat().st_size for f in index_dir.rglob('*') if f.is_file())
                size_mb = size / (1024 * 1024)
                
                mtime = index_dir.stat().st_mtime
                from datetime import datetime
                modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                
                print(f"  • {index_dir.name}")
                print(f"    Size: {size_mb:.1f} MB")
                print(f"    Last indexed: {modified}")
                print()
    
    elif args.command == 'clean':
        if args.all:
            global_dir = Path.home() / '.codebase-nav'
            if global_dir.exists():
                import shutil
                shutil.rmtree(global_dir)
                print("Deleted all indexes")
            else:
                print("No indexes found")
        else:
            target_path = Path(args.path).resolve()
            db_path = Path(get_db_path(target_path))
            
            if db_path.exists():
                import shutil
                shutil.rmtree(db_path)
                print(f"Deleted index for {target_path.name}")
            else:
                print(f"No index found for {target_path}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()