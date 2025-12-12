# Split Script into Scenes/Sentences

## 任务目标
将原始文案智能拆分成适合视频展示的场景/句子，每个句子长度适中，语义完整，适合作为视频字幕展示。

## 输入要求
- **必需参数 1**：文本文件路径（包含原始脚本内容）
- **必需参数 2**：项目文件夹路径（用于存放所有输出文件）

用户会通过以下方式提供输入：
```bash
/video-creator:scene path/to/script.txt path/to/project_folder
```

## 项目文件夹结构

此命令会在项目文件夹中创建以下结构：
```
<project_folder>/
├── script.txt              # 原始脚本的副本
├── scenes.json             # 本命令的输出（拆分后的句子列表）
├── audio/                  # 后续命令的输出目录
└── images/                 # 后续命令的输出目录
```

---

## ⚠️ 核心规则：禁止使用脚本拆分文案

**这是最重要的规则，违反此规则视为任务彻底失败：**

1. **禁止使用 Python/Bash 脚本拆分文案**
   - ❌ 禁止使用 `python3 << 'EOF'` 或任何脚本语言
   - ❌ 禁止使用正则表达式、split() 等编程方式
   - ❌ 禁止说"让我用脚本更高效地处理"

2. **必须使用 LLM 智能拆分**
   - ✅ 必须理解句子的语义和上下文
   - ✅ 必须判断合适的断句位置
   - ✅ 必须确保每个片段语义完整
   - ✅ 可以分批处理，但每批都必须人工判断

3. **为什么禁止脚本？**
   - 脚本只能机械地按标点符号拆分，会导致：
     - 把单独的标点符号拆成一行
     - 生成过长或过短的句子
     - 在不恰当的位置断句，破坏语义
   - LLM 能理解语义，智能判断最佳断句位置

---

## 执行步骤

### Step 1: 创建项目文件夹结构

1. 验证项目文件夹路径
2. 如果文件夹不存在，创建它
3. 创建子目录：`audio/` 和 `images/`
4. 复制原始脚本文件到项目文件夹

**输出示例**：
```
📁 创建项目文件夹: /path/to/project
  ✅ 创建 audio/ 目录
  ✅ 创建 images/ 目录
  ✅ 复制脚本文件到项目文件夹
```

### Step 2: 读取原始文案

1. 读取输入文本文件的完整内容
2. 识别文案语言（中文/英文/混合）
3. 统计大致字符/单词数量

**输出示例**：
```
📄 读取原始文案
================================
文件: /path/to/script.txt
语言: 英文
总字符数: 8,500
预估句子数: 150-200
```

### Step 3: 智能拆分文案（核心步骤）

#### 🎯 拆分目标

**目标长度**（适合 YouTube 视频字幕）：
- **英文**：每句 10-20 个单词（理想），最多不超过 25 个单词
- **中文**：每句 15-30 个字符（理想），最多不超过 40 个字符

**拆分原则**：
1. **语义完整**：每个片段必须是一个完整的意思单元，可以独立理解
2. **长度适中**：不能太长（难以阅读），不能太短（太碎片化）
3. **自然断句**：在自然的语气停顿处断开，如逗号、分号、连接词
4. **保留标点**：每个句子应保留其结尾标点

#### 🔢 批次划分

由于文案可能很长，需要分批处理：

| 原文长度 | 每批处理量 | 说明 |
|---------|-----------|------|
| < 2000 字符 | 全部 | 一次处理完 |
| 2000-5000 字符 | 约 1000 字符 | 分 2-5 批 |
| 5000-10000 字符 | 约 1500 字符 | 分 4-7 批 |
| > 10000 字符 | 约 2000 字符 | 根据总量计算 |

#### 📋 拆分流程

**对于每一批，必须执行以下流程：**

```
═══════════════════════════════════════════════════════════════
📦 批次 1/5：处理原文第 1-1500 字符
═══════════════════════════════════════════════════════════════

原文片段：
"Your brain on toxic love is like a slot machine player at 3 a.m., same reward patterns, same addiction cycles, same panic when the machine stops paying out. The dopamine hits feel amazing at first..."

拆分结果：
1. "Your brain on toxic love is like a slot machine player at 3 a.m."
2. "Same reward patterns, same addiction cycles, same panic when the machine stops paying out."
3. "The dopamine hits feel amazing at first."
...

✅ 批次 1 完成：生成 25 个句子
═══════════════════════════════════════════════════════════════
```

#### ⚠️ 拆分注意事项

**正确拆分示例**：

| 原文 | 正确拆分 | 错误拆分 |
|------|---------|---------|
| "He said, 'I love you.' She smiled." | ✅ "He said, 'I love you.'" + "She smiled." | ❌ "He said," + "'I love you.'" + "She smiled." |
| "First, prepare the ingredients; second, mix them well." | ✅ "First, prepare the ingredients." + "Second, mix them well." | ❌ "First," + "prepare the ingredients;" + "second," + "mix them well." |
| "This is amazing—truly incredible!" | ✅ "This is amazing—truly incredible!" | ❌ "This is amazing—" + "truly incredible!" |

