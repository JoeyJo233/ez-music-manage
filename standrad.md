# 音乐文件 Metadata 与命名规范

本文档记录此目录下 FLAC 音乐文件的 metadata 填写标准与文件命名规则，供 AI 助手在处理新文件时统一遵守。

---

## 一、文件命名规则

**格式：`歌名-歌手.flac`**

- 歌名和歌手之间用半角连字符 `-` 分隔，无空格
- 歌名、歌手名均直接取自 metadata 中的 `title` 和 `artist` 字段
- 标点符号保留原样（如 `?`、`!`、`()`、`′` 等），不做替换
- 歌名尾部不得有多余空格（如 `夏枯れ ` → `夏枯れ`）

**示例：**
```
Peek-A-Boo-Red Velvet.flac
What is Love?-TWICE.flac
SPAGHETTI (Member ver.)-LE SSERAFIM.flac
SPINNIN′ ON IT-NMIXX.flac
夏枯れ-ずっと真夜中でいいのに。.flac
```

---

## 二、Metadata 填写规则

### 2.1 必填字段

| 字段 | 说明 |
|------|------|
| `title` | 歌曲标题，见下方规则 |
| `artist` | 演唱艺人，见下方规则 |
| `album` | 所属专辑或单曲集名称 |

### 2.2 歌曲标题（title）

- 使用官方发布的原语言标题，**不附加任何翻译**
- 日文歌曲：使用原日文标题，不在括号内附加中文翻译
  - ✅ `夏枯れ`
  - ❌ `夏枯れ (靡靡盛夏)`
- 韩文歌曲：若官方英文标题存在，优先使用英文
  - ✅ `Peek-A-Boo`
  - ❌ `피카부 (Peek-A-Boo) (躲猫猫)`
- 存在特定版本的歌曲，版本标注保留在标题中
  - ✅ `SPAGHETTI (Member ver.)`

### 2.3 艺人名（artist）

**使用官方英文或原语言舞台名，不使用汉字转写名。**

| 艺人 | 正确写法 | 错误写法 |
|------|----------|----------|
| 宇多田ヒカル | `宇多田ヒカル` | `宇多田光`（汉字读法） |
| JEON SOMI | `JEON SOMI` | `全昭弥`（汉字名） |
| NewJeans | `NewJeans` | `NewJeans (뉴진스)`（附加韩文） |
| ずっと真夜中でいいのに。 | `ずっと真夜中でいいのに。` | `ずっと真夜中でいいのに`（缺少句号） |

**重要：`ずっと真夜中でいいのに。` 艺名末尾必须带日文句号 `。`**

### 2.4 专辑名（album）

- 使用专辑/EP/单曲集的官方完整名称
- 先行单曲若已正式收录进某 EP/专辑，album 字段填写该 EP/专辑名
  - 示例：JEON SOMI 的 `EXTRA` 是《Chaotic & Confused》EP 的先行曲，album 填 `Chaotic & Confused`

---

## 三、操作流程（供 AI 参考）

处理新增音乐文件时，建议按以下顺序操作：

1. 读取文件现有 metadata（使用 `mutagen` 库）
2. 逐字段核查是否符合上述规则
3. 如有不确定的专辑/艺人信息，联网搜索官方资料后再修正
4. 写入修正后的 metadata
5. 按 `歌名-歌手.flac` 格式重命名文件
6. 输出所有改动的汇总清单

**Python 环境：** 使用 `mutagen` 库读写 FLAC metadata
```python
pip install mutagen --break-system-packages

from mutagen.flac import FLAC
audio = FLAC('文件名.flac')
audio['artist'] = '宇多田ヒカル'
audio.save()
```

---

## 四、已收录艺人参考

以下为本目录已收录艺人及其正确写法：

| 艺人 | 类型 |
|------|------|
| `NewJeans` | K-POP 女团 |
| `TWICE` | K-POP 女团 |
| `Red Velvet` | K-POP 女团 |
| `LE SSERAFIM` | K-POP 女团 |
| `NMIXX` | K-POP 女团 |
| `ILLIT` | K-POP 女团 |
| `MISAMO` | K-POP 女团（TWICE 子单元） |
| `KISS OF LIFE` | K-POP 女团 |
| `KiiiKiii` | K-POP 女团 |
| `Hearts2Hearts` | K-POP 女团 |
| `JEON SOMI` | K-POP 独唱 |
| `宇多田ヒカル` | J-POP 独唱 |
| `ずっと真夜中でいいのに。` | J-POP 乐队（注意末尾句号） |
| `DADARAY` | J-POP 乐队 |
| `FantasticYouth` | J-POP |
