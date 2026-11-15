---
title: "你好，Chaos"
date: 2026-09-12
description: "Chaos主题功能速览：设计理念、基础配置与系列指南索引。"
categories: ["指南"]
tags: ["Chaos", "Hugo", "入门"]
series: "Chaos 主题指南"
---

Chaos是一个专为个人博客设计的极简[Hugo](https://gohugo.io/)主题：不依赖前端脚本框架，
仅用轻量原生脚本提供外观模式切换、自动目录、代码与标题链接复制、
即时页面导航以及针对中文排版的细致处理。

<!--more-->

## 设计理念

主题配色源自[日本传统色](https://zh.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E4%BC%A0%E7%BB%9F%E8%89%B2%E7%B3%BB)（[和色]^(wairo)）：日间以[**生成り色**]{きなりいろ}为纸底、[**黒**]^(kuro)与[**墨**]^(sumi)为字墨，
辅以[**蘇芳**]{すおう}与[**藍色**]{あいいろ}作为强调与链接色；夜间则采用沉静的暖炭底色，配以[**白鼠**]^(shiro-nezumi)、[**退紅**]^(arazome)与[**浅縹**]^(asa-hanada)。
兼顾素雅纸张质感与[WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/)规定的色彩对比度要求。

> [!TIP]
> 点击右上角的🌓按钮，可以在「跟随系统/浅色/深色」三种模式之间切换。

## 基础配置

在站点的`hugo.toml`中，建议配置以下基础字段：

```toml
theme = 'chaos'
baseURL = 'https://example.org/'
locale = 'zh-cn'
defaultContentLanguage = 'zh-cn'
title = '混沌札记'

# 必须启用：让 Hugo 按字符统计中文字数并正常截断摘要
hasCJKLanguage = true

[outputs]
  home = ['HTML', 'ATOM', 'sitemapxsl', 'RSS', 'feedxsl', 'REDIR']
  section = ['HTML']
  taxonomy = ['HTML']
  term = ['HTML']

# 解析期折叠中文段落内的软换行，避免源码折行变成多余空格
[markup.goldmark.extensions.cjk]
  enable = true
  eastAsianLineBreaks = true
  eastAsianLineBreaksStyle = 'css3draft'
  escapedSpace = true

[params]
  subtitle = '一个*Chaos*主题的示例站点'
  mainSections = ['posts']

  [params.search]
    enable = true
```

## 主题特性指南

本系列文章分别介绍主题的各项功能与对应配置方法：

1. **[中文排版：汉字、西文与标点的混排处理](../chinese-typography/)**：中西文间距、标点挤压与悬挂、楷体与着重号、振假名与拼音注音、源码断行空格净化。
2. **[提示框的语义类型与语法](../alerts-and-callouts/)**：NOTE、TIP、IMPORTANT、WARNING、CAUTION、HISTORICAL与DISCLAIMER，以及自定义标题支持。
3. **[代码语法高亮、交互参数与Mermaid图表](../code-and-diagrams/)**：静态语法高亮、行号悬停联动、可交互代码参数（`code_vars`）、代码一键复制与Mermaid图表。
4. **[用KaTeX书写数学公式](../math-with-katex/)**：行内与块级公式、Goldmark passthrough配置与洛伦兹方程组。
5. **[文章元数据与内容控制](../front-matter-and-metadata/)**：`deprecated`（过时降权）、`searchHidden`（隐藏检索）、`noindex`（避免收录）、`series`（系列导航与时间线）与标题段落链接。
6. **[全文检索与阅读交互](../search-and-reading-experience/)**：两层离线全文检索（支持繁简互通）、快捷键、打印注释与文末二维码、页面即时预渲染。
7. **[少即是多：静态博客的依赖取舍](../on-minimalism/)**：尽量不引入冗余外界依赖的工程取舍，以及各项特性在Gzip与Brotli下的真实尺寸对比。

