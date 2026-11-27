---
title: "你好，Chaos"
date: 2026-09-12
description: "Chaos主题功能速览：设计理念、基础配置与系列指南索引。"
categories: ["指南"]
tags: ["Chaos", "Hugo", "入门"]
series: "Chaos 主题指南"
---

Chaos是一个面向个人博客、个人Wiki与技术知识库的极简[Hugo](https://gohugo.io/)主题：不依赖前端脚本框架，
仅用轻量原生脚本提供外观模式切换、自动目录、代码与标题链接复制、
即时页面导航以及针对中文排版的细致处理。

<!--more-->

## 设计理念

主题配色源自[日本传统色](https://zh.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E4%BC%A0%E7%BB%9F%E8%89%B2%E7%B3%BB)（[和色]^(wairo)）：日间以[]{#FBFAF5}[**生成り色**]{きなりいろ}为纸底、[]{#2B2B2B}[**黒**]^(kuro)与[]{#595857}[**墨**]^(sumi)为字墨，
辅以[]{#9E3D3F}[**蘇芳**]{すおう}与[]{#165E83}[**藍色**]{あいいろ}作为强调与链接色；夜间则采用沉静的[暖炭底色]{#151514}，配以[]{#DCDDDD}[**白鼠**]^(shiro-nezumi)、[]{#D69090}[**退紅**]^(arazome)与[]{#84B9CB}[**浅縹**]^(asa-hanada)。
兼顾素雅纸张质感与[WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/)规定的色彩对比度要求。

正如[Livid](https://www.v2ex.com/member/Livid)所说，「好的设计都带着爱心」。除了视觉上的克制与舒适，Chaos也投入了大量精力做好无障碍支持，
希望不同阅读方式与辅助工具的读者都能顺畅地读完每一篇文章：

- **清晰的语义结构与键盘导航**：严格维护页面地标（`<header>`、`<nav>`、`<main>`、`<search>`、`<footer>`）与标题层级，提供「跳至正文」入口、原生`<dialog>`焦点管理、清晰的`:focus-visible`焦点环，并去除列表卡片中指向同一目标的冗余链接，减少纯键盘用户的`Tab`负担。
- **对读屏软件与语音控制友好**：为「阅读全文」等短链接补充视觉隐藏上下文，确保可访问名称以可见文字开头（WCAG 2.5.3）；为表单控件建立显式`for`/`id`关联，并通过统一的`aria-live`区域播报主题切换与搜索结果状态。
- **尊重系统偏好与弹性排版**：正文与界面字号采用`rem`以响应浏览器缩放，全面兼容高对比度模式（`forced-colors`）与减弱动态效果偏好（`prefers-reduced-motion`），在关闭JavaScript时仍能完整阅读内容。

除时间线式的个人博客外，Chaos也通过纯配置支持目录索引式的个人Wiki与速查手册场景：开启`listStyle = "index"`、`hidePostDate`与`alwaysShowLastmod`即可将首页与归档切换为按分类或章节组织的紧凑目录，并配合自动补全标题的内链（`[](/path/)`）、可折叠的`[!DETAILS]`说明卡、交互式代码参数面板（`code_vars`）以及支持过时降权的离线全文检索，将长期维护的参考笔记串联成有机整体。

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

1. **[快速安装与部署：配置、构建脚本与上线指南](../quick-start/)**：三种安装方式、必选与可选`hugo.toml`配置、示例`build.sh`构建脚本，以及Nginx/`rsync`、GitHub Pages与Cloudflare Pages部署流程。
2. **[中文排版：汉字、西文与标点的混排处理](../chinese-typography/)**：中西文间距、标点挤压与悬挂、楷体与着重号、振假名与拼音注音、源码断行空格净化。
3. **[提示框的语义类型与语法](../alerts-and-callouts/)**：NOTE、TIP、IMPORTANT、WARNING、CAUTION、HISTORICAL、DISCLAIMER、可折叠的`DETAILS`卡片与`TAB`选项卡切换，以及自定义标题支持。
4. **[代码语法高亮、交互参数与Mermaid图表](../code-and-diagrams/)**：静态语法高亮、行号悬停联动、可交互代码参数（`code_vars`）、代码一键复制与Mermaid图表。
5. **[用KaTeX书写数学公式](../math-with-katex/)**：行内与块级公式、Goldmark passthrough配置与洛伦兹方程组。
6. **[文章元数据与内容控制](../front-matter-and-metadata/)**：`deprecated`（过时降权）、`searchHidden`（隐藏检索）、`noindex`（避免收录）、`series`（系列导航与时间线）与标题段落链接。
7. **[全文检索与阅读交互](../search-and-reading-experience/)**：两层离线全文检索（支持繁简互通）、快捷键、打印注释与文末二维码、页面即时预渲染。
8. **[引用外部数据：YouTube与X静态嵌入](../external-embeds/)**：响应式YouTube短代码与打印二维码降级，以及静态缓存零追踪脚本的X帖文卡片。
9. **[行内色卡与独立语录卡片](../color-swatches-and-quotes/)**：`[label]{#hex}` / `[]{#hex}` 行内十六进制色卡，以及带出处右对齐署名的`{.quote}`语录卡片。
10. **[对谈与剧本：对话体排版示例](../dialogue-and-scripts/)**：基于定义列表与`{.dialogue}` / `{.dialogue .script}`的访谈与剧本版式。
11. **[双语对照：两栏平行文本排版示例](../bilingual-parallel-text/)**：基于`{.bilingual}`（含`.even`与`.wide-ref`变体）的中外文平行对照与单栏防误选。
12. **[米字格与注音：字词展示排版示例](../mizige-copybook/)**：`{.mizige}`朱砂米字格字帖与整词/跨格义训注音。
13. **[竖排与古籍引文：直排、界栏、抬头与双行夹注](../vertical-typesetting/)**：`{.vertical}`独立竖排容器、乌丝栏/朱丝栏、篇名、双行夹注、行间旁批、圈点、抬头与自动分叶，附《岳阳楼记》与《前出师表》全文示例。
14. **[少即是多：静态博客的依赖取舍](../on-minimalism/)**：尽量不引入冗余外界依赖的工程取舍，以及各项特性在Gzip与Brotli下的真实尺寸对比。

如需一页对照全部组件的视觉效果，可查阅[组件一览样张](../specimen/)与[中西文混排样张](../typography-specimen/)。

