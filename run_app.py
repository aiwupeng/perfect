import streamlit as st
import streamlit.web.cli as stcli
import sys
import os

def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app.py"),  # 替换为你的Streamlit应用的主文件
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
