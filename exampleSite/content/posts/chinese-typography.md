---
title: "中文排版：汉字、西文与标点的混排处理"
date: 2026-08-30
description: "介绍 Chaos 主题的中西文间距、标点悬挂、注音语法与源码断行空格净化机制。"
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

使用中文写作时，必须在站点的`hugo.toml`中配置：

```toml
hasCJKLanguage = true
```

> [!IMPORTANT]
> 若未启用此项，Hugo的分词引擎会将连续的中文字句视作单个单词，导致字数统计与预计阅读时间严重失真，亦会影响列表页正文摘要的准确截断。

## 注音语法（Ruby Annotations）

主题支持标准的注音标记语法。在Markdown中书写时，在 `[文字]` 之后附带 `{注音}` 或 `^(注音)`，
构建时将转换为HTML标准的[`<ruby>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ruby)与[`<rt>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/rt)标签，
并附带`<rp>`括号，以便在不支持注音的阅读环境中平稳退化为常规括号注记：

- [漢字]{かんじ}：日文[振假名](https://zh.wikipedia.org/wiki/%E6%8C%AF%E5%81%87%E5%90%8D)（Furigana，使用 `{...}`）
- [汉字]^(hàn zì)：[汉语拼音](https://zh.wikipedia.org/wiki/%E6%B1%89%E8%AF%AD%E6%8B%BC%E9%9F%B3)（使用 `^(...)`）
- [漢]^(ㄏㄢˋ)[字]^(ㄗˋ)：[注音符号](https://zh.wikipedia.org/wiki/%E6%B3%A8%E9%9F%B3%E7%AC%A6%E8%99%9F)
- [临时方案]{永久保留}：借用注音语法标注言外之意的中文「义训」用法

## 源码换行与空白处理

撰写Markdown文本时，作者常习惯依句子结构或按行宽手动折行。
根据[CommonMark](https://commonmark.org/)规范，
段落内的单个换行符在转换为HTML时通常会被视为空白字符，
进而在相连的两个中文字符之间渲染出多余的ASCII空格。

Chaos在模板中配置了正则处理规则，在生成HTML时，
自动剔除CJK字符与标点之间的源码单行换行与空格，
同时保留真实的段落分块（`</p><p>`）。
如此，无论编辑源码时如何断行，最终呈现的文本均平顺连贯。

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
| **中西文间距** | CSS (`text-autospace`) | 汉字与西文、数字之间自动呈现微间距 |
| **标点悬挂** | CSS (`hanging-punctuation`) | 标点略微悬挂于版心边缘，使文本边沿平直 |
| **注音标注** | 模板Render Hook | 输出标准HTML`<ruby>`（支持假名、拼音与注音符号） |
| **空白净化** | Hugo构建期正则 | 消除Markdown源码中文折行产生的多余空格 |

