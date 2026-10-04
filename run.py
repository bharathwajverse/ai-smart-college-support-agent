"""
Convenient launch script for CampusResolve AI.
Runs Uvicorn server with automatic open port detection.
"""

import os
import sys
import socket
import uvicorn


def find_available_port(preferred_port: int = 8000, host: str = "127.0.0.1") -> int:
    for port in [preferred_port, 8080, 8001, 8081, 8888]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    return preferred_port


if __name__ == "__main__":
    port = int(os.getenv("PORT", 0)) or find_available_port(8000)
    print("================================================================")
    print("🚀 Starting CampusResolve AI - Smart College Support Agent")
    print("   Foundations of Artificial Intelligence (FAI) Project")
    print(f"   Open your browser at: http://localhost:{port}")
    print("================================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=True)
