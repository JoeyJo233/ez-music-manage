# ez-music-manage

A self-hosted web app for managing local music file metadata — edit tags, fetch cover art and lyrics, batch operations. Supports FLAC and AAC (M4A) formats.

[中文文档](#中文文档)

---

## Features

- **Recursive directory scan**: auto-discovers all `.flac` / `.m4a` / `.aac` files
- **Metadata editing**: title, artist, album, year, track number, genre, composer, comment, and more
- **Cover art management**: local upload, online search via iTunes + Netease, copy from library, one-click sync to entire album
- **LRC lyrics management**: dual-source search (LRCLIB + Netease), separate original/translated lyrics, manual editing
- **Batch operations**: multi-select songs, then batch-fetch covers, lyrics, or sync album art
- **Dual view modes**: flat list / artist→album tree grouping
- **Search & filter**: instant filter by title, artist, or album
- **Dark theme UI**: single-page design, no page navigation

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) package manager

## Quick Start

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install dependencies

```bash
git clone https://github.com/JoeyJo233/ez-music-manage.git
cd ez-music-manage
uv sync
```

### 3. Start the app

```bash
uv run uvicorn main:app --reload --port 8765
```

Or use the packaging-friendly launcher that starts the local server and opens the browser automatically:

```bash
uv run python launcher.py
```

### 4. Open in browser

