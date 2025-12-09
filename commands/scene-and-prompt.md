# Generate YouTube Video Script with Stick Figure Prompts

## 任务目标
从文本文件生成 YouTube 视频脚本，并为每一句话配上极简火柴人风格的画面提示词。图像采用 16:9 横屏比例，适合 YouTube 视频。

## 输入要求
- **必需参数 1**：文本文件路径（包含原始脚本内容）
- **必需参数 2**：项目文件夹路径（用于存放所有输出文件）

用户会通过以下方式提供输入：
```bash
/video-creator:scene-and-prompt path/to/script.txt path/to/project_folder
```

## 项目文件夹结构

此命令会在项目文件夹中创建以下结构：
```
<project_folder>/
├── script.txt              # 原始脚本的副本
├── script_output.json      # 本命令的输出（脚本+提示词）
├── audio/                  # 后续 script-to-audio 命令的输出目录
└── images/                 # 后续 prompt-to-image 命令的输出目录
```

**重要**: 项目文件夹路径将被后续命令使用，它们会自动从项目文件夹中读取所需文件。

## 执行步骤

### Step 0: 询问图像模式

**在开始处理之前，必须先询问用户选择图像生成模式**：

```
🖼️  请选择图像生成模式：

1. 单图模式 (Single Image Mode)
   - 每个场景生成 1 张图片
   - 支持中文和英文脚本
   - 图片数量 = 句子数量

2. 多图模式 (Multi-Image Mode)
   - 根据句子长度自动计算图片数量
   - 仅支持英文脚本
   - 图片数量 = ceil(单词数 / 5)
   - 更丰富的视觉叙事

请输入 1 或 2 选择模式：
```

**等待用户输入后，根据选择执行不同的处理逻辑。**

---

### Step 1: 创建项目文件夹结构

1. 验证项目文件夹路径
2. 如果文件夹不存在，创建它
3. 创建子目录：`audio/` 和 `images/`
4. 复制原始脚本文件到项目文件夹（可选，方便归档）

**输出示例**：
```
📁 创建项目文件夹: /path/to/project
  ✅ 创建 audio/ 目录
  ✅ 创建 images/ 目录
  ✅ 复制脚本文件到项目文件夹
```

### Step 2: 读取并拆分文本

1. 读取输入文本文件的完整内容
2. 按句子拆分成数组（一句话一个元素）
   - **英文文本**：使用句号（.）、问号（?）、感叹号（!）作为主要分隔符
   - **中文文本**：使用句号（。）、问号（？）、感叹号（！）作为主要分隔符
   - 保留每句话的标点符号
3. **智能长度控制**（适合 YouTube 视频脚本的最佳长度）：
   - **目标长度**：每句 10-20 个英文单词（或 15-30 个中文字符）
   - **最大长度**：不超过 25 个英文单词（或 40 个中文字符）
   - **拆分策略**：
     - 英文：如果句子超过 25 个单词，在逗号、分号、冒号、连接词（but, and, or, when, while, because）处智能拆分
     - 中文：如果句子超过 40 个字符，在逗号（，）、分号（；）、冒号（：）处拆分
     - 拆分后的片段必须保持语义完整，每个片段可以独立作为视频字幕展示
4. 去除空白句子和纯空格行
5. **如果是多图模式**：统计每句话的单词数量（用于计算图片数量）
6. **直接输出**拆分后的句子列表并**立即继续**生成提示词（不等待用户确认）

**输出格式示例（单图模式）**：
```
找到 14 个句子：
1. Your brain on toxic love is like a slot machine player at 3 a.m.
2. Same reward patterns, same addiction cycles, same panic when the machine stops paying out.
3. ...

正在生成画面提示词...
```

**输出格式示例（多图模式）**：
```
找到 14 个句子：
1. [14 words] Your brain on toxic love is like a slot machine player at 3 a.m.
2. [13 words] Same reward patterns, same addiction cycles, same panic when the machine stops paying out.
3. ...

正在生成画面提示词...
```

---

### Step 3: 生成极简火柴人画面提示词

#### 📊 多图模式：图片数量计算规则

**仅在多图模式下执行此计算**：

```
图片数量 = ceil(单词数量 / 5)  # 向上取整
```

**计算示例**：
| 单词数量 | 图片数量 |
|---------|---------|
| 1-5 个单词 | 1 张 |
| 6-10 个单词 | 2 张 |
| 11-15 个单词 | 3 张 |
| 16-20 个单词 | 4 张 |
| 21-25 个单词 | 5 张 |

---

对于**每一句话**，按照以下五步构建法生成高质量的提示词：

#### 🎨 五步构建法 (The 5-Step Method)

##### **第零步：多图前缀 (Multi-Image Prefix) - 仅多图模式**
**仅在多图模式下**，每个提示词**必须**以多图生成指令开头：
- **格式**：`Generate [N] images of ...`
- **数字用英文**：`one`, `two`, `three`, `four`, `five`, `six` 等
- **示例**：
  - 1张图：`Generate one image of digital drawing...`
  - 2张图：`Generate two images of digital drawing...`
  - 3张图：`Generate three images of digital drawing...`

