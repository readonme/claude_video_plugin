#!/usr/bin/env python3
"""
Verify image completeness for video projects.

This script reads script_output.json from a project folder,
checks if all expected images exist in the images/ directory,
and reports any missing images with their index and original prompt.

By default, outputs a missing_images.json file to the project folder
for use with prompt_to_image_batch to regenerate missing images.

Usage:
    python verify_images.py <project_folder>

Example:
    python verify_images.py /path/to/project
    python verify_images.py ./my_video_project --no-output  # Don't write JSON file
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_expected_files(index: int, image_count: int, image_format: str = 'png') -> list[str]:
    """
    Generate expected file names based on index and image_count.

    Naming rules:
    - Single image (image_count=1): image_003.png (no suffix)
    - Multiple images (image_count>1): image_001_01.png, image_001_02.png, ...

    Args:
        index: The 1-based index of the prompt
        image_count: Number of images expected for this prompt
        image_format: Image file extension (default: png)

    Returns:
        List of expected file names
    """
    if image_count == 1:
        return [f"image_{index:03d}.{image_format}"]
    else:
        return [f"image_{index:03d}_{i:02d}.{image_format}" for i in range(1, image_count + 1)]


def verify_images(project_folder: str) -> dict:
    """
    Verify image completeness in a project folder.

    Args:
        project_folder: Path to the project folder

    Returns:
        Dictionary containing:
        - expected_count: Total expected image count
        - actual_count: Actual image count found
        - missing: List of dicts with index, missing_files, and prompt
        - all_complete: Boolean indicating if all images are present
    """
    script_path = os.path.join(project_folder, 'script_output.json')
    images_folder = os.path.join(project_folder, 'images')

    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script output not found: {script_path}")
    if not os.path.exists(images_folder):
        raise FileNotFoundError(f"Images folder not found: {images_folder}")

    # Load script data
    with open(script_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    # Get existing files in images folder
    existing_files = set(os.listdir(images_folder))

    # Check each prompt's expected images
    expected_count = 0
    actual_count = 0
    missing = []

    for i, entry in enumerate(script_data, start=1):
        image_count = entry.get('image_count', 1)
        prompt = entry.get('prompt', '')
        script = entry.get('script', '')

        expected_files = get_expected_files(i, image_count)
        expected_count += len(expected_files)

        missing_files = []
        for expected_file in expected_files:
            if expected_file in existing_files:
                actual_count += 1
            else:
                missing_files.append(expected_file)

        if missing_files:
            missing.append({
                'index': i,
                'missing_files': missing_files,
                'prompt': prompt,
                'script': script,
                'expected_count': image_count,
                'missing_count': len(missing_files)
            })

    return {
        'expected_count': expected_count,
        'actual_count': actual_count,
        'missing': missing,
        'all_complete': len(missing) == 0
    }


def print_report(result: dict, project_folder: str):
    """
    Print a formatted verification report.

    Args:
        result: Result dictionary from verify_images()
        project_folder: Path to the project folder for display
    """
    print(f"🔍 验证图片完整性")
    print("=" * 40)
    print(f"项目文件夹: {project_folder}")
    print(f"预期图片数: {result['expected_count']}")
    print(f"实际图片数: {result['actual_count']}")
    print()

    if result['all_complete']:
        print("✅ 所有图片已生成完毕！")
    else:
        total_missing = sum(m['missing_count'] for m in result['missing'])
        print(f"⚠️ 缺失的图片:")
        print()

        for item in result['missing']:
            print(f"  - Index {item['index']}: {', '.join(item['missing_files'])}")
            # Truncate prompt if too long
            prompt_preview = item['prompt'][:100] + '...' if len(item['prompt']) > 100 else item['prompt']
            print(f"    Script: \"{item['script']}\"")
            print(f"    Prompt: \"{prompt_preview}\"")
            print()

        print(f"缺失总数: {total_missing} 张图片 (来自 {len(result['missing'])} 个提示词)")


def output_json(result: dict):
    """
    Output result as JSON to stdout.

    Args:
        result: Result dictionary from verify_images()
    """
    print(json.dumps(result, ensure_ascii=False, indent=2))


def save_missing_json(result: dict, project_folder: str) -> str:
    """
    Save missing images info to a JSON file for use with prompt_to_image_batch.

    Args:
        result: Result dictionary from verify_images()
        project_folder: Path to the project folder

    Returns:
        Path to the saved JSON file
    """
    output_path = os.path.join(project_folder, 'missing_images.json')

    # Format for prompt_to_image_batch compatibility
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "project_folder": project_folder,
        "summary": {
            "expected_count": result['expected_count'],
            "actual_count": result['actual_count'],
            "missing_count": result['expected_count'] - result['actual_count'],
            "missing_prompts_count": len(result['missing'])
        },
        "missing_prompts": [
            {
                "index": item['index'],
                "prompt": item['prompt'],
                "script": item['script'],
                "expected_count": item['expected_count'],
                "missing_files": item['missing_files'],
                "missing_count": item['missing_count']
            }
            for item in result['missing']
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Verify image completeness for video projects.'
    )
    parser.add_argument(
        'project_folder',
        help='Path to the project folder containing script_output.json and images/'
    )
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output result as JSON to stdout instead of formatted report'
    )
    parser.add_argument(
        '--no-output',
        action='store_true',
        help='Do not write missing_images.json file to project folder'
    )

    args = parser.parse_args()

    # Resolve to absolute path
    project_folder = os.path.abspath(args.project_folder)

    # Check if project folder exists
    if not os.path.isdir(project_folder):
        print(f"Error: Project folder not found: {project_folder}")
        sys.exit(1)

    try:
        result = verify_images(project_folder)

        if args.json:
            output_json(result)
        else:
            print_report(result, project_folder)

            # Save missing_images.json if there are missing images (unless --no-output)
            if not result['all_complete'] and not args.no_output:
                output_path = save_missing_json(result, project_folder)
                print()
                print(f"📄 缺失信息已保存到: {output_path}")
                print("   可使用此文件配合 prompt_to_image_batch 补充生成缺失图片")

        # Exit with non-zero status if images are missing
        if not result['all_complete']:
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
