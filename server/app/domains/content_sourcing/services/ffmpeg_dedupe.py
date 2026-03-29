"""
FFmpeg Deduplication Service
============================
Provides two levels of video deduplication to bypass platform re-up detection:
  - apply_light_dedupe: strips metadata + changes MD5 without visual re-encoding
  - apply_deep_dedupe:  visual/audio transformation (hflip + speed change)

D-04 from 03-CONTEXT.md: Configurable deduplication level (Admin can switch).
"""

import ffmpeg


def apply_light_dedupe(input_path: str, output_path: str) -> str:
    """
    Strip ALL metadata (Exif, ID3 tags) and copy streams without re-encoding.
    Changes the file's MD5 hash without touching visual/audio quality.

    Strategy: Siêu Nhẹ — Metadata Wipe only.

    Args:
        input_path: Path to the source video file.
        output_path: Path where the processed output will be saved.

    Returns:
        output_path on success.

    Raises:
        ffmpeg.Error: If FFmpeg processing fails.
    """
    try:
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                map_metadata=-1,   # Strip all metadata
                vcodec='copy',     # Copy video stream (no re-encode)
                acodec='copy',     # Copy audio stream (no re-encode)
            )
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        stderr = e.stderr.decode() if e.stderr else "Unknown FFmpeg error"
        raise RuntimeError(f"apply_light_dedupe failed: {stderr}") from e


def apply_deep_dedupe(input_path: str, output_path: str) -> str:
    """
    Apply visual and audio transformations to evade fingerprint-based detection.
    Applies: horizontal flip + slight video speed increase + matching audio tempo.

    Strategy: Xào Sâu — Video flip + speed change (1.05x) + audio sync.

    Args:
        input_path: Path to the source video file.
        output_path: Path where the processed output will be saved.

    Returns:
        output_path on success.

    Raises:
        ffmpeg.Error: If FFmpeg processing fails.
    """
    try:
        stream = ffmpeg.input(input_path)
        video = (
            stream.video
            .filter('hflip')              # Mirror horizontally
            .filter('setpts', '0.95*PTS') # Speed up to 1.05x
        )
        audio = (
            stream.audio
            .filter('atempo', 1.05)       # Match audio tempo to video speed
        )
        (
            ffmpeg
            .output(video, audio, output_path, map_metadata=-1)
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        stderr = e.stderr.decode() if e.stderr else "Unknown FFmpeg error"
        raise RuntimeError(f"apply_deep_dedupe failed: {stderr}") from e


# Dedupe mode constants for campaign configuration
DEDUPE_MODE_LIGHT = "light"
DEDUPE_MODE_DEEP = "deep"


def apply_dedupe(input_path: str, output_path: str, mode: str = DEDUPE_MODE_LIGHT) -> str:
    """
    Dispatch deduplication based on configured mode.

    Args:
        input_path: Source video path.
        output_path: Output video path.
        mode: "light" (metadata wipe only) or "deep" (flip + speed change).

    Returns:
        output_path on success.
    """
    if mode == DEDUPE_MODE_DEEP:
        return apply_deep_dedupe(input_path, output_path)
    return apply_light_dedupe(input_path, output_path)
