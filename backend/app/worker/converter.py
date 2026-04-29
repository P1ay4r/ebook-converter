"""
Calibre ebook-convert 调用封装。

通过 subprocess 异步调用 calibre 命令行工具，
实时解析 stderr 输出以获取转换进度。
"""

import asyncio
import os
import re
import tempfile
from typing import AsyncGenerator

from app.config import settings
from app.utils.file_utils import format_compatibility

# calibre 命令行路径
CALIBRE_CONVERT_CMD = "ebook-convert"

# 进度正则：匹配 "(X%)" 格式的进度输出
PROGRESS_RE = re.compile(r"\((\d+)%\)")


def is_calibre_available() -> bool:
    """检查系统中是否安装了 calibre。"""
    try:
        import subprocess
        result = subprocess.run(
            [CALIBRE_CONVERT_CMD, "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _build_command(input_path: str, output_path: str, options: dict | None) -> list[str]:
    """构建 calibre 命令行参数。"""
    cmd = [CALIBRE_CONVERT_CMD, input_path, output_path]

    if not options:
        return cmd

    opt_map = {
        "margin_top": "--margin-top",
        "margin_bottom": "--margin-bottom",
        "margin_left": "--margin-left",
        "margin_right": "--margin-right",
        "base_font_size": "--base-font-size",
        "line_height": "--line-height",
        "embed_fonts": "--embed-fonts",
        "compression_level": "--compression-level",
        "remove_paragraph_spacing": "--remove-paragraph-spacing",
        "extra_css": "--extra-css",
    }

    for key, value in options.items():
        if value is None:
            continue
        calibre_opt = opt_map.get(key)
        if calibre_opt is None:
            continue
        if isinstance(value, bool):
            if value:
                cmd.append(calibre_opt)
        elif key == "extra_css" and value:
            cmd.extend([calibre_opt, value])
        else:
            cmd.extend([calibre_opt, str(value)])

    return cmd


async def convert_ebook(
    input_path: str,
    output_path: str,
    options: dict | None = None,
    timeout: int = 600,
) -> AsyncGenerator[dict, None]:
    """
    异步执行 calibre 转换，实时 yield 进度。

    Yields:
        {"type": "progress", "percent": int, "message": str}
        {"type": "complete", "output_path": str}
        {"type": "error", "code": str, "message": str}
    """
    cmd = _build_command(input_path, output_path, options)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stderr_lines = []

        async def read_stderr():
            assert proc.stderr is not None
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").strip()
                stderr_lines.append(decoded)

                # 尝试解析进度
                match = PROGRESS_RE.search(decoded)
                if match:
                    percent = int(match.group(1))
                    # 将 calibre 的 0-100% 映射到我们的 5-90%
                    mapped = max(5, min(90, percent))
                    yield {"type": "progress", "percent": mapped, "message": decoded}

        progress_gen = read_stderr()

        try:
            async for progress in progress_gen:
                yield progress

            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            retcode = await proc.wait()

            if retcode != 0:
                error_text = "\n".join(stderr_lines[-20:])  # 最后 20 行错误信息
                yield {
                    "type": "error",
                    "code": "calibre_error",
                    "message": f"Calibre 返回错误码 {retcode}: {error_text}",
                }
                return

            # 校验输出
            if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
                yield {
                    "type": "error",
                    "code": "output_invalid",
                    "message": "转换完成但输出文件为空或不存在",
                }
                return

            yield {"type": "complete", "output_path": output_path}

        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            yield {
                "type": "error",
                "code": "timeout",
                "message": f"转换超时（{timeout}s），请尝试较小的文件",
            }

    except FileNotFoundError:
        yield {
            "type": "error",
            "code": "calibre_not_found",
            "message": "未找到 calibre，请确保已安装并加入 PATH",
        }
    except Exception as e:
        yield {
            "type": "error",
            "code": "unexpected_error",
            "message": f"转换过程异常: {str(e)}",
        }
