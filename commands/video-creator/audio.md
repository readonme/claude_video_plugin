# Generate TTS Audio Files from Video Script

## 任务目标
从项目文件夹中读取 `script_output.json`，使用 MiniMax TTS Batch API 批量生成高质量音频文件。

## 输入要求
- **必需参数**：项目文件夹路径（包含 `script_output.json` 的目录）
- **可选参数**：
  - `--voice` / `-v`: 音色 ID（默认: `English_Gentle-voiced_man`）
  - `--speed` / `-s`: 语速 [0.5-2.0]（默认: `1.2`）
  - `--emotion` / `-e`: 情绪风格（默认: 自动检测）
  - `--format` / `-f`: 音频格式 (mp3/wav/flac)（默认: `mp3`）

## 用户使用方式

```bash
# 基本用法（从项目文件夹读取）
/video-creator:audio /path/to/project_folder

# 自定义音色和语速
/video-creator:audio /path/to/project_folder --voice English_Graceful_Lady --speed 1.2

# 指定情绪
/video-creator:audio /path/to/project_folder --emotion happy
```

## 项目文件夹结构

此命令期望以下项目文件夹结构：
```
<project_folder>/
├── script_output.json      # 输入：脚本+提示词（来自 /video-creator:scene-and-prompt）
└── audio/                  # 输出：音频文件将保存到这里
    ├── audio_001.mp3
    ├── audio_002.mp3
    ├── ...
    └── audio_metadata.json
```

## 执行步骤

### Step 1: 验证项目文件夹和读取输入

1. 验证项目文件夹存在
2. 读取 `<project_folder>/script_output.json`
3. 验证 JSON 格式（必须是包含 `script` 字段的数组）
4. 确保 `<project_folder>/audio/` 目录存在
5. 显示任务概览

**输出格式示例**：
```
🎙️ 生成 TTS 音频文件
================================
项目文件夹: /path/to/project
输入文件: script_output.json
句子总数: 14
音色: English_Gentle-voiced_man
语速: 1.2x
输出目录: audio/

准备批量生成音频...
```

### Step 2: 使用批量 TTS 工具生成音频

**优先使用批量工具** `mcp__minimax-tts__text_to_speech_batch`，一次调用生成所有音频：

```json
{
  "json_file": "/path/to/project/script_output.json",
  "output_dir": "/path/to/project/audio",
  "voice_id": "English_Gentle-voiced_man",
  "model": "speech-2.6-hd",
  "speed": 1.2,
  "audio_format": "mp3",
  "sample_rate": 32000,
  "naming_pattern": "sequential",
  "start_index": 1,
  "concurrency": 3,
  "force_regenerate": false
}
```

**批量工具优势**：
- 并行处理多个句子（默认 3 个并发）
- 自动生成 `audio_metadata.json` 元数据文件
- 支持断点续传（跳过已存在的文件）
- 统一的命名模式：`audio_001.mp3`, `audio_002.mp3`, ...

**批量工具参数说明**：
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `json_file` | 输入 JSON 文件路径（包含 `script` 字段的数组） | 必需 |
| `output_dir` | 音频输出目录 | `./audio_output` |
| `voice_id` | 音色 ID | `female-tianmei` |
| `model` | TTS 模型 | `speech-2.6-hd` |
| `speed` | 语速 [0.5-2.0] | `1.0` |
| `audio_format` | 音频格式 (mp3/wav/flac) | `mp3` |
| `concurrency` | 并发数 [1-5] | `3` |
| `force_regenerate` | 是否强制重新生成 | `false` |

### Step 3: 验证输出

批量工具会自动生成 `audio_metadata.json`，包含：
- 每个音频文件的绝对路径 (`absolute_path`)
- 音频时长 (`duration_ms`)
- 文件大小 (`file_size_bytes`)
- 处理状态（成功/跳过/失败）

**元数据文件格式示例**：
```json
{
  "source_file": "/path/to/project/script_output.json",
  "generated_at": "2024-01-01T12:00:00.000Z",
  "total_sentences": 14,
  "successful_generations": 14,
  "failed_generations": 0,
  "skipped_files": 0,
  "voice_settings": {
    "voice_id": "English_Gentle-voiced_man",
    "model": "speech-2.6-hd",
    "speed": 1.2,
    "audio_format": "mp3"
  },
  "audio_files": [
    {
      "index": 1,
      "script": "Your brain on toxic love is like a slot machine player at 3 a.m.",
      "audio_file": "audio_001.mp3",
      "absolute_path": "/path/to/project/audio/audio_001.mp3",
      "duration_ms": 3500,
      "file_size_bytes": 56000
    }
  ],
  "summary": {
    "total_duration_ms": 48650,
    "total_duration_seconds": 48.65,
    "total_size_bytes": 778400
  }
}
```

### Step 4: 显示完成摘要和后续命令

```
🎉 音频生成完成！
================================
✅ 成功: 14/14 个句子
⏭️  跳过: 0 个（已存在）
❌ 失败: 0 个
📂 输出目录: /path/to/project/audio/
⏱️  总时长: 48.65 秒
📊 元数据: audio_metadata.json

后续命令:
  1. 生成图像: /video-creator:image /path/to/project
  2. 创建视频: /video-creator:jianying_draft /path/to/project
```

## 音色选项

### 英文音色（推荐）
- `English_Gentle-voiced_man` - 温和男声（默认）
- `English_Trustworthy_Man` - 可信赖男声
- `English_Diligent_Man` - 勤勉男声
- `English_Graceful_Lady` - 优雅女士
- `Arnold` - 浑厚男声（较快语速）
- `Rudolph` - 活力男声
- `Grinch` - 戏剧性男声（较慢语速）

### 中文音色
- `female-tianmei` - 甜美女声
- `male-qn-qingse` - 清晰男声

## 情绪选项

`happy`, `sad`, `angry`, `fearful`, `disgusted`, `surprised`, `calm`（默认）, `fluent`

## 断点续传

如果音频生成中断，再次运行命令会：
1. 自动检测已存在的音频文件
2. 跳过已存在的文件（不重新生成）
3. 只生成缺失的音频文件
4. 更新元数据文件

要强制重新生成所有音频，使用 `force_regenerate: true` 参数。

## 边界情况处理

- **项目文件夹不存在**: 提示先运行 `/video-creator:scene-and-prompt`
- **script_output.json 不存在**: 提示先运行 `/video-creator:scene-and-prompt`
- **部分失败**: 继续处理其他句子，记录错误到 metadata 的 `errors` 字段
- **文件已存在**: 默认跳过，除非设置 `force_regenerate: true`

## 成功标准

✅ 任务成功的标志：
1. 成功从项目文件夹读取 `script_output.json`
2. 使用批量 TTS 工具生成所有音频文件
3. 音频文件保存到 `<project_folder>/audio/` 目录
4. 自动生成 `audio_metadata.json` 元数据文件
5. 显示完成摘要和后续命令提示

## 注意事项

- **优先使用批量工具**: 使用 `mcp__minimax-tts__text_to_speech_batch` 而非逐个调用
- **使用绝对路径**: `json_file` 和 `output_dir` 都必须是绝对路径
- **项目文件夹**: 所有输出都保存到项目文件夹的 `audio/` 子目录中
- **并发控制**: 默认 3 个并发，最大支持 5 个并发请求
