---
title: "提示框的语义类型与语法"
date: 2026-05-04
description: "介绍 Chaos 主题支持的提示框类型：NOTE、TIP、IMPORTANT、WARNING、CAUTION、HISTORICAL 与 DISCLAIMER，以及自定义标题与多语言适配。"
categories: ["指南"]
tags: ["Chaos", "Markdown", "提示框"]
series: "Chaos 主题指南"
---

Chaos 支持 [GitHub 风格的提示框语法](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts)，标题文字会随站点语言自动本地化，并配有对应的图标与边框色彩。除通用的五种类型外，主题还扩充了面向技术归档与免责声明的语义类型。

<!--more-->

## 渲染效果

> [!NOTE]
> 供浏览时参考的背景信息与补充说明。

> [!TIP]
> 有助于提高操作效率的使用技巧与建议。

> [!IMPORTANT]
> 达成目标所必须了解的关键步骤或必要前提。

> [!WARNING]
> 需特别注意、以免引发错误或阻塞进度的警示。

> [!CAUTION]
> 提醒某些破坏性操作可能带来的严重后果或数据丢失风险。

> [!HISTORICAL]
> 提示该文属于年代久远、技术方案已废弃或仅作归档参考的历史记录。

> [!DISCLAIMER]
> 声明作者不对依据本文内容操作导致的风险或意外后果承担连带责任。

> [!NOTE] 自定义标题示例
> 提示框亦支持自定义标题：在标记之后紧跟自定义文字，即可覆盖默认的本地化标题。

## Markdown源码写法

只需在引用块（`>`）的第一行声明类型关键词：

```markdown
> [!NOTE]
> 供浏览时参考的背景信息与补充说明。

> [!TIP]
> 有助于提高操作效率的使用技巧与建议。

> [!IMPORTANT]
> 达成目标所必须了解的关键步骤或必要前提。

> [!WARNING]
> 需特别注意、以免引发错误或阻塞进度的警示。

> [!CAUTION]
> 提醒某些破坏性操作可能带来的严重后果或数据丢失风险。

> [!HISTORICAL]
> 提示该文属于年代久远、技术方案已废弃或仅作归档参考的历史记录。

> [!DISCLAIMER]
> 声明作者不对依据本文内容操作导致的风险或意外后果承担连带责任。

> [!NOTE] 自定义标题示例
> 在标记之后紧随标题文本，即可自定义提示框的头部说明。
```

> [!TIP]
> **多语言适配**：不论在简体中文（zh-CN）、繁体中文（zh-TW）、英语（EN）、日语（JA）还是韩语（KO）页面下，默认标题均会自动渲染为对应的母语文字（如 Note、注意、友情提示、歴史的ファイル 等），作者统一书写大写的英文关键词即可。


