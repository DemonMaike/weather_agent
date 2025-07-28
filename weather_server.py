#!/usr/bin/env python3
"""
Weather MCP Server - точка входа для Claude Desktop
"""
import sys
import os

# Добавляем src в Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.weather_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()