# Build Complete Video from Project

## 任务目标
从项目文件夹中读取 `script_output.json`，自动执行完整的视频生成流程：生成 TTS 音频、生成 AI 图像、创建 CapCut 草稿。

**这是一个完整的自动化命令**，相当于依次执行：
1. `/video-creator:audio` - 生成音频
2. `/video-creator:image` - 生成图像
3. `/video-creator:jianying_draft` - 创建视频草稿

## 输入要求
- **必需参数**：项目文件夹路径（包含 `script_output.json` 的目录）

## 用户使用方式

```bash
# 基本用法（从项目文件夹自动生成所有资源）
/video-creator:build /path/to/project_folder
```

## 项目文件夹结构

此命令期望以下项目文件夹结构：

**输入**：
```
<project_folder>/
└── script_output.json      # 必需：脚本+提示词（来自 /video-creator:scene 和 /video-creator:prompt）
```

**输出**：
```
<project_folder>/
├── script_output.json      # 输入文件
├── audio/                  # Step 1 生成：音频文件
│   ├── audio_001.mp3
│   ├── audio_002.mp3
│   └── ...
├── images/                 # Step 2 生成：图像文件
│   ├── image_001.png (或 image_001_01.png, image_001_02.png ...)
│   ├── image_002.png
│   └── ...
└── subtitles.srt          # Step 3 生成：字幕文件
```

## 执行步骤

### Step 1: 验证项目文件夹和输入文件

1. 验证项目文件夹存在
2. 读取 `<project_folder>/script_output.json`
3. 验证 JSON 格式（必须是包含 `script` 和 `prompt` 字段的数组）
4. 显示任务概览

**输出格式示例**：
```
🎬 构建完整视频
================================
项目文件夹: /path/to/project
场景数量: 174
语言: 英文
音色: English_Gentle-voiced_man
分辨率: 1920x1080 (YouTube 横屏)

准备开始自动化构建...
```

### Step 2: 生成 TTS 音频文件（使用 MCP 工具）

使用 `mcp__minimax-tts__script_batch_tts` 工具批量生成音频：

**工具调用参数**：
```json
{
  "script_file": "<project_folder>/script_output.json",
  "output_dir": "<project_folder>/audio",
  "voice_id": "English_Gentle-voiced_man",
  "speed": 1.2
}
```

**重要规则**：
- 必须使用**绝对路径**作为 `script_file` 和 `output_dir`
- `script_file` 必须指向包含 `script` 字段的 JSON 数组文件
- 音频文件将按顺序命名：`audio_001.mp3`, `audio_002.mp3`, ...
- **与 `/video-creator:audio` 的区别**：
  - `script_batch_tts` 直接处理完整的 script_output.json，无需分批
  - `/video-creator:audio` 使用 `text_to_speech_batch`，需要分批处理（每批最多10个）

**输出示例**：
```
🎙️ Step 1/3: 生成 TTS 音频
================================
输入文件: script_output.json (174 个场景)
输出目录: audio/
音色: English_Gentle-voiced_man
语速: 1.2x

⏳ 批量生成中... (并发数: 3)

✅ 音频生成完成
  - 成功: 174/174
  - 总时长: 524.3 秒 (8.7 分钟)
  - 输出: audio/audio_001.mp3 ~ audio_174.mp3
```

### Step 3: 生成 AI 图像（使用 MCP 工具）

使用 `mcp__minimax-tts__script_batch_image_gen` 工具批量生成图像：

**工具调用参数**：
```json
{
  "script_file": "<project_folder>/script_output.json",
  "output_dir": "<project_folder>/images"
}
```

**重要规则**：
- 必须使用**绝对路径**作为 `script_file` 和 `output_dir`
- `script_file` 必须包含 `prompt` 和 `image_count` 字段
- 图像文件命名规则：
  - 单图（image_count=1）：`image_XXX.png`
  - 多图（image_count>1）：`image_XXX_01.png`, `image_XXX_02.png`, ...
- **与 `/video-creator:image` 的区别**：
  - `script_batch_image_gen` 直接处理完整的 script_output.json
  - `/video-creator:image` 使用 `prompt_to_image_batch`，可能需要手动配置参数

**输出示例**：
```
🎨 Step 2/3: 生成 AI 图像
================================
输入文件: script_output.json (174 个提示词)
输出目录: images/
模型: doubao-seedream-4-0-250828
分辨率: 2048x2048

⏳ 批量生成中... (并发数: 5)

✅ 图像生成完成
  - 成功: 416/416
  - 多图场景: 89 个
  - 输出: images/image_001.png ~ image_174.png (或多图格式)
```

### Step 4: 创建 CapCut 视频草稿（使用 MCP 工具）

使用 `mcp__capcut-api__jianying_draft_from_folder` 工具创建草稿：

**工具调用参数**：
```json
{
  "project_folder": "<project_folder>",
  "width": 1920,
  "height": 1080
}
```

**重要规则**：
- `project_folder` 必须是绝对路径
- 该工具会自动读取 `script_output.json`、`audio/` 和 `images/` 目录
- 自动生成 SRT 字幕文件
- 自动添加图片动画和转场效果
- 草稿名称将自动使用项目文件夹名称

**输出示例**：
```
🎬 Step 3/3: 创建 CapCut 草稿
================================
项目文件夹: /path/to/project
草稿名称: my_project
分辨率: 1920x1080

⏳ 创建草稿...
  ✅ 创建草稿: my_project_1703456789_abc123
  ✅ 添加 416 张图片（含动画和转场）
  ✅ 添加 174 个音频文件
  ✅ 生成 SRT 字幕文件
  ✅ 添加字幕到草稿
  ✅ 保存草稿

✅ 草稿创建完成
  - 草稿 ID: my_project_1703456789_abc123
  - 总时长: 524.3 秒 (8.7 分钟)
  - 位置: ~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/
```

