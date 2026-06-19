import os
import json
import sys

def update_json_file(file_path, server_name, command):
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        return False

    if not os.path.exists(file_path):
        data = {"mcpServers": {}}
    else:
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading JSON from {file_path}. Is it valid?")
            return False

    if "mcpServers" not in data:
        data["mcpServers"] = {}

    server_config = {
        "command": command,
        "args": []
    }

    if "venv" in command:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(command)))
        cli_path = os.path.join(base_dir, "venv", "Scripts", "notebooklm.exe")
        log_path = os.path.join(base_dir, "logs", "notebooklm-mcp.log")
        server_config["env"] = {
            "NOTEBOOKLM_CLI": cli_path,
            "LOG_FILE": log_path
        }

    data["mcpServers"][server_name] = server_config

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully added {server_name} to {file_path}")
    return True

def main():
    print("NotebookLM MCP Server - Auto-Installer")
    
    python_executable = os.path.join(os.getcwd(), "venv", "Scripts", "notebooklm-mcp.exe")
    if not os.path.exists(python_executable):
        python_executable = "notebooklm-mcp" # Fallback to global command
    
    print(f"Using server command: {python_executable}")

    user_home = os.path.expanduser("~")
    
    # Target configurations
    configs = [
        # Claude Desktop
        os.path.join(user_home, "AppData", "Roaming", "Claude", "claude_desktop_config.json"),
        # Cursor
        os.path.join(user_home, "AppData", "Roaming", "Cursor", "User", "globalStorage", "rooveterinaryinc.roo-cline", "settings", "cline_mcp_settings.json"),
        # Antigravity / Gemini
        os.path.join(user_home, ".gemini", "config", "mcp_config.json")
    ]
    
    success = False
    for conf in configs:
        if os.path.exists(conf):
            if update_json_file(conf, "NotebookLM", python_executable):
                success = True
                
    if not success:
        print("\nNo supported IDE configuration files found automatically.")
        print("Please add the MCP server manually in your IDE settings.")
    else:
        print("\nInstallation complete! Please restart your AI agent/IDE.")

if __name__ == "__main__":
    main()
