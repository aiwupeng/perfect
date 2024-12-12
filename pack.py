import streamlit as st
import streamlit.web.cli as stcli

def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("perfect.py"),  # 替换为你的Streamlit应用的主文件
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())

from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('streamlit')

[theme]
primaryColor="#1576fe"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F5F7FA"
textColor="#212121"
font="sans serif"

[server]
port=8552
headless=true

[browser]
gatherUsageStats = false

[global]
developmentMode = false