### Step 5: 显示完成摘要

```
🎉 视频构建完成！
================================
📂 项目文件夹: /path/to/project

✅ Step 1: TTS 音频生成
  - 174 个音频文件
  - 总时长: 524.3 秒 (8.7 分钟)

✅ Step 2: AI 图像生成
  - 416 张图片（89 个多图场景）
  - 分辨率: 2048x2048

✅ Step 3: CapCut 草稿创建
  - 草稿 ID: my_project_1703456789_abc123
  - 分辨率: 1920x1080
  - 位置: ~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/

下一步操作:
  1. 在 JianYing Pro (剪映) 中打开草稿
  2. 预览视频效果
  3. 导出最终视频

💡 提示: 如需单独执行某个步骤：
  - 仅生成音频: /video-creator:audio /path/to/project
  - 仅生成图像: /video-creator:image /path/to/project
  - 仅创建草稿: /video-creator:jianying_draft /path/to/project
```

## 边界情况处理

### 项目文件夹不存在
```
❌ 错误：项目文件夹不存在 - /path/to/project
请先运行 /video-creator:scene 和 /video-creator:prompt 命令创建项目
```

### 缺少 script_output.json
```
❌ 错误：找不到 script_output.json
路径: /path/to/project/script_output.json

请先运行以下命令生成脚本和提示词:
  1. /video-creator:scene script.txt /path/to/project
  2. /video-creator:prompt /path/to/project
```

### JSON 格式错误
```
❌ 错误：script_output.json 格式无效
  - 文件必须是 JSON 数组
  - 每个元素必须包含 "script" 和 "prompt" 字段

示例格式:
[
  {
    "index": 1,
    "script": "Your brain on toxic love...",
    "prompt": "A glowing brain connected to a slot machine...",
    "image_count": 3
  }
]
```

### 某个步骤失败时的处理

如果任何步骤失败，显示详细错误并停止执行：

```
❌ Step 1 失败: TTS 音频生成错误
错误详情: API rate limit exceeded

已完成步骤: 无
未完成步骤: Step 1, Step 2, Step 3

建议:
  1. 等待几分钟后重试
  2. 或单独执行失败的步骤:
     /video-creator:audio /path/to/project
```

## 性能优化

### 并发控制
- **音频生成**: 并发数 3（MCP 工具默认）
- **图像生成**: 并发数 5（MCP 工具默认）

### 断点续传
- **音频**: 如果 `audio/` 目录已存在文件，MCP 工具会自动跳过已生成的文件
- **图像**: 如果 `images/` 目录已存在文件，MCP 工具会自动跳过已生成的文件
- **草稿**: 每次都会创建新草稿（不会覆盖）

### 估算时间
根据场景数量估算总时间：

| 场景数 | 音频生成 | 图像生成 | 草稿创建 | 总时长 |
|--------|---------|---------|---------|--------|
| 50     | ~2 分钟  | ~3 分钟  | ~1 分钟  | ~6 分钟 |
| 100    | ~4 分钟  | ~6 分钟  | ~1 分钟  | ~11 分钟 |
| 200    | ~8 分钟  | ~12 分钟 | ~2 分钟  | ~22 分钟 |

注：实际时间取决于网络速度和 API 响应时间

## 成功标准

✅ 任务成功的标志：
1. 成功读取 `script_output.json`
2. 成功生成所有 TTS 音频文件到 `audio/` 目录
3. 成功生成所有 AI 图像到 `images/` 目录
4. 成功创建 CapCut 草稿并保存到 JianYing Pro
5. 所有步骤都没有错误或警告
6. 显示完整的成功摘要

## 注意事项

- **必须先运行前置命令**：`/video-creator:scene` 和 `/video-creator:prompt`
- **使用绝对路径**：所有 MCP 工具调用都必须使用绝对路径
- **检查磁盘空间**：确保有足够空间存储音频（~1MB/文件）和图像（~2MB/文件）
- **API 限制**：注意 MiniMax API 的速率限制，大型项目可能需要分批处理
- **网络连接**：需要稳定的网络连接来调用 MCP 服务
- **分辨率固定**：当前版本使用固定的 1920x1080 分辨率（YouTube 横屏）
- **音色固定**：当前版本使用固定的 `English_Gentle-voiced_man` 音色
- **语速固定**：当前版本使用 1.2x 语速

## 与单独命令的对比

| 方式 | 命令数量 | MCP 工具 | 优点 | 缺点 |
|------|---------|---------|------|------|
| **单独命令** | 3 个 | `text_to_speech_batch`<br>`prompt_to_image_batch` | 灵活控制每个步骤，可自定义参数（音色、语速、模型等） | 需要手动执行多次，分批处理，容易遗漏步骤 |
| **build 命令** | 1 个 | `script_batch_tts`<br>`script_batch_image_gen` | 自动化完整流程，一次处理完整 script 文件，无需分批 | 参数固定（当前版本） |

**关键区别**：
- **build 命令**使用专门的 `script_batch_*` 工具，直接处理完整的 `script_output.json` 文件
- **单独命令**使用通用的 `*_batch` 工具，需要手动分批或配置参数

**使用建议**：
- 🎯 **推荐使用 build 命令**：适合标准工作流，快速生成视频，一键完成
- ⚙️ **使用单独命令**：需要自定义参数（如音色、分辨率、语速、模型）时

## 未来改进方向

可能的增强功能（未来版本）：
1. 支持自定义音色、语速、分辨率等参数
2. 支持选择性执行步骤（如只生成音频和图像，不创建草稿）
3. 支持进度保存和恢复（中断后继续）
4. 支持预估时间和进度条
5. 支持批量处理多个项目文件夹
