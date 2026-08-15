import asyncio
import os
import shutil
import sys
from pathlib import Path
from core.logger import logger


def get_downloads_dir(subfolder: str = None) -> Path:
    """
    Cross-platform default Downloads folder resolver (Linux, Windows, macOS).
    Optionally appends a subfolder name to the path.
    """
    download_path = Path.home() / "Downloads"

    if sys.platform == "win32":
        try:
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location, _ = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')
                download_path = Path(os.path.expandvars(location))
        except Exception as e:
            logger.warning(f"Could not read Windows Registry Downloads path: {e}")
    elif sys.platform.startswith("linux"):
        xdg_config = os.path.expanduser("~/.config/user-dirs.dirs")
        if os.path.exists(xdg_config):
            try:
                with open(xdg_config, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("XDG_DOWNLOAD_DIR="):
                            path = line.split("=", 1)[1].strip().strip('"')
                            path = os.path.expandvars(path)
                            download_path = Path(os.path.expanduser(path))
                            break
            except Exception as e:
                logger.warning(f"Could not read user-dirs.dirs: {e}")

    if subfolder:
        download_path = download_path / subfolder

    return download_path


def get_ffmpeg_executable() -> str | None:
    """Find system ffmpeg or imageio_ffmpeg executable."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


async def convert_mp4_to_gif(mp4_path: Path, delete_original: bool = True) -> Path | None:
    """
    Converts an MP4 video file into an animated GIF file using ffmpeg.
    Returns the Path to the generated .gif file on success, or None on failure.
    """
    ffmpeg_exe = get_ffmpeg_executable()
    if not ffmpeg_exe:
        logger.error("ffmpeg executable not found for MP4 to GIF conversion.")
        return None

    mp4_path = Path(mp4_path)
    gif_path = mp4_path.with_suffix(".gif")

    filter_complex = "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", str(mp4_path),
        "-vf", filter_complex,
        str(gif_path)
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()

        if proc.returncode == 0 and gif_path.exists():
            if delete_original and mp4_path.exists() and mp4_path != gif_path:
                try:
                    mp4_path.unlink()
                except Exception as e:
                    logger.warning(f"Could not remove original MP4 file {mp4_path}: {e}")
            return gif_path
        else:
            cmd_simple = [ffmpeg_exe, "-y", "-i", str(mp4_path), str(gif_path)]
            proc_simple = await asyncio.create_subprocess_exec(
                *cmd_simple,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc_simple.communicate()

            if proc_simple.returncode == 0 and gif_path.exists():
                if delete_original and mp4_path.exists() and mp4_path != gif_path:
                    try:
                        mp4_path.unlink()
                    except Exception:
                        pass
                return gif_path
            else:
                logger.error(f"ffmpeg failed for {mp4_path}: {stderr.decode('utf-8', errors='ignore')}")
                return None
    except Exception as e:
        logger.exception(f"Error converting {mp4_path} to GIF: {e}")
        return None
