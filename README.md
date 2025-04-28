# MCA课程大纲工具

## 项目简介

这是一个用于获取课程大纲数据并转换为Markdown格式的工具。它可以从API获取课程信息，包括课程名称、章节和小节的详细信息，并生成结构化的Markdown文档。

## 功能特点

- 获取课程列表和版本信息
- 获取课程大纲的详细内容（章节、小节及其时长）
- 丰富课程大纲，添加详细信息
- 将课程大纲转换为Markdown格式
- 支持将大纲内容拆分为多个文件或生成单个完整文件
- 处理标题中的空格和换行，确保格式正确

## 安装要求

- Python 3.6+
- 依赖库：`requests`

安装依赖库：

```bash
pip install requests
```

## 使用方法

### 交互式使用

1. 直接运行脚本，进入交互式模式：

```bash
python mca_request.py
```

2. 按照提示选择课程、版本，获取大纲并生成Markdown文件。

### 命令行参数使用

直接使用命令行参数生成Markdown文件：

```bash
# 基本用法
python mca_request.py --generate-md

# 指定输入JSON文件和输出Markdown文件
python mca_request.py --generate-md [input_json_path] [output_md_path]

# 控制文件分割（0表示不分割）
python mca_request.py --generate-md [input_json_path] [output_md_path] [max_chars_per_file]
```

参数说明：
- `input_json_path`：输入的JSON文件路径（可选，默认为`data/course_outline_enriched_simple.json`）
- `output_md_path`：输出的Markdown文件路径（可选，默认为`data/course_outline.md`）
- `max_chars_per_file`：每个文件的最大字符数（可选，默认为0，表示不分割）

### 文件分割选项

工具支持两种文件生成方式：
1. 生成单个完整的Markdown文件（默认）
2. 按指定字符数将内容分割成多个文件

## 示例

### 生成单个完整文件

```bash
python mca_request.py --generate-md data/course_outline_enriched.json data/complete_outline.md 0
```

### 按字符数分割文件

```bash
# 每个文件最多20000个字符
python mca_request.py --generate-md data/course_outline_enriched.json data/split_outline.md 20000
```

## 输出文件

- 当选择不分割时，会生成单个Markdown文件
- 当选择分割时，会生成一个主索引文件和多个内容文件：
  - `course_outline.md`：主索引文件
  - `course_outline_1.md`、`course_outline_2.md` 等：内容文件

## 注意事项

- 确保在运行前已正确安装依赖库
- 如果遇到获取数据失败，请检查网络连接和API可用性
- 生成的Markdown文件默认保存在`data`目录下 