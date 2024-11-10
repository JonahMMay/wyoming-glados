#!/usr/bin/env python3
"""Utility for running GLaDOS TTS server."""

import argparse
import asyncio
import logging
import sys
from functools import partial
from pathlib import Path

from nltk import download as nltk_download
from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer

# Ensure 'gladostts' module is importable
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from gladostts.glados import tts_runner
from gladostts.server.handler import GladosEventHandler

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the GLaDOS TTS server."""
    parser = argparse.ArgumentParser(description="GLaDOS TTS Server")
    parser.add_argument(
        "--uri", default="stdio://", help="Server URI (e.g., 'unix://', 'tcp://')"
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default="./models",
        help="Directory containing the model files",
    )
    parser.add_argument(
        "--auto-punctuation",
        default=".?!",
        help="Characters to use for automatic punctuation",
    )
    parser.add_argument(
        "--samples-per-chunk",
        type=int,
        default=1024,
        help="Number of samples per audio chunk",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    # Define TTS voices
    voices = [
        TtsVoice(
            name="default",
            description="Default GLaDOS voice",
            attribution=Attribution(
                name="R2D2FISH", url="https://github.com/R2D2FISH/glados-tts"
            ),
            installed=True,
            languages=["en"],
            version=2,
        )
    ]

    # Define TTS program information
    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="glados-tts",
                description="A GLaDOS TTS using Forward Tacotron and HiFiGAN.",
                attribution=Attribution(
                    name="R2D2FISH", url="https://github.com/R2D2FISH/glados-tts"
                ),
                installed=True,
                voices=voices,
                version=2,
            )
        ],
    )

    # Initialize GLaDOS TTS
    models_dir = Path(args.models_dir).resolve()
    glados_tts = tts_runner(
        gpu=True, full_english=False, models_dir=str(models_dir)
    )

    # Download necessary NLTK data
    nltk_download("punkt", quiet=True)

    # Start the server
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("GLaDOS TTS server is ready.")
    await server.run(
        partial(GladosEventHandler, wyoming_info, args, glados_tts)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Server shutdown requested. Exiting...")