Visit [http://localhost:8765](http://localhost:8765)

## Usage

1. **Open folder**: enter your music directory path in the top bar (e.g. `~/Music/my_music`) and click "Open"
2. **Select songs**: click a song name to select it, or use checkboxes for multi-select
3. **Edit metadata**: modify fields in the right panel and click "Save" to write to file
4. **Manage cover art**:
   - Click the cover area to upload a local image
   - Click "Search Cover" to search iTunes / Netease online
   - Click "Copy from Library" to copy cover art from another song
   - Click "⚡ Sync to Album" to write the cover to all songs in the same album
5. **Manage lyrics**:
   - Click "Fetch Lyrics" to search LRCLIB / Netease for LRC lyrics
   - Lyrics are saved as `.lrc` (original) and `.trans.lrc` (translation)
6. **Batch operations**: select multiple songs and use the toolbar batch buttons
7. **Settings**: click ⚙ in the top-right to configure Netease Cookie, cover compression settings, etc.

## Netease Cookie (Optional)

Provides full access to Netease lyrics and cover art search:

1. Open [music.163.com](https://music.163.com) and log in
2. Open DevTools (F12) → Network tab
3. Click anywhere on the page to trigger a request
4. Copy the `Cookie` header value from that request
5. Paste it into the "Netease Cookie" field in the app settings panel

## Project Structure

```
.
├── main.py                 # FastAPI entry point
├── pyproject.toml          # Project dependencies
├── settings.json           # Runtime config (auto-generated, gitignored)
├── routers/
│   ├── library.py          # Directory scanning
│   ├── songs.py            # Single song metadata read/write
│   ├── cover.py            # Cover art search, download, sync
│   ├── lrc.py              # LRC lyrics read/write, search
│   ├── batch.py            # Batch operations
│   └── settings.py         # Settings read/write
├── services/
│   ├── scanner.py          # Recursive scan, in-memory index
│   ├── metadata.py         # mutagen wrapper (unified FLAC/M4A interface)
│   ├── cover_search.py     # iTunes + Netease cover search
│   ├── lyrics.py           # LRCLIB + Netease lyrics search
│   └── settings.py         # settings.json read/write
└── frontend/
    └── index.html          # Vue 3 single-file frontend
```

## Tech Stack

| Component | Choice |
|-----------|--------|
| Backend framework | FastAPI |
| Audio tag read/write | mutagen |
| Image processing | Pillow |
| HTTP client | httpx |
| Netease API | pyncm |
| Frontend framework | Vue 3 |
| Package manager | uv |

## macOS Packaging

For macOS packaging, use the desktop launcher and the bundled PyInstaller spec:

```bash
uv run --with pyinstaller pyinstaller ez_music_manage.spec
```

This produces a macOS `.app` in `dist/`, which can be wrapped into a `.dmg` in the next step.

To build the `.dmg` package:

```bash
bash scripts/build_dmg.sh
```

---

## 中文文档

本地音乐库管理工具，通过浏览器界面管理本机硬盘上的音乐文件 metadata。支持 FLAC / AAC (M4A) 格式。

## 功能特性

- **目录递归扫描**：自动发现所有 `.flac` / `.m4a` / `.aac` 文件
- **Metadata 编辑**：标题、艺术家、专辑、年份、曲目号、流派、作曲、评论等
- **封面管理**：本地上传、iTunes + 网易云在线搜索、从库中复制、一键同步到整张专辑
- **LRC 歌词管理**：LRCLIB + 网易云双源搜索、原文/译文分别存储、手动编辑
- **批量操作**：多选歌曲后批量搜索封面、获取歌词、同步专辑封面
- **双视图模式**：平铺列表 / 艺术家→专辑树形分组
- **搜索过滤**：按标题、艺术家、专辑即时过滤
- **深色主题 UI**：单页面设计，无路由跳转

## 环境要求

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) 包管理器

## 快速开始

### 1. 安装 uv（如未安装）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆并安装依赖

```bash
git clone https://github.com/JoeyJo233/ez-music-manage.git
cd ez-music-manage
uv sync
```

### 3. 启动应用

```bash
uv run uvicorn main:app --reload --port 8765
```

也可以使用更接近桌面应用形态的启动入口，它会启动本地服务并自动打开浏览器：

```bash
uv run python launcher.py
```

### 4. 打开浏览器

访问 [http://localhost:8765](http://localhost:8765)

## 使用方法

1. **打开文件夹**：在顶栏输入音乐文件夹路径（如 `~/Music/my_music`），点击「打开」
2. **选择歌曲**：左栏点击歌曲名称单选，或通过 checkbox 多选
3. **编辑 Metadata**：右栏直接修改各字段，点击「保存」写入文件
4. **管理封面**：
   - 点击封面区域上传本地图片
   - 点击「搜索封面」从 iTunes / 网易云在线搜索
   - 点击「从库复制」从已有歌曲复制封面
   - 点击「⚡ 同步到整张专辑」将封面写入同名专辑所有歌曲
5. **管理歌词**：
   - 点击「获取歌词」从 LRCLIB / 网易云搜索 LRC
   - 歌词自动保存为 `.lrc`（原文）和 `.trans.lrc`（译文）
6. **批量操作**：多选歌曲后使用工具栏的批量按钮
7. **设置**：点击右上角 ⚙ 配置网易云 Cookie、封面压缩参数等

## 网易云 Cookie 配置（可选）

配置后可解锁完整的网易云歌词和封面搜索：

1. 浏览器打开 [music.163.com](https://music.163.com) 并登录
2. F12 打开开发者工具 → Network 标签
3. 随意点击页面触发一个请求
4. 复制该请求 Headers 中的 `Cookie` 字段值
5. 粘贴到应用设置面板中的「网易云 Cookie」输入框

## 项目结构

```
.
├── main.py                 # FastAPI 入口
├── pyproject.toml          # 项目依赖声明
├── settings.json           # 运行时配置（自动生成，已 gitignore）
├── routers/
│   ├── library.py          # 扫描目录
│   ├── songs.py            # 单曲 metadata 读写
│   ├── cover.py            # 封面搜索、下载、同步
│   ├── lrc.py              # LRC 歌词读写、搜索
│   ├── batch.py            # 批量操作
│   └── settings.py         # 设置读写
├── services/
│   ├── scanner.py          # 目录递归扫描，内存索引
│   ├── metadata.py         # mutagen 封装（FLAC / M4A 统一接口）
│   ├── cover_search.py     # iTunes + 网易云封面搜索
│   ├── lyrics.py           # LRCLIB + 网易云歌词搜索
│   └── settings.py         # settings.json 读写
└── frontend/
    └── index.html          # Vue 3 单文件前端
```

## 技术栈

| 组件 | 选型 |
|------|------|
| 后端框架 | FastAPI |
| 音频标签读写 | mutagen |
| 图片处理 | Pillow |
| HTTP 客户端 | httpx |
| 网易云 API | pyncm |
| 前端框架 | Vue 3 |
| 包管理 | uv |

## macOS 打包

如果要做 macOS 应用打包，使用桌面启动入口和仓库内的 PyInstaller 配置：

```bash
uv run --with pyinstaller pyinstaller ez_music_manage.spec
```

这一步会先在 `dist/` 下产出 `.app`，后续再把这个 `.app` 包成 `.dmg`。

生成 `.dmg` 时，执行：

```bash
bash scripts/build_dmg.sh
```
