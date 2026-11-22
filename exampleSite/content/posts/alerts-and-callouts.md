---
title: "提示框的语义类型与语法"
date: 2026-05-04
description: "介绍Chaos主题支持的提示框类型：NOTE、TIP、IMPORTANT、WARNING、CAUTION、HISTORICAL、DISCLAIMER与可折叠的DETAILS，以及自定义标题与多语言适配。"
categories: ["指南"]
tags: ["Chaos", "Markdown", "提示框"]
series: "Chaos 主题指南"
---

Chaos支持[GitHub风格的提示框语法](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts)，标题文字会随站点语言自动本地化，并配有对应的图标与底色。除通用的五种类型外，主题还扩充了面向技术归档与免责声明的语义类型。

<!--more-->

只需在引用块（`>`）的第一行声明类型关键词即可（因为定义列表的术语行不支持嵌入块级引用与代码块，以下逐一将源码写法与渲染效果穿插对照）。

## 标准提示框类型

### `NOTE`

```markdown
> [!NOTE]
> 供浏览时参考的背景信息与补充说明。
```

> [!NOTE]
> 供浏览时参考的背景信息与补充说明。

### `TIP`

```markdown
> [!TIP]
> 有助于提高操作效率的使用技巧与建议。
```

> [!TIP]
> 有助于提高操作效率的使用技巧与建议。

### `IMPORTANT`

```markdown
> [!IMPORTANT]
> 达成目标所必须了解的关键步骤或必要前提。
```

> [!IMPORTANT]
> 达成目标所必须了解的关键步骤或必要前提。

### `WARNING`

```markdown
> [!WARNING]
> 需特别注意、以免引发错误或阻塞进度的警示。
```

> [!WARNING]
> 需特别注意、以免引发错误或阻塞进度的警示。

### `CAUTION`

```markdown
> [!CAUTION]
> 提醒某些破坏性操作可能带来的严重后果或数据丢失风险。
```

> [!CAUTION]
> 提醒某些破坏性操作可能带来的严重后果或数据丢失风险。

## 扩展语义类型

### `HISTORICAL`

```markdown
> [!HISTORICAL]
> 提示该文属于年代久远、技术方案已废弃或仅作归档参考的历史记录。
```

> [!HISTORICAL]
> 提示该文属于年代久远、技术方案已废弃或仅作归档参考的历史记录。

### `DISCLAIMER`

```markdown
> [!DISCLAIMER]
> 声明作者不对依据本文内容操作导致的风险或意外后果承担连带责任。
```

> [!DISCLAIMER]
> 声明作者不对依据本文内容操作导致的风险或意外后果承担连带责任。

## 自定义标题与多语言适配

### 自定义标题与行内语法

```markdown {.wrap}
> [!NOTE] 自定义标题与`行内语法`示例
> 提示框亦支持自定义标题：在标记之后紧跟自定义文字（可含*强调*、`行内代码`、链接或注音），即可覆盖默认的本地化标题。
```

> [!NOTE] 自定义标题与`行内语法`示例
> 提示框亦支持自定义标题：在标记之后紧跟自定义文字（可含*强调*、`行内代码`、链接或注音），即可覆盖默认的本地化标题。

> [!TIP]
> **多语言适配**：不论在简体中文（zh-CN）、繁体中文（zh-TW）、英语（EN）、日语（JA）还是韩语（KO）页面下，默认标题均会自动渲染为对应的母语文字（如Note、注意、友情提示、歴史的ファイル等），作者统一书写大写的英文关键词即可。

## 可折叠提示框与 `DETAILS`

对于作弊条或长文档中可选阅读的技术背景、协议细节或较长日志，可以使用原生 `<details>` 折叠卡片将其收起，避免打断主线阅读。

### 中性折叠卡片：`DETAILS`

`DETAILS` 沿用与 `code_vars` 参数面板一致的中性底色（`--ground` / `--ground-head`），不带图标，默认处于折叠状态；在标记后加上 `+` 则默认展开。

```markdown {.wrap}
> [!DETAILS] 背景：`Date`头、`Received`头与IMAP `INTERNALDATE`
> 电子邮件里与时间相关的字段主要有三个来源：发件方填写的`Date:`头、沿途MTA写入的`Received:`头，以及IMAP服务器维护的`INTERNALDATE`。
```

> [!DETAILS] 背景：`Date`头、`Received`头与IMAP `INTERNALDATE`
> 电子邮件里与时间相关的字段主要有三个来源：发件方填写的`Date:`头、沿途MTA写入的`Received:`头，以及IMAP服务器维护的`INTERNALDATE`。

```markdown {.wrap}
> [!DETAILS]+ 默认展开的补充说明
> 在标记末尾加上`+`，页面初次加载时即处于展开状态，读者仍可手动收起。
```

> [!DETAILS]+ 默认展开的补充说明
> 在标记末尾加上`+`，页面初次加载时即处于展开状态，读者仍可手动收起。

### 为任意提示框启用折叠

在任意现有提示框类型后追加 `-`（默认折叠）或 `+`（默认展开），即可保留其和色底纹与图标并转换为可折叠卡片：

```markdown {.wrap}
> [!TIP]- 展开查看命令行参数说明
> 可折叠提示框支持嵌套列表、代码块与链接，浏览器的页内查找（`Cmd+F` / `Ctrl+F`）仍可命中并自动展开其中文字；打印页面时所有正文折叠块也会自动全部展开，以免纸面遗漏信息。
```

> [!TIP]- 展开查看命令行参数说明
> 可折叠提示框支持嵌套列表、代码块与链接，浏览器的页内查找（`Cmd+F` / `Ctrl+F`）仍可命中并自动展开其中文字；打印页面时所有正文折叠块也会自动全部展开，以免纸面遗漏信息。
