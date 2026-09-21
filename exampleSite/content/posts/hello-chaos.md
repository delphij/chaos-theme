+++
title = '你好，Chaos'
date = '2026-09-12'
description = 'Chaos 主题功能速览：深浅色模式、目录、即时导航与多语言支持。'
categories = ['主题']
tags = ['Hugo', 'Chaos', '入门']
series = 'Chaos 主题指南'
+++

Chaos 是一个极简的 Hugo 博客主题：没有 JavaScript 框架，全部脚本加起来大约 3KB，
却仍然提供了深浅色模式、自动目录、即时页面导航和完整的多语言支持。

<!--more-->

## 设计理念

主题的配色取自日本传统色（和色）：以白練为纸、以墨为字，用红緋与瑠璃色点缀链接和强调。
目标是让页面读起来像一张安静的纸，同时满足 WCAG 的对比度要求。

> [!TIP]
> 点击右上角的 🌓 按钮，可以在「跟随系统 / 浅色 / 深色」三种模式之间切换。

## 主要特性

- **性能优先**：依赖极少，样式与脚本经 Hugo Pipes 打包、压缩并附带 SRI 校验
- **响应式布局**：移动端优先，带毛玻璃效果的汉堡菜单
- **自动目录**：文章页右侧的目录会随滚动高亮当前章节
- **即时导航**：基于 Speculation Rules API 预渲染，回退到 instant.page
- **多语言**：内置简体中文、繁體中文、English、日本語、한국어

## 快速开始

```toml
theme = 'chaos'
languageCode = 'zh-cn'
defaultContentLanguage = 'zh-cn'

[params]
  subtitle = '支持 **Markdown** 的副标题'
```

## 下一步

本系列的后续文章会分别介绍中文排版、数学公式、提示框以及代码高亮。
