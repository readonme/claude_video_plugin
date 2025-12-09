# Generate Images from Prompts using Seedream API

## 任务目标
从项目文件夹中读取 `script_output.json`，使用 Seedream API 批量生成高质量图像文件。

## 重要：多图像支持

**Seedream API 可能为单个 prompt 生成多张图像**。当 `sequential_image_generation` 设置为 `'on'` 或 `'auto'` 时，模型会根据 prompt 内容推断是否需要生成序列图像（如故事、场景变化等）。

**关键**：调用 MCP 工具后，必须检查返回结果中的 `image_count` 字段：
- `image_count = 1`: 单张图像，使用 `output_file` 字段
- `image_count > 1`: 多张图像，使用 `images` 数组获取所有图像路径

## 输入要求
- **必需参数**：项目文件夹路径（包含 `script_output.json` 的目录）

## 用户使用方式

```bash
# 基本用法（从项目文件夹读取）
/video-creator:image /path/to/project_folder
```

## 项目文件夹结构

此命令期望以下项目文件夹结构：
```
<project_folder>/
├── script_output.json      # 输入：脚本+提示词（来自 /video-creator:scene-and-prompt）
└── images/                 # 输出：图像文件将保存到这里
    ├── image_001.png       # prompt 1 的图像（可能有多张: image_001_01.png, image_001_02.png）
    ├── image_002.png
    └── image_metadata.json # 元数据（包含多图像信息）
```

## 执行步骤

### Step 1: 验证项目文件夹和读取输入

1. 验证项目文件夹存在
2. 读取 `<project_folder>/script_output.json`
3. 验证 JSON 格式（必须是包含 `prompt` 字段的数组）
4. 确保 `<project_folder>/images/` 目录存在
5. 显示任务概览

**输出格式示例**：
```
🎨 生成 AI 图像
================================
项目文件夹: /Users/zhenhaohua/projects/toxic_love
输入文件: script_output.json
提示词总数: 24
模型: doubao-seedream-4-0-250828
尺寸: 2K (2048x2048)
输出目录: images/
并发数: 3

准备生成图像...
```

### Step 2: 调用 MCP 批量图像生成工具

**重要**: 必须使用绝对路径作为 output_dir。

调用 `mcp__minimax-tts__prompt_to_image_batch` 工具：

```json
{
  "json_file": "/Users/zhenhaohua/projects/toxic_love/script_output.json",
  "output_dir": "/Users/zhenhaohua/projects/toxic_love/images",
  "concurrency": 3,
  "naming_pattern": "sequential",
  "image_format": "png",
  "size": "2K",
  "watermark": false
}
```

### Step 3: 显示批量处理进度

批量工具会自动处理所有提示词，并处理多图像响应：
```
⏳ 处理中 1/24
✅ 已生成 1/24: image_001.png (1 张图像)
⏳ 处理中 2/24
✅ 已生成 2/24: image_002_01.png, image_002_02.png, image_002_03.png (3 张图像)
⏳ 处理中 3/24
✅ 已生成 3/24: image_003.png (1 张图像)
...
```

**注意**: 当 `sequential_image_generation` 为 `'auto'` 或 `'on'` 时，模型会根据 prompt 内容自动决定生成图像数量。

### Step 4: 显示完成摘要和后续命令

```
🎉 图像生成完成！
================================
📝 提示词总数: 24
🖼️ 生成图像总数: 28 (部分 prompt 生成了多张图像)
✅ 成功: 23/24 个提示词
❌ 失败: 1 个提示词
📂 输出目录: /Users/zhenhaohua/projects/toxic_love/images/
💾 总大小: 55.95 MB
📝 元数据: image_metadata.json

后续命令:
  创建视频: /video-creator:jianying_draft /path/to/project
```

## 默认设置说明

- **模型**: `doubao-seedream-4-0-250828`
- **尺寸**: `2K` (2048x2048 像素)
- **并发数**: `3` (同时处理 3 个图像)
- **命名模式**: `sequential` (image_001.png, image_002.png, ...)
- **图像格式**: `png`
- **水印**: `false` (无水印)

