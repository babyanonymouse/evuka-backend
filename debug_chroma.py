import sqlite3
import sys

print(f"Python Version: {sys.version}")
print(f"SQLite Version: {sqlite3.sqlite_version}")

try:
    import chromadb
    client = chromadb.PersistentClient(path="./test_db")
    print("ChromaDB initialized successfully.")
except Exception as e:
    print(f"ChromaDB Error: {e}")
