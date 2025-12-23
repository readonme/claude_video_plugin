#!/usr/bin/env python3
"""
Prepare batch data for CapCut video creation.

This script reads script_output.json and audio files from a project folder,
then generates images_batch.json and audios_batch.json for use with CapCut API.

Usage:
    python prepare_batch_data.py <project_folder>

Example:
    python prepare_batch_data.py /Users/zhenhaohua/code/test_empty/r2_0

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
    from mutagen import File
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# Animation lists (循环使用)
INTRO_ANIMATIONS = [
    "Fade_In", "Zoom_1", "Zoom_2", "Slide_Down", "Slide_Up",
    "Slide_Left", "Slide_Right", "Rotate", "Flip", "Mini_Zoom"
]

TRANSITIONS = [
    "Dissolve", "Mix", "Black_Fade", "White_Flash", "Blur",
    "Slide", "Wipe_Right", "Wipe_Left", "Flip", "Glitch"
]


def get_audio_duration(audio_path: str) -> float:
    """
    Get audio duration in seconds from file.

    Args:
        audio_path: Path to the audio file

    Returns:
        Duration in seconds
    """
    ext = Path(audio_path).suffix.lower()

    if ext == '.mp3':
        audio = MP3(audio_path)
    elif ext == '.flac':
        audio = FLAC(audio_path)
    else:
        audio = File(audio_path)
        if audio is None:
            raise ValueError(f"Unsupported audio format: {ext}")

    return audio.info.length


def get_image_path(images_folder: str, scene_idx: int, img_idx: int, image_count: int) -> str:
    """
    Get image path based on naming convention.

    Args:
        images_folder: Path to images folder
        scene_idx: 0-based scene index
        img_idx: 0-based image index within scene
        image_count: Total images in this scene

    Returns:
        Absolute path to image file, or None if not found
    """
    scene_num = f"{scene_idx + 1:03d}"

    if image_count == 1:
        # Single image: image_XXX.png
        path = os.path.join(images_folder, f"image_{scene_num}.png")
        if os.path.exists(path):
            return path
        # Fallback to multi-image format
        path = os.path.join(images_folder, f"image_{scene_num}_01.png")
        if os.path.exists(path):
            return path
    else:
        # Multi-image: image_XXX_YY.png
        img_num = f"{img_idx + 1:02d}"
        path = os.path.join(images_folder, f"image_{scene_num}_{img_num}.png")
        if os.path.exists(path):
            return path

    return None


def prepare_batch_data(project_folder: str) -> dict:
    """
    Prepare batch data for images and audio.

    Args:
        project_folder: Path to the project folder

    Returns:
        Dict with images_batch, audios_batch, and stats
    """
    # Load script output
    script_path = os.path.join(project_folder, 'script_output.json')
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script output not found: {script_path}")

    with open(script_path, 'r', encoding='utf-8') as f:
        script_output = json.load(f)

    # Get audio files
    audio_folder = os.path.join(project_folder, 'audio')
    if not os.path.exists(audio_folder):
        raise FileNotFoundError(f"Audio folder not found: {audio_folder}")

    audio_files = sorted([
        f for f in os.listdir(audio_folder)
        if f.endswith('.mp3') and f.startswith('audio_')
    ])
    audio_paths = [os.path.join(audio_folder, f) for f in audio_files]

    if not audio_paths:
        raise FileNotFoundError(f"No audio files found in: {audio_folder}")

    # Images folder
    images_folder = os.path.join(project_folder, 'images')
    if not os.path.exists(images_folder):
        raise FileNotFoundError(f"Images folder not found: {images_folder}")

    # Prepare batch data
    accumulated_time = 0
    total_duration = 0
    images_batch = []
    audios_batch = []
    warnings = []

    # Process each scene
    for scene_idx, scene in enumerate(script_output):
        if scene_idx >= len(audio_paths):
            warnings.append(f"Scene {scene_idx + 1}: No corresponding audio file")
            break

        audio_path = audio_paths[scene_idx]
        audio_duration = get_audio_duration(audio_path)

        image_count = scene.get('image_count', 1)
        per_image_duration = audio_duration / image_count
        scene_start = accumulated_time

        # Get animation for this scene
        intro_animation = INTRO_ANIMATIONS[scene_idx % len(INTRO_ANIMATIONS)]
        transition = TRANSITIONS[scene_idx % len(TRANSITIONS)]

        # Add images for this scene
        for img_idx in range(image_count):
            image_path = get_image_path(images_folder, scene_idx, img_idx, image_count)
            if image_path is None:
                warnings.append(f"Scene {scene_idx + 1}: Missing image {img_idx + 1}/{image_count}")
                continue

            img_start = scene_start + (img_idx * per_image_duration)
            img_end = img_start + per_image_duration

            image_config = {
                "image_url": image_path,
                "start": round(img_start, 3),
                "end": round(img_end, 3),
                "track_name": "main"
            }

            # Only add animation to first image of scene
            if img_idx == 0:
                image_config["intro_animation"] = intro_animation
                image_config["transition"] = transition

            images_batch.append(image_config)

        # Add audio for this scene
        audios_batch.append({
            "audio_url": audio_path,
            "start": 0,
            "end": round(audio_duration, 3),
            "target_start": round(scene_start, 3),
            "track_name": "audio_main"
        })

        total_duration += audio_duration
        accumulated_time += audio_duration

    return {
        "images_batch": images_batch,
        "audios_batch": audios_batch,
        "stats": {
            "total_scenes": len(script_output),
            "total_images": len(images_batch),
            "total_audios": len(audios_batch),
            "total_duration_seconds": round(total_duration, 2),
            "total_duration_minutes": round(total_duration / 60, 2)
        },
        "warnings": warnings
    }


def main():
    parser = argparse.ArgumentParser(
        description='Prepare batch data for CapCut video creation.'
    )
    parser.add_argument(
        'project_folder',
        help='Path to the project folder'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default=None,
        help='Output directory for batch JSON files (default: project_folder)'
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

    print(f"Preparing batch data for: {args.project_folder}")
    print()

    try:
        result = prepare_batch_data(args.project_folder)

        # Print stats
        stats = result["stats"]
        print(f"Total scenes: {stats['total_scenes']}")
        print(f"Total images: {stats['total_images']}")
        print(f"Total audios: {stats['total_audios']}")
        print(f"Total duration: {stats['total_duration_seconds']} seconds ({stats['total_duration_minutes']} minutes)")

        # Print warnings
        if result["warnings"]:
            print()
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")

        # Determine output directory
        output_dir = args.output_dir or args.project_folder

        # Save batch data to JSON files
        images_batch_path = os.path.join(output_dir, 'images_batch.json')
        audios_batch_path = os.path.join(output_dir, 'audios_batch.json')

        with open(images_batch_path, 'w', encoding='utf-8') as f:
            json.dump(result["images_batch"], f, indent=2)

        with open(audios_batch_path, 'w', encoding='utf-8') as f:
            json.dump(result["audios_batch"], f, indent=2)

        print()
        print(f"Batch data saved:")
        print(f"  - {images_batch_path}")
        print(f"  - {audios_batch_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
