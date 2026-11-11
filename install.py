#!/usr/bin/env python3
"""
================================================================================
Antigravity Comic Neubrutalism Theme - Universal 1-Click Installer
Supports: Linux, macOS, and Windows
Zero external dependencies (uses standard Python library only)
================================================================================
"""

import os
import sys
import glob
import json
import base64
import socket
import urllib.request
from pathlib import Path

THEME_CSS_FILE = Path(__file__).parent / "theme.css"

def get_platform_info():
    p = sys.platform.lower()
    if p.startswith("linux"):
        return "Linux"
    elif p.startswith("darwin"):
        return "macOS"
    elif p.startswith("win") or p == "cygwin":
        return "Windows"
    return "Unknown"

def find_candidate_ports():
    ports = set()
    plat = get_platform_info()
    home = Path.home()

    candidates = [
        Path("/tmp/antigravity-cdp-port")
    ]

    if plat == "Linux":
        candidates.extend([
            home / ".config" / "Antigravity-Profiles",
            home / ".config" / "Antigravity",
            Path("/run/user") / str(os.getuid()) / "antigravity"
        ])
    elif plat == "macOS":
        candidates.extend([
            home / "Library" / "Application Support" / "Antigravity-Profiles",
            home / "Library" / "Application Support" / "Antigravity"
        ])
    elif plat == "Windows":
        appdata = os.environ.get("APPDATA")
        localappdata = os.environ.get("LOCALAPPDATA")
        if appdata:
            candidates.append(Path(appdata) / "Antigravity-Profiles")
            candidates.append(Path(appdata) / "Antigravity")
        if localappdata:
            candidates.append(Path(localappdata) / "Antigravity-Profiles")
            candidates.append(Path(localappdata) / "Antigravity")

    # Search for DevToolsActivePort files
    for root in candidates:
        if not root.exists():
            continue
        if root.is_file():
            try:
                with open(root, "r", encoding="utf-8") as f:
                    val = f.readline().strip()
                    if val.isdigit():
                        ports.add(int(val))
            except Exception:
                pass
        elif root.is_dir():
            for p_file in root.glob("**/DevToolsActivePort"):
                try:
                    with open(p_file, "r", encoding="utf-8") as f:
                        val = f.readline().strip()
                        if val.isdigit():
                            ports.add(int(val))
                except Exception:
                    pass

    return sorted(ports)

def raw_ws_evaluate(host, port, path, js_expression):
    """
    Pure Python RFC 6455 WebSocket client to execute CDP Runtime.evaluate
    with zero external dependencies.
    """
    s = socket.create_connection((host, port), timeout=3.0)
    key = base64.b64encode(os.urandom(16)).decode("utf-8")
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    s.sendall(req.encode("utf-8"))

    # Receive HTTP Upgrade handshake
    res = b""
    while b"\r\n\r\n" not in res:
        chunk = s.recv(1024)
        if not chunk:
            break
        res += chunk

    # Build WebSocket text frame
    payload = json.dumps({
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_expression,
            "returnByValue": True
        }
    }).encode("utf-8")

    L = len(payload)
    if L < 126:
        header = bytes([0x81, 0x80 | L])
    elif L < 65536:
        header = bytes([0x81, 0x80 | 126, (L >> 8) & 0xff, L & 0xff])
    else:
        header = bytes([0x81, 0x80 | 127]) + L.to_bytes(8, "big")

    mask = os.urandom(4)
    masked_payload = bytes([b ^ mask[i % 4] for i, b in enumerate(payload)])
    s.sendall(header + mask + masked_payload)

    # Read response
    s.settimeout(2.0)
    try:
        reply = s.recv(4096)
    except Exception:
        pass
    finally:
        s.close()

def inject_theme(css_content):
    ports = find_candidate_ports()
    if not ports:
        print("[!] No active Antigravity CDP debug ports found.")
        print("    If Antigravity is not running with remote debugging, launch it with:")
        print("    --remote-debugging-port=0")
        return False

    success_count = 0
    js_snippet = f"""(() => {{
        let el = document.getElementById("antigravity-comic-theme-style");
        if (!el) {{
            el = document.createElement("style");
            el.id = "antigravity-comic-theme-style";
            (document.head || document.documentElement).appendChild(el);
        }}
        el.textContent = {json.dumps(css_content)};
        return "Theme applied successfully!";
    }})()"""

    for port in ports:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/json")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                targets = json.loads(resp.read().decode())
        except Exception:
            continue

        for target in targets:
            if target.get("type") != "page":
                continue
            path = target.get("devtoolsFrontendUrl", "").split("?")[-1]
            ws_url = target.get("webSocketDebuggerUrl")
            ws_path = f"/devtools/page/{target['id']}"

            try:
                raw_ws_evaluate("127.0.0.1", port, ws_path, js_snippet)
                title = target.get("title", "Antigravity Window")
                print(f"  ✓ Injected into '{title}' (Port {port})")
                success_count += 1
            except Exception as e:
                pass

    return success_count > 0

def persist_theme_profile(css_content):
    """
    Saves theme.css into the user's Antigravity profile directory
    for persistent loading on boot.
    """
    plat = get_platform_info()
    home = Path.home()
    target_dirs = []

    if plat == "Linux":
        target_dirs.append(home / ".config" / "Antigravity" / "themes")
        target_dirs.append(home / ".config" / "antigravity-custom-theme")
        target_dirs.append(home / ".config" / "Antigravity-Profiles" / "themes")
    elif plat == "macOS":
        target_dirs.append(home / "Library" / "Application Support" / "Antigravity" / "themes")
        target_dirs.append(home / "Library" / "Application Support" / "Antigravity-Profiles" / "themes")
    elif plat == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            target_dirs.append(Path(appdata) / "Antigravity" / "themes")
            target_dirs.append(Path(appdata) / "Antigravity-Profiles" / "themes")

    for d in target_dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            theme_out = d / "antigravity-comic-theme.css"
            with open(theme_out, "w", encoding="utf-8") as f:
                f.write(css_content)
            print(f"  ✓ Persisted theme to: {theme_out}")
        except Exception:
            pass

def main():
    print("=" * 64)
    print("  🎨 Antigravity Comic Neubrutalism Theme Installer")
    print(f"  Platform: {get_platform_info()} | Python: {sys.version.split()[0]}")
    print("=" * 64)

    if not THEME_CSS_FILE.exists():
        print(f"[x] Error: theme.css not found at {THEME_CSS_FILE}")
        sys.exit(1)

    with open(THEME_CSS_FILE, "r", encoding="utf-8") as f:
        css = f.read()

    print("[*] Persisting theme file to system configuration...")
    persist_theme_profile(css)

    print("\n[*] Hot-reloading theme into active Antigravity instances...")
    ok = inject_theme(css)

    print("\n" + "=" * 64)
    if ok:
        print("  🎉 SUCCESS: Comic Neubrutalism theme is active and live!")
    else:
        print("  ✓ Theme files installed. Launch Antigravity to enjoy the new theme!")
    print("=" * 64)

if __name__ == "__main__":
    main()