## 边界情况处理

- **项目文件夹不存在**: 提示先运行 `/create-youtube-video`
- **script_output.json 不存在**: 提示先运行 `/create-youtube-video`
- **部分失败**: 继续处理，记录错误到 metadata
- **文件已存在**: 自动跳过，支持断点续传

## 元数据文件结构

生成的 `image_metadata.json` 支持多图像输出：

```json
{
  "source_file": "/Users/zhenhaohua/projects/toxic_love/script_output.json",
  "generated_at": "2024-01-15T10:30:00Z",
  "total_prompts": 24,
  "total_images": 28,
  "successful_generations": 23,
  "failed_generations": 1,
  "skipped_files": 0,
  "generation_settings": {
    "model": "doubao-seedream-4-0-250828",
    "size": "2K",
    "sequential_image_generation": "auto",
    "watermark": false,
    "image_format": "png"
  },
  "images": [
    {
      "index": 1,
      "prompt": "A person checking phone anxiously...",
      "script": "Your brain on toxic love is like a slot machine player at 3 a.m.",
      "image_count": 1,
      "image_files": [
        {
          "image_file": "image_001.png",
          "absolute_path": "/Users/zhenhaohua/projects/toxic_love/images/image_001.png",
          "image_size_bytes": 2456789
        }
      ]
    },
    {
      "index": 2,
      "prompt": "A sequence showing emotional rollercoaster...",
      "script": "Same reward patterns, same addiction cycles...",
      "image_count": 3,
      "image_files": [
        {
          "image_file": "image_002_01.png",
          "absolute_path": "/Users/zhenhaohua/projects/toxic_love/images/image_002_01.png",
          "image_size_bytes": 2345678
        },
        {
          "image_file": "image_002_02.png",
          "absolute_path": "/Users/zhenhaohua/projects/toxic_love/images/image_002_02.png",
          "image_size_bytes": 2234567
        },
        {
          "image_file": "image_002_03.png",
          "absolute_path": "/Users/zhenhaohua/projects/toxic_love/images/image_002_03.png",
          "image_size_bytes": 2123456
        }
      ]
    }
  ],
  "summary": {
    "total_size_bytes": 55950000,
    "total_size_mb": 55.95,
    "average_size_bytes": 1998214
  },
  "errors": [
    {
      "index": 15,
      "prompt": "Failed prompt text...",
      "error": "API timeout"
    }
  ]
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `total_prompts` | 输入的 prompt 总数 |
| `total_images` | 实际生成的图像总数（可能大于 prompt 数） |
| `image_count` | 该 prompt 生成的图像数量 |
| `image_files` | 图像文件数组（支持多图像） |
| `absolute_path` | 图像文件的绝对路径 |

### 多图像命名规则

- **单图像**: `image_001.png`, `image_002.png`, ...
- **多图像**: `image_001_01.png`, `image_001_02.png`, `image_001_03.png`, ...

## 性能说明

- 平均每个图像生成时间: 15-30 秒
- 24 个图像预计耗时: 2-4 分钟（并发处理）
- 每张 2K 图像约 2-3 MB (PNG 格式)

## 成功标准

✅ 任务成功的标志：
1. 成功从项目文件夹读取 `script_output.json`
2. 调用 MCP prompt_to_image_batch 工具
3. 生成图像文件到 `<project_folder>/images/` 目录
4. 创建 `image_metadata.json` 元数据文件，包含：
   - 每个 prompt 的 `image_count` 和 `image_files` 数组
   - 所有图像的 `absolute_path`
   - `total_images` 统计（可能大于 prompt 数量）
5. 显示后续命令提示

## 注意事项

- **使用绝对路径**: json_file 和 output_dir 必须是绝对路径
- **项目文件夹**: 所有输出都保存到项目文件夹的 `images/` 子目录中
- **断点续传**: 已存在的图像文件会被自动跳过
- **多图像处理**:
  - 必须检查 MCP 工具返回的 `image_count` 字段
  - 当 `image_count > 1` 时，使用 `images` 数组获取所有图像路径
  - 元数据中的 `total_images` 可能大于 `total_prompts`
