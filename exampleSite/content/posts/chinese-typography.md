---
title: "中文排版：汉字、西文与标点的混排处理"
date: 2026-08-30
description: "介绍Chaos主题的中西文间距、标点挤压与悬挂、楷体与着重号、注音语法及源码断行净化机制。"
categories: ["指南"]
tags: ["Chaos", "中文排版", "CSS", "CJK", "注音"]
series: "Chaos 主题指南"
---

排版的目的在于呈现文本本身。中西文混排时的微小间距、行末标点悬挂与注音标注，
若处置得宜，阅读时便不致产生视觉阻滞。Chaos尽量依托现代CSS规范与构建期处理，
在页面生成与渲染时自动协调这些细节。

<!--more-->

## 中西文混排与标点悬挂

在支持[`text-autospace`](https://developer.mozilla.org/en-US/docs/Web/CSS/text-autospace)
的现代浏览器中，即便原文直接书写为「使用Hugo构建的blog」，汉字与西文或数字之间亦会自动留出适度的空隙；
在尚不支持该属性的环境中，页面依然保持常规渲染。
配合[`hanging-punctuation`](https://developer.mozilla.org/en-US/docs/Web/CSS/hanging-punctuation)，
行首与行末的标点可微调悬挂于版心边缘，使段落边界更为平整。

### 站点必须的配置

使用中文写作时，必须在站点的`hugo.toml`中开启CJK字数统计与Goldmark的东亚断行折叠扩展：

```toml
hasCJKLanguage = true

[markup.goldmark.extensions.cjk]
  enable = true
  eastAsianLineBreaks = true
  eastAsianLineBreaksStyle = 'css3draft'
  escapedSpace = true
```

> [!IMPORTANT]
> 若未启用`hasCJKLanguage`，Hugo的分词引擎会将连续的中文字句视作单个单词，导致字数统计与预计阅读时间严重失真，亦会影响列表页正文摘要的准确截断；而`[markup.goldmark.extensions.cjk]`则负责在解析期消除中文段落内手动折行产生的空格。

## 粗体、楷体变体与着重号

中文排版中，「改变字重」与「添加着重号」承担不同的语义，不宜混为一谈；同时，汉字并无西文式的斜体字形，浏览器默认的机械倾斜（伪斜体）会破坏汉字重心。主题将三者拆分为各自独立的表现形式：

- **粗体**（`**粗体**`）：纯字重加粗，不附加着重号，适用于列表引导词与关键术语。
- *变体强调*（`*楷体与Latin italic*`）：西文保持真斜体，中文禁用机械倾斜并切换为楷体（若系统未安装楷体，则回退至有衬线宋体；日文页面切换为明朝体，韩文使用斜体）；`***粗斜体***`则合成为加粗楷体与西文粗斜体。
- [着重号]{.}（`[文字]{.}`）：保持正常字重与正体，在汉字下方添加实心圆点（日文与韩文页面分别按各自排版惯例置于文字上侧；构建期转换为`<em class="em-dot">`，在RSS阅读器中平稳退化为标准`<em>`）。

## 注音语法（Ruby Annotations）

主题支持标准的注音标记语法。在Markdown中书写时，在`[文字]`之后附带`{注音}`或`^(注音)`，
构建时将转换为HTML标准的[`<ruby>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ruby)与[`<rt>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/rt)标签，
并附带`<rp>`括号，以便在不支持注音的阅读环境中平稳退化为常规括号注记：

- [漢字]{かんじ}：日文[振假名](https://zh.wikipedia.org/wiki/%E6%8C%AF%E5%81%87%E5%90%8D)（Furigana，使用`{...}`）
- [汉字]^(hàn zì)：[汉语拼音](https://zh.wikipedia.org/wiki/%E6%B1%89%E8%AF%AD%E6%8B%BC%E9%9F%B3)（使用`^(...)`）
- [漢]^(ㄏㄢˋ)[字]^(ㄗˋ)：[注音符号](https://zh.wikipedia.org/wiki/%E6%B3%A8%E9%9F%B3%E7%AC%A6%E8%99%9F)
- [临时方案]{永久保留}：借用注音语法标注言外之意的中文「义训」用法

## 源码换行与空白处理

撰写Markdown文本时，作者常习惯依句子结构或按行宽手动折行，历史稿件中也常遗留手敲的中西文空格。
根据[CommonMark](https://commonmark.org/)规范，
段落内的单个换行符在转换为HTML时默认会被视为空白字符，
进而在相连的汉字或全角标点之间渲染出多余的ASCII空格。

Chaos分两层处理这些空白，并且完全避开`<pre>`与行内`<code>`代码块：

1. **解析期软换行折叠**：依靠`hugo.toml`中的`[markup.goldmark.extensions.cjk]`（配合`eastAsianLineBreaksStyle = 'css3draft'`包含全角标点边界），在Markdown解析阶段直接折叠中日韩段落内的单行折行符。
2. **渲染后边界净化与软断点注入**：构建期模板（网页与Atom/RSS订阅源共用）自动剔除汉字与西文、数字或内联标签（如`**粗体**`、`*楷体*`、链接）之间手敲的空格，统一交由CSS `text-autospace`控制间距；同时为16字符以上的行内代码与24字符以上的裸链接在`.`、`/`、`::`、`->`等分隔符前注入零宽软断点（`<wbr>`），避免两端对齐段落因长标识符整串换行而拉出空白「河流线」（详例见[混排样张](../typography-specimen/)）。

## 引文

> 南海之帝为儵，北海之帝为忽，中央之帝为浑沌。儵与忽时相与遇于浑沌之地，浑沌待之甚善。
> 儵与忽谋报浑沌之德，曰：「人皆有七窍以视听食息，此独无有，尝试凿之。」
> 日凿一窍，七日而浑沌死。
>
> ——[《庄子·应帝王》](https://zh.wikisource.org/wiki/%E8%8E%8A%E5%AD%90/%E6%87%89%E5%B8%9D%E7%8E%8B)（参见维基百科[浑沌](https://zh.wikipedia.org/wiki/%E6%B5%91%E6%B2%8C)传说）


## 表格排版

针对较宽的表格，样式会自动允许在移动设备或窄屏视口下水平滑动浏览，避免破坏整篇版面：

| 特性 | 实现层 | 作用与表现 |
| :--- | :--- | :--- |
| **中西文间距** | CSS（`text-autospace`） | 汉字与西文、数字之间自动呈现微间距 |
| **标点挤压与悬挂** | CSS（`text-spacing-trim` + `chws` + `hanging-punctuation`） | 收紧连续全角标点留白，行端标点微挂于版心边缘 |
| **斜体与变体** | CSS（`font-synthesis-style` + `--font-em`） | 西文真斜体，中日文禁用伪斜体并切换楷体/宋体/明朝体 |
| **着重号** | 构建期重写 + CSS（`text-emphasis`） | `[文字]{.}`输出`<em class="em-dot">`，中文下加圆点，日韩上加傍点 |
| **注音标注** | 构建期重写 | 输出标准HTML `<ruby>`（支持假名、拼音与注音符号） |
| **长词软断行** | 构建期重写（`<wbr>`） | 为16字符以上行内代码与24字符以上裸链接在分隔符前注入零宽折行点 |
| **空白净化** | Goldmark CJK扩展 + 构建期重写 | 消除Markdown源码折行与手敲空格在CJK边界产生的多余空白 |

