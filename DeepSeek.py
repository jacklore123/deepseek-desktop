#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 轻量桌面安装/启动脚本（仅限 Windows）。

用途：
    使用系统自带的 Edge 或 Chrome，把 DeepSeek 网页版做成独立的 App 窗口，
    并创建桌面、开始菜单和开机启动快捷方式。

常用命令：
    python DeepSeek.py                 # 安装快捷方式、开启自启动并立即打开
    python DeepSeek.py --no-autostart  # 安装快捷方式，但不开启自启动
    python DeepSeek.py --launch-only   # 只打开，不创建快捷方式
    python DeepSeek.py --uninstall     # 删除本脚本创建的快捷方式和自启动
"""

import argparse
import base64
import os
import subprocess
import sys


APP_URL = "https://chat.deepseek.com/"
APP_NAME = "DeepSeek"


def _candidates():
    env = os.environ
    pf86 = env.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    pf = env.get("ProgramFiles", r"C:\Program Files")
    local = env.get("LOCALAPPDATA", os.path.expanduser("~"))
    return [
        os.path.join(pf86, "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(pf, "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(local, "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(pf86, "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(pf, "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
    ]


def _ps_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def _run_powershell(script):
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def find_browser():
    for path in _candidates():
        if path and os.path.isfile(path):
            return path
    return None


def user_data_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "DeepSeekWeb")


def browser_arguments():
    args = [
        "--app=" + APP_URL,
        "--user-data-dir=" + user_data_dir(),
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1240,820",
    ]
    return args


def desktop_dir():
    return os.environ.get("USERPROFILE") and os.path.join(
        os.environ["USERPROFILE"], "Desktop"
    ) or os.path.expanduser("~/Desktop")


def start_menu_dir():
    return os.path.join(
        os.environ.get("APPDATA", os.path.expanduser("~/AppData/Roaming")),
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
    )


def startup_dir():
    return os.path.join(
        os.environ.get("APPDATA", os.path.expanduser("~/AppData/Roaming")),
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )


def create_shortcut(shortcut_path, browser, args, icon=None):
    directory = os.path.dirname(shortcut_path)
    os.makedirs(directory, exist_ok=True)
    argument_string = subprocess.list2cmdline(args)
    icon_string = f"{_ps_literal(icon + ',0')}" if icon else "$null"
    script = f"""
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut({_ps_literal(shortcut_path)})
$shortcut.TargetPath = {_ps_literal(browser)}
$shortcut.Arguments = {_ps_literal(argument_string)}
$shortcut.WorkingDirectory = {_ps_literal(os.path.dirname(browser))}
$shortcut.IconLocation = {icon_string}
$shortcut.Description = 'DeepSeek 桌面客户端'
$shortcut.Save()
"""
    _run_powershell(script)


def remove_if_exists(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass


def uninstall():
    desktop = os.path.join(desktop_dir(), APP_NAME + ".lnk")
    start_menu = os.path.join(start_menu_dir(), APP_NAME + ".lnk")
    startup = os.path.join(startup_dir(), APP_NAME + ".lnk")
    for path in (desktop, start_menu, startup):
        remove_if_exists(path)
        print("已删除：" + path)


def launch(browser):
    args = browser_arguments()
    creation_flags = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
    creation_flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    subprocess.Popen([browser] + args, creationflags=creation_flags)


def main():
    if sys.platform != "win32":
        print("此脚本仅支持 Windows。")
        return 1

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        import ctypes

        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="DeepSeek 轻量桌面安装/启动脚本")
    parser.add_argument("--no-autostart", action="store_true", help="不创建开机启动快捷方式")
    parser.add_argument("--launch-only", action="store_true", help="只打开，不创建快捷方式")
    parser.add_argument("--no-launch", action="store_true", help="只创建快捷方式，不立即打开")
    parser.add_argument("--uninstall", action="store_true", help="删除快捷方式和自启动")
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
        return 0

    browser = find_browser()
    if not browser:
        print("未找到 Edge 或 Chrome，请先安装其中一个浏览器。")
        return 1

    print("使用浏览器：" + browser)

    if not args.launch_only:
        create_shortcut(
            os.path.join(desktop_dir(), APP_NAME + ".lnk"),
            browser,
            browser_arguments(),
        )
        create_shortcut(
            os.path.join(start_menu_dir(), APP_NAME + ".lnk"),
            browser,
            browser_arguments(),
        )

        startup_shortcut = os.path.join(startup_dir(), APP_NAME + ".lnk")
        if args.no_autostart:
            remove_if_exists(startup_shortcut)
        else:
            create_shortcut(startup_shortcut, browser, browser_arguments())

    if not args.no_launch:
        launch(browser)

    print("完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
