"""Utility for downloading gladostts models"""

import argparse
import hashlib
import logging
import shutil
from pathlib import Path
from typing import Union
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import urlopen

DEFAULT_URL = "https://github.com/nalf3in/glados-tts/releases/download/v0.1.0-alpha/{file}"
DEFAULT_MODEL_DIR = "./gladostts/models"

_LOGGER = logging.getLogger(__name__)


def _quote_url(url: str) -> str:
    """Quote the file part of the URL in case it contains UTF-8 characters."""
    parts = list(urlsplit(url))
    parts[2] = quote(parts[2])
    return urlunsplit(parts)


def get_file_hash(path: Union[str, Path], bytes_per_chunk: int = 8192) -> str:
    """Calculate the MD5 hash of a file in chunks."""
    md5_hash = hashlib.md5()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(bytes_per_chunk), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def ensure_model_exists(download_dir: Union[str, Path], base_url: str):
    download_dir = Path(download_dir)

    # List of model files and their expected MD5 checksums
    model_files = [
        {"filename": "glados-new.pt", "md5": "d6945ffd96ee0619d0d49a581b5b83ad"},
        {"filename": "glados.pt", "md5": "11383a00f7ddfc8f80285ce3aba2ebb0"},
        {"filename": "en_us_cmudict_ipa_forward.pt", "md5": "33887f7f579f010ce4463534306120b0"},
        {"filename": "emb/glados_p2.pt", "md5": "ff2ad1438e9acb1f8e8607864c239ffc"},
        {"filename": "emb/glados_p1.pt", "md5": "e0ffe67a6f53c4ff0b3952fc678946d9"},
        {"filename": "vocoder-gpu.pt", "md5": "d35c13c01d2cacd348aa216649bbfac3"},
        {"filename": "vocoder-cpu-hq.pt", "md5": "e8842210dc989e351c2e50614ff55f46"},
        {"filename": "vocoder-cpu-lq.pt", "md5": "cfd048af8bb8190995eac7b95bf7367e"},
    ]

    for model in model_files:
        model_file = model["filename"]
        model_file_path = download_dir / model_file
        model_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine if the file needs to be downloaded
        need_download = True
        if model_file_path.exists():
            if model_file_path.stat().st_size >= 1024:
                md5_hash = get_file_hash(model_file_path)
                if md5_hash == model["md5"]:
                    need_download = False
                else:
                    _LOGGER.warning(
                        "MD5 hash mismatch for %s. Expected %s, got %s.",
                        model_file_path,
                        model["md5"],
                        md5_hash,
                    )
                    model_file_path.unlink()
            else:
                _LOGGER.warning("File %s is too small. Re-downloading.", model_file_path)
                model_file_path.unlink()

        if need_download:
            try:
                model_url = base_url.format(file=model_file)
                _LOGGER.info("Downloading %s to %s", model_url, model_file_path)
                with urlopen(_quote_url(model_url)) as response, open(
                    model_file_path, "wb"
                ) as out_file:
                    shutil.copyfileobj(response, out_file)
                _LOGGER.info("Downloaded %s", model_file_path)
            except Exception:
                _LOGGER.exception(
                    "Failed to download %s from %s",
                    model_file_path,
                    _quote_url(model_url),
                )
                if model_file_path.exists():
                    model_file_path.unlink()  # Remove incomplete file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Downloader")
    parser.add_argument(
        "--model_dir",
        type=str,
        default=DEFAULT_MODEL_DIR,
        help="Directory for the models",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help="URL for downloading models",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    ensure_model_exists(args.model_dir, args.url)
