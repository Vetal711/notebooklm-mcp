import os
import re
import sys
from pathlib import Path

# Paths to the target package
APPDATA_PATH = Path(os.environ.get("APPDATA", os.path.expanduser("~")))
MCP_PKG_DIR = APPDATA_PATH / "Python" / "Python314" / "site-packages" / "notebooklm_mcp"

def patch_file(filepath: Path, patches: list[tuple[str, str, str]]):
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    original_content = content
    
    for name, search_pattern, replace_str in patches:
        if re.search(search_pattern, content, re.MULTILINE):
            content = re.sub(search_pattern, replace_str, content, count=1, flags=re.MULTILINE)
            print(f"[OK] Applied patch: {name} in {filepath.name}")
        else:
            print(f"[WARN] Could not find pattern for {name} in {filepath.name}")
            
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[SAVED] Saved {filepath.name}\n")
    else:
        print(f"[SKIP] No changes made to {filepath.name}\n")

def main():
    if not MCP_PKG_DIR.exists():
        print(f"Error: Could not find notebooklm_mcp at {MCP_PKG_DIR}")
        sys.exit(1)
        
    print(f"Patching notebooklm_mcp at: {MCP_PKG_DIR}\n")
    
    # 1. Patch config.py
    config_file = MCP_PKG_DIR / "config.py"
    config_patches = [
        (
            "Fix 2: Absolute profile_dir",
            r'profile_dir:\s*str\s*=\s*"./chrome_profile_notebooklm"',
            'profile_dir: str = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "notebooklm-mcp", "chrome_profile")'
        )
    ]
    patch_file(config_file, config_patches)
    
    # 2. Patch client.py
    client_file = MCP_PKG_DIR / "client.py"
    
    detect_chrome_func = """
    def _detect_chrome_major(self) -> int | None:
        import re, subprocess, winreg
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                k = winreg.OpenKey(hive, r"Software\\\\Google\\\\Chrome\\\\BLBeacon")
                ver, _ = winreg.QueryValueEx(k, "version")
                return int(ver.split(".")[0])
            except OSError:
                continue
        for p in (r"%ProgramFiles%\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe",
                  r"%ProgramFiles(x86)%\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe"):
            import os
            p = os.path.expandvars(p)
            if os.path.exists(p):
                try:
                    out = subprocess.run([p, "--version"], capture_output=True, text=True).stdout
                    m = re.search(r"(\\\\d+)\\\\\\\\.", out)
                    if m: return int(m.group(1))
                except Exception:
                    pass
        return None

    def _start_browser(self)"""

    start_browser_replace = """self.driver = uc.Chrome(options=options, version_main=self._detect_chrome_major())"""

    mojibake_replace = """        # Send message using JS to avoid Cyrillic mojibake
        self.driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
            chat_input, message
        )"""

    auth_error_replace = """logger.warning("❌ Authentication required - need manual login. Run: notebooklm-mcp init \\"<url>\\"")"""

    get_response_replace = """        response_selectors = [
            "[data-message-author='model']",
            ".message-content",
            "[data-testid*='response']",
            "[class*='message']:last-child",
            "[class*='response']:last-child",
        ]"""
    
    clean_response_replace = """        ui_artifacts = [
            "copy_all", "thumb_up", "thumb_down", "share", "more_options", 
            "like", "dislike", "arrow_forward", "volume_up", "volume_off",
            "content_copy"
        ]"""

    client_patches = [
        (
            "Fix 1.1: Inject _detect_chrome_major",
            r'def _start_browser\(self\)',
            detect_chrome_func
        ),
        (
            "Fix 1.2: Use dynamic version_main",
            r'self\.driver\s*=\s*uc\.Chrome\(options=options,\s*version_main=(?:None|149)\)',
            start_browser_replace
        ),
        (
            "Fix 4: Auth error message",
            r'logger\.warning\("❌ Authentication required - need manual login"\)',
            auth_error_replace
        ),
        (
            "Fix 6: Cyrillic input via JS",
            r'chat_input\.clear\(\)\n\s*chat_input\.send_keys\(message\)',
            mojibake_replace
        ),
        (
            "Fix 5.1: Better response selectors",
            r'response_selectors\s*=\s*\[[^\]]+\]',
            get_response_replace
        ),
        (
            "Fix 5.2: Filter out arrow_forward",
            r'ui_artifacts\s*=\s*\[[\s\S]*?\]',
            clean_response_replace
        )
    ]
    patch_file(client_file, client_patches)
    
    # 3. Patch cli (to fix UTF-8 encoding)
    for cli_filename in ["cli.py", "server.py", "__main__.py", "notebooklm_cli.py"]:
        cli_file = MCP_PKG_DIR / cli_filename
        if cli_file.exists():
            cli_patches = [
                (
                    "Fix 3: UTF-8 encoding",
                    r'(import sys\n)',
                    r'\1try:\n    sys.stdout.reconfigure(encoding="utf-8", errors="replace")\n    sys.stderr.reconfigure(encoding="utf-8", errors="replace")\nexcept Exception:\n    pass\n\n'
                )
            ]
            patch_file(cli_file, cli_patches)
            break
    
    print("Done patching.")

if __name__ == "__main__":
    main()
