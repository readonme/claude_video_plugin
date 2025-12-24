# Claude Video Creator Plugin

Claude Code 视频创作插件，提供 AI 视频创作的斜杠命令。

## 安装

### 前提条件

在安装此插件之前，需要先设置 MCP 服务器：

```bash
npm install -g claude-video-creator
claude-video-creator setup
```

### 安装插件

```bash
# 添加插件市场
claude plugin marketplace add readonme/claude_video_plugin

# 安装插件
claude plugin install video-creator

# 重启 Claude Code
```

## 可用命令

安装后，以下命令将在 Claude Code 中可用：

| 命令 | 说明 |
|------|------|
| `/video-creator:scene` | 拆分文本脚本为适合视频展示的场景/句子 |
| `/video-creator:prompt` | 为每个场景生成 AI 图像提示词 |
| `/video-creator:build` | **一键生成**：自动执行音频+图像+草稿完整流程 |
| `/video-creator:audio` | 批量生成 TTS 语音文件 |
| `/video-creator:image` | 批量生成 AI 图像 |
| `/video-creator:jianying_draft` | 创建剪映/CapCut 草稿 |

## 使用流程

### 🚀 快速流程（推荐）

```
1. 准备文本脚本（.txt 文件）

2. 拆分文本为场景
   /video-creator:scene script.txt ./my_project

3. 生成图像提示词
   /video-creator:prompt ./my_project

4. 一键生成视频（自动执行音频+图像+草稿）
   /video-creator:build ./my_project

5. 在剪映中编辑和导出
```

### ⚙️ 手动流程（自定义参数）

```
1. 准备文本脚本（.txt 文件）

2. 拆分文本为场景
   /video-creator:scene script.txt ./my_project

3. 生成图像提示词
   /video-creator:prompt ./my_project

4. 生成配音（可自定义音色、语速）
   /video-creator:audio ./my_project

5. 生成图像（可自定义模型、分辨率）
   /video-creator:image ./my_project

6. 创建视频草稿（可自定义分辨率）
   /video-creator:jianying_draft ./my_project

7. 在剪映中编辑和导出
```

## 卸载

```bash
claude plugin uninstall video-creator
```

## 相关项目

- [claude-video-creator](https://github.com/readonme/video_plugin) - MCP 服务器安装包

## 许可证

MIT License