**避免以下错误**：
- ❌ 把单独的标点符号（如 `"` 或 `—`）拆成独立句子
- ❌ 在引号中间断开
- ❌ 生成只有 1-3 个单词的超短句子
- ❌ 生成超过 30 个单词的超长句子
- ❌ 在破折号、省略号中间断开

#### ⚡ 重要：批次之间不要等待

- 完成一批后，**立即开始下一批**
- 不要询问用户"是否继续"
- 保持连续工作直到所有批次完成

#### 🧹 文本清理（TTS 预处理）

拆分完成后，需要清理每个句子中会影响 TTS 朗读的特殊字符：

**需要移除的字符**：
- `*` 星号（Markdown 强调标记）
- `-` 句首的连字符/列表符号
- `"` `"` `'` `'` `"` `'` 各类引号
- `~` 波浪号
- `#` 井号
- `_` 下划线（Markdown 强调标记）

**清理规则**：
1. 移除句首的 `-` 或 `*`（列表符号）
2. 移除所有类型的引号（中英文引号）
3. 移除 Markdown 格式字符（`*`、`_`、`#`、`~`）
4. 保留正常的句子标点（句号、逗号、问号、感叹号）

**清理示例**：

| 原句 | 清理后 |
|------|--------|
| `"This is amazing!"` | `This is amazing!` |
| `- First, do this.` | `First, do this.` |
| `*Really* important` | `Really important` |
| `She said, "Hello."` | `She said, Hello.` |

### Step 4: 生成输出文件

将拆分结果保存到 `<project_folder>/scenes.json`：

```json
{
  "source_file": "/path/to/script.txt",
  "language": "en",
  "total_sentences": 174,
  "generated_at": "2024-01-15T10:30:00Z",
  "sentences": [
    {
      "index": 1,
      "script": "Your brain on toxic love is like a slot machine player at 3 a.m.",
      "word_count": 14
    },
    {
      "index": 2,
      "script": "Same reward patterns, same addiction cycles, same panic when the machine stops paying out.",
      "word_count": 13
    }
  ]
}
```

**字段说明**：
- `source_file`：原始文件路径
- `language`：检测到的语言（`en` / `zh` / `mixed`）
- `total_sentences`：总句子数
- `sentences`：句子数组
  - `index`：句子序号（从 1 开始）
  - `script`：句子内容
  - `word_count`：单词数（英文）或字符数（中文）

### Step 5: 显示完成摘要和后续命令

```
🎉 文案拆分完成！
================================
📂 项目文件夹: /path/to/project
📄 原始文件: script.txt
📝 输出文件: scenes.json
🌐 语言: 英文
📊 句子数量: 174
📏 平均长度: 15.2 单词/句

句子长度分布:
  5-10 单词: 32 句 (18.4%)
  11-15 单词: 68 句 (39.1%)
  16-20 单词: 52 句 (29.9%)
  21-25 单词: 22 句 (12.6%)

后续命令:
  1. 生成提示词: /video-creator:prompt /path/to/project
  2. 生成音频: /video-creator:audio /path/to/project
  3. 生成图像: /video-creator:image /path/to/project
```

---

## 边界情况处理

### 空文件或无有效内容
如果输入文件为空，停止执行并提示：
```
⚠️ 输入文件为空或没有找到有效的内容。
```

### 文件不存在
如果输入文件路径不存在，停止执行并提示：
```
❌ 错误：文件不存在 - {file_path}
```

### 项目文件夹已存在
如果项目文件夹已存在且包含 `scenes.json`：
```
⚠️ 项目文件夹已存在且包含之前的输出
是否覆盖？(y/n)
```

### 混合语言内容
如果检测到中英文混合：
- 按主要语言的规则处理
- 在输出中标注 `language: "mixed"`

---

## 成功标准

✅ 任务成功的标志：
1. 成功创建项目文件夹结构（包含 audio/ 和 images/ 子目录）
2. 成功读取原始文案
3. **使用 LLM 智能拆分**（禁止使用脚本）
4. 每个句子长度适中（英文 10-25 单词，中文 15-40 字符）
5. 每个句子语义完整，可独立理解
6. 没有产生单独的标点符号句子
7. 成功生成 `scenes.json` 文件
8. 显示完成摘要和后续命令提示

---

## 注意事项

- **🚫 绝对禁止使用脚本拆分文案**：这是本命令的核心要求
- **语义完整性优先**：宁可句子稍长，也不要在不恰当的位置断开
- **保留原文标点**：拆分后的句子应保留原有的标点符号
- **检查拆分质量**：拆分完成后快速检查是否有异常短句或标点符号句子
- **分批处理**：长文案必须分批处理，每批都要人工判断断句位置