##### **第一步：基调与媒介 (Tone & Medium)**
- **强制包含**：`digital drawing`, `stick figure style`, `16:9 aspect ratio`, `widescreen horizontal composition`
- **背景锁定**：`beige background` 或 `black ink on beige background`

##### **第二步：主体与数量 (Subject & Count) - 关键升级**
不要只写 "people"，必须精确定义：
- **数量精确**：`group of 10 people`, `four characters`, `two stick figures`
- **位置关系**：`standing in a row`, `standing behind a large sign`, `sitting on a bench`

##### **第三步：差异化与特征 (Differentiation & Features) - 拒绝单调**
如果是多人场景，**必须**描述个体差异：
- **发型多样性**：`diverse hairstyles`, `curly hair`, `short curly hair`, `long straight hair`, `bald`
- **装饰与特征**：`wearing glasses`, `one with a beard`, `one with a bowtie`, `various body shapes`
- **性别比例**：`6 males and 4 females`, `three female stick figures`

##### **第四步：空间逻辑与具体交互 (Spatial Logic & Interaction)**
描述物体位置、动作指向和物品细节：
- **方位描述**：`standing on the left`, `walking to the right`, `clock in the center`
- **物品细节**：`clock hands pointing to 12 and 10`, `numbers 1-12 on the clock`
- **动作与姿态**：`holding a diamond-shaped object`, `hand on hip`, `looking at wrist watch`
- **文字与符号**：用单引号包裹，例如 `sign with 'THANK YOU' in bold letters`

##### **第四点五步：多图序列描述 (Multi-Image Sequence) - 仅多图模式且图片数量 ≥ 2 时**

当需要生成 2 张或更多图片时，**必须**使用序列描述格式：

**格式要求**：
- 使用 `first image shows...`, `second image shows...`, `third image shows...` 格式
- 在基础风格描述后用冒号 `:` 引出序列描述
- 后续图片可引用前面的元素（如 `this figure`, `the same character`, `now standing`）

**内容要求**：
- 每张图片侧重句子中的**不同关键词**或**不同动作阶段**
- 保持场景连贯性，展现动作或情绪的变化过程
- 可以展示因果关系、时间顺序或不同视角

**序列描述示例**：
```
...16:9 aspect ratio, widescreen horizontal composition: first image shows a stick figure sitting at desk with worried expression, second image shows this figure standing up with determined pose, third image shows the same character walking towards a door with confident stride...
```

##### **第五步：风格润色与负面约束 (Style & Negative Constraints)**
用风格词锁定画风，并用否定词排除干扰：
- **风格词**：`minimalistic`, `cartoonish`, `comic style`, `simple and clean design`, `humorous`, `casual and friendly atmosphere`, `expressive faces`
- **技术约束（必须包含）**：`no shading`, `no detailed clothing`, `no background elements`, `clean lines`, `no texture`, `digital medium`

#### 📋 严格限制要求

**违反任何一条都视为任务失败：**

1. **多图前缀（仅多图模式）**：每个 Prompt **必须**以 `Generate [N] images of` 开头，N 为英文数字。
2. **序列描述（仅多图模式，图片≥2）**：必须使用 `first image shows..., second image shows...` 格式。
3. **纯标签结构**：禁止使用 "and", "with", "that is", "a picture of" 等连接词。所有概念必须拆解为独立的、逗号分隔的标签（Tags）。
4. **文字格式**：画面中的文字内容**必须**使用单引号 `'Text'` 包裹，严禁使用双引号。
5. **背景铁律**：背景永远是 `beige background`。禁止复杂环境背景。
6. **否定词约束**：每个 Prompt 末尾必须包含 `no shading`, `no texture`, `clean lines`。
7. **细节脑补**：输入简单时，**必须**自动补充细节，禁止输出单调的短 Prompt。
8. **横屏规格**：每个 Prompt 必须包含 `16:9 aspect ratio`, `widescreen horizontal composition`。

---

#### 🎯 目标范例

**单图模式范例**：
```
digital drawing, stick figure style, black ink on beige background, 16:9 aspect ratio, widescreen horizontal composition, line art, group of 10 people standing in a row, diverse hairstyles, simple facial expressions, 6 males and 4 females, various body shapes, 5 with glasses, one with curly hair, one with short curly hair, one with a beard, one with a bowtie, minimalistic, cartoonish, no shading, no detailed clothing, no background elements, simple and clean design, casual and friendly atmosphere
```

**多图模式范例（3图序列）**：
```
Generate three images of digital drawing, stick figure style, beige background, 16:9 aspect ratio, widescreen horizontal composition: first image shows a stick figure standing in front of a slot machine with heart symbols on the screen, second image shows this figure pulling the lever with anxious expression sweat drops flying, third image shows the same character slumped over the machine clock showing 3:00 in corner, minimalistic, no shading, clean lines, no texture
```

