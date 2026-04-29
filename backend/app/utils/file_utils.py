import hashlib
import os


SUPPORTED_FORMATS = {"epub", "mobi", "azw3", "pdf", "txt", "docx", "html", "fb2", "cbz", "cbr"}

# 通过文件魔数检测格式
MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    "epub": [b"PK\x03\x04"],        # ZIP-based
    "pdf": [b"%PDF"],
    "mobi": [b"BOOKMOBI", b"TEXtREAd"],
    "docx": [b"PK\x03\x04"],        # ZIP-based
    "html": [b"<html", b"<!DOCTYPE html"],
    "fb2": [b"<?xml "],
}

# 更精确的区分：epub vs docx vs cbz 都是 ZIP，需要额外的检测
# 这里先以扩展名为准，calibre 会自动进一步检测


def detect_format(filename: str) -> str | None:
    """通过文件扩展名检测格式，转为小写。"""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    # 处理 azw3 / cbz / cbr 等
    return ext if ext in SUPPORTED_FORMATS else None


def compute_file_hash(filepath: str) -> str:
    """计算文件 SHA256 哈希。"""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def get_file_ext(format: str) -> str:
    """根据格式返回文件扩展名（带点）。"""
    return f".{format}"


def format_compatibility() -> dict[str, list[str]]:
    """返回格式兼容性矩阵。"""
    return {
        "epub": ["mobi", "azw3", "pdf", "txt", "docx", "html", "fb2"],
        "mobi": ["epub", "azw3", "pdf", "txt", "docx", "html"],
        "azw3": ["epub", "mobi", "pdf", "txt", "docx", "html"],
        "pdf": ["epub", "mobi", "txt", "docx", "html"],
        "txt": ["epub", "mobi", "pdf", "docx", "html", "fb2"],
        "docx": ["epub", "mobi", "pdf", "txt", "html", "fb2"],
        "html": ["epub", "mobi", "pdf", "txt", "docx", "fb2"],
        "fb2": ["epub", "mobi", "pdf", "txt", "docx", "html"],
        "cbz": ["pdf"],
        "cbr": ["pdf"],
    }


def is_compatible(source: str, target: str) -> bool:
    """检查源格式到目标格式是否可转换。"""
    matrix = format_compatibility()
    return source in matrix and target in matrix[source]
