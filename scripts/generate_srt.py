#!/usr/bin/env python3
"""
Generate SRT subtitle files with smart splitting for long text.

This script reads script data and audio files from a project folder,
then generates an SRT file with automatic subtitle splitting for long sentences.

Usage:
    python generate_srt.py <project_folder> [--max-words N]

Example:
    python generate_srt.py psy
    python generate_srt.py psy --max-words 10

Requirements:
    pip install mutagen
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


def format_timestamp(ms: float) -> str:
    """Convert milliseconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(ms // 3600000)
    minutes = int((ms % 3600000) // 60000)
    seconds = int((ms % 60000) // 1000)
    millis = int(ms % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def get_audio_duration_ms(audio_path: str) -> float:
    """
    Get audio duration in milliseconds from file.

    Args:
        audio_path: Path to the audio file

    Returns:
        Duration in milliseconds
    """
    if not MUTAGEN_AVAILABLE:
        raise ImportError("mutagen library is required. Install with: pip install mutagen")

    ext = Path(audio_path).suffix.lower()

    if ext == '.mp3':
        audio = MP3(audio_path)
    elif ext == '.flac':
        audio = FLAC(audio_path)
    elif ext in ('.ogg', '.oga'):
        audio = OggVorbis(audio_path)
    else:
        # Try generic mutagen for other formats
        from mutagen import File
        audio = File(audio_path)
        if audio is None:
            raise ValueError(f"Unsupported audio format: {ext}")

    return audio.info.length * 1000  # Convert seconds to milliseconds


def split_subtitle(text: str, max_words: int = 12) -> list[str]:
    """
    Split a subtitle text into segments if it exceeds max_words.

    Args:
        text: The subtitle text to split
        max_words: Maximum words per segment (default: 12)

    Returns:
        List of text segments
    """
    words = text.split()
    if len(words) <= max_words:
        return [text]

    segments = []
    while words:
        segment = words[:max_words]
        words = words[max_words:]
        segments.append(' '.join(segment))

    return segments


def calculate_timing(segments: list[str], start_ms: float, end_ms: float) -> list[dict]:
    """
    Calculate proportional timing for subtitle segments based on word count.

    Args:
        segments: List of text segments
        start_ms: Start time in milliseconds
        end_ms: End time in milliseconds

    Returns:
        List of dicts with 'text', 'start_ms', 'end_ms' for each segment
    """
    total_duration = end_ms - start_ms
    total_words = sum(len(s.split()) for s in segments)

    timings = []
    current_time = start_ms

    for segment in segments:
        word_count = len(segment.split())
        duration = total_duration * (word_count / total_words)

        timings.append({
            'text': segment,
            'start_ms': current_time,
            'end_ms': current_time + duration
        })
        current_time += duration

    return timings


def get_audio_files(audio_folder: str) -> list[str]:
    """
    Get sorted list of audio files from the audio folder.

    Args:
        audio_folder: Path to the audio folder

    Returns:
        List of audio file paths sorted by filename (audio_001.mp3, audio_002.mp3, ...)
    """
    audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
    audio_files = []

    for f in os.listdir(audio_folder):
        if Path(f).suffix.lower() in audio_extensions:
            audio_files.append(os.path.join(audio_folder, f))

    # Sort by filename to ensure correct order (audio_001, audio_002, ...)
    audio_files.sort(key=lambda x: os.path.basename(x))

    return audio_files


def load_data(project_folder: str) -> tuple[list[str], list[dict]]:
    """
    Load audio files and script data from project folder.

    Args:
        project_folder: Path to the project folder

    Returns:
        Tuple of (audio_file_paths, script_data)
    """
    audio_folder = os.path.join(project_folder, 'audio')
    script_path = os.path.join(project_folder, 'script_output.json')

    if not os.path.exists(audio_folder):
        raise FileNotFoundError(f"Audio folder not found: {audio_folder}")
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script output not found: {script_path}")

    audio_files = get_audio_files(audio_folder)

    if not audio_files:
        raise FileNotFoundError(f"No audio files found in: {audio_folder}")

    with open(script_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    return audio_files, script_data


def generate_srt(project_folder: str, max_words: int = 12, output_path: str = None) -> str:
    """
    Generate SRT file with smart subtitle splitting.

    Args:
        project_folder: Path to the project folder
        max_words: Maximum words per subtitle segment (default: 12)
        output_path: Custom output path (default: project_folder/subtitles.srt)

    Returns:
        Path to the generated SRT file
    """
    audio_files, script_data = load_data(project_folder)

    srt_content = []
    srt_index = 1
    current_time_ms = 0
    split_count = 0

    if len(audio_files) != len(script_data):
        print(f"Warning: Audio files ({len(audio_files)}) and script entries ({len(script_data)}) count mismatch")

    for i, (audio_path, script) in enumerate(zip(audio_files, script_data)):
        # Get duration directly from audio file
        duration_ms = get_audio_duration_ms(audio_path)

        start_ms = current_time_ms
        end_ms = start_ms + duration_ms

        text = script.get('script', '')
        segments = split_subtitle(text, max_words)

        if len(segments) > 1:
            split_count += 1
            print(f"  Scene {i+1}: Split into {len(segments)} segments ({len(text.split())} words)")

        timings = calculate_timing(segments, start_ms, end_ms)

        for timing in timings:
            srt_content.append(f"{srt_index}")
            srt_content.append(f"{format_timestamp(timing['start_ms'])} --> {format_timestamp(timing['end_ms'])}")
            srt_content.append(timing['text'])
            srt_content.append("")
            srt_index += 1

        current_time_ms = end_ms

    # Determine output path
    if output_path is None:
        output_path = os.path.join(project_folder, 'subtitles.srt')

    # Write SRT file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))

    return output_path, srt_index - 1, split_count


def main():
    parser = argparse.ArgumentParser(
        description='Generate SRT subtitle files with smart splitting for long text.'
    )
    parser.add_argument(
        'project_folder',
        help='Path to the project folder containing audio/ and script_output.json'
    )
    parser.add_argument(
        '--max-words', '-m',
        type=int,
        default=12,
        help='Maximum words per subtitle segment (default: 12)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Custom output path for SRT file (default: project_folder/subtitles.srt)'
    )

    args = parser.parse_args()

    # Check if mutagen is available
    if not MUTAGEN_AVAILABLE:
        print("Error: mutagen library is required. Install with: pip install mutagen")
        sys.exit(1)

    # Check if project folder exists
    if not os.path.isdir(args.project_folder):
        print(f"Error: Project folder not found: {args.project_folder}")
        sys.exit(1)

    print(f"Generating SRT for: {args.project_folder}")
    print(f"Max words per segment: {args.max_words}")
    print()

    try:
        output_path, total_entries, split_count = generate_srt(
            args.project_folder,
            max_words=args.max_words,
            output_path=args.output
        )

        print()
        print(f"SRT file generated: {output_path}")
        print(f"Total subtitle entries: {total_entries}")
        print(f"Scenes with splits: {split_count}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