---

### Step 4: 生成输出文件

将结果保存到项目文件夹中：

#### JSON 文件（主输出）
保存为 `<project_folder>/script_output.json`：

**单图模式输出格式**：
```json
[
  {
    "script": "一群在排队的朋友，长相各不相同。",
    "prompt": "digital drawing, stick figure style, black ink on beige background, 16:9 aspect ratio, widescreen horizontal composition, group of 6 friends standing in a line, waiting in queue, diverse hairstyles, 3 males and 3 females, one with curly hair, one wearing glasses, one with a baseball cap, various body shapes, casual postures, chatting, minimalistic, cartoonish, no shading, clean lines, friendly atmosphere, side view"
  }
]
```

**多图模式输出格式**：
```json
[
  {
    "script": "Your brain on toxic love is like a slot machine player at 3 a.m.",
    "word_count": 14,
    "image_count": 3,
    "prompt": "Generate three images of digital drawing, stick figure style, beige background, 16:9 aspect ratio, widescreen horizontal composition: first image shows a stick figure standing in front of a slot machine with heart symbols on the screen, second image shows this figure pulling the lever with anxious expression sweat drops flying, third image shows the same character slumped over the machine clock showing 3:00 in corner, minimalistic, no shading, clean lines, no texture"
  }
]
```

**字段说明**：
- `script`：原始脚本文字（保持不变）
- `prompt`：完整提示词
- `word_count`：（仅多图模式）句子中的单词数量
- `image_count`：（仅多图模式）根据公式计算的图片数量

---

### Step 5: 显示完成摘要和后续命令

**单图模式摘要**：
```
🎉 脚本和提示词生成完成！
================================
📂 项目文件夹: /path/to/project
📝 脚本输出: script_output.json
📊 句子数量: 14
🖼️  图像模式: 单图模式（每句1张）
🎨 风格: 极简火柴人

后续命令:
  1. 生成音频: /video-creator:audio /path/to/project
  2. 生成图像: /video-creator:image /path/to/project
  3. 创建视频: /video-creator:jianying_draft /path/to/project
```

**多图模式摘要**：
```
🎉 脚本和提示词生成完成！
================================
📂 项目文件夹: /path/to/project
📝 脚本输出: script_output.json
📊 句子数量: 14
📸 总图片数量: 38（根据单词数自动计算）
🖼️  图像模式: 多图模式（每5词1张）
🎨 风格: 极简火柴人

后续命令:
  1. 生成音频: /video-creator:audio /path/to/project
  2. 生成图像: /video-creator:image /path/to/project
  3. 创建视频: /video-creator:jianying_draft /path/to/project
```

---

## 边界情况处理

### 空文件或无有效句子
如果输入文件为空或拆分后没有有效句子，输出：
```json
[]
```
并提示用户：`⚠️ 输入文件为空或没有找到有效的句子。`

### 文件不存在
如果输入文件路径不存在，停止执行并提示：`❌ 错误：文件不存在 - {file_path}`

### 项目文件夹已存在
如果项目文件夹已存在且包含 `script_output.json`：
```
⚠️ 项目文件夹已存在且包含之前的输出
是否覆盖？(y/n)
```
或自动备份旧文件为 `script_output.json.bak`

### 多图模式使用中文脚本
如果用户选择多图模式但脚本包含中文：
```
⚠️ 多图模式仅支持英文脚本。检测到中文内容。
是否切换到单图模式？(y/n)
```

---

## 成功标准

✅ 任务成功的标志：
1. **正确询问并记录用户选择的图像模式**
2. 成功创建项目文件夹结构（包含 audio/ 和 images/ 子目录）
3. 成功读取并拆分输入文件
4. **单图模式**：每个句子生成 1 个提示词
5. **多图模式**：正确计算 image_count = ceil(word_count / 5)，提示词以 `Generate [N] images of` 开头
6. 所有提示词都包含 `16:9 aspect ratio`, `widescreen horizontal composition`
7. 所有提示词都以否定词约束结尾（`no shading`, `no texture`, `clean lines`）
8. 多人场景包含了个体差异描述
9. 成功生成 JSON 文件到项目文件夹
10. 终端显示预览表格和后续命令提示

---

## 注意事项

- **不要修改原始脚本文字**：`script` 字段必须保持原样
- **保持提示词的高密度**：参考范例的详细程度，不要生成过于简单的提示词
- **严格遵守标签格式**：逗号分隔，不使用自然语言连接词
- **背景必须是米色**：`beige background` 是强制要求
- **横屏规格**：所有提示词都必须包含 `16:9 aspect ratio`, `widescreen horizontal composition`
- **多人场景必须体现差异**：至少描述 3-5 种个体特征差异
- **项目文件夹路径**：后续命令只需要项目文件夹路径，无需重复指定各种文件路径
