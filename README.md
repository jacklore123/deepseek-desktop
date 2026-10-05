# DeepSeek 桌面版（Windows 一键安装）

把 DeepSeek 网页版（<https://chat.deepseek.com/>）变成 Windows 上的一个独立窗口应用，
并自动创建桌面快捷方式、开始菜单项和开机启动。

> 这不是 DeepSeek 官方安装器，而是一个轻量外壳：用系统自带的 Edge / Chrome 以
> App 模式打开 DeepSeek 网页，省掉「开浏览器 → 找标签页」的步骤。

## 仓库文件

| 文件 | 说明 |
| --- | --- |
| `DeepSeek_Setup.exe` | 图形安装程序，双击即用（v1.0.0） |
| `DeepSeek.py` | 同一功能的 Python 脚本版 |

## 用 Python 脚本版

```powershell
python DeepSeek.py                 # 安装快捷方式、开启自启动并立即打开
python DeepSeek.py --no-autostart  # 只装快捷方式，不开自启动
python DeepSeek.py --launch-only   # 只打开，不创建快捷方式
python DeepSeek.py --uninstall     # 删除本脚本创建的快捷方式和自启动
```

## 说明

- 仅支持 Windows，依赖系统自带的 Edge 或 Chrome。
- 卸载：运行 `python DeepSeek.py --uninstall`，或直接删除快捷方式。

## 许可

MIT License，见 [LICENSE](LICENSE)。
