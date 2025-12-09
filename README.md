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
| `/video-creator:scene-and-prompt` | 生成视频脚本和 AI 图像提示词 |
| `/video-creator:audio` | 批量生成 TTS 语音文件 |
| `/video-creator:image` | 批量生成 AI 图像 |
| `/video-creator:jianying_draft` | 创建剪映/CapCut 草稿 |

## 使用流程

```
1. 准备文本脚本（.txt 文件）

2. 生成场景和提示词
   /video-creator:scene-and-prompt script.txt ./my_project

3. 生成配音
   /video-creator:audio ./my_project

4. 生成图像
   /video-creator:image ./my_project

5. 创建视频草稿
   /video-creator:jianying_draft ./my_project

6. 在剪映中编辑和导出
```

## 卸载

```bash
claude plugin uninstall video-creator
```

## 相关项目

- [claude-video-creator](https://github.com/readonme/video_plugin) - MCP 服务器安装包

## 许可证

MIT License
