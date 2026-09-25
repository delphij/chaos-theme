---
title: "全文检索与阅读交互"
date: 2026-09-18
description: "介绍 Chaos 主题的离线全文检索、打印外链自动转尾注、页面即时预渲染与无障碍辅助设计。"
categories: ["指南"]
tags: ["Chaos", "搜索", "性能", "排版", "无障碍"]
series: "Chaos 主题指南"
---

静态博客以文字阅读为主，但随文章积累，离线全文检索、纸质打印排版以及页面平滑导航等辅助支持亦不可或缺。
Chaos在不引入额外前端框架的前提下，提供了若干实用的交互功能。

<!--more-->

## 站内全文检索

Chaos内置了轻量级的客户端离线全文检索，无需依赖任何第三方外部搜索服务。

### 快捷键

- `/`：开启搜索界面并聚焦输入框。
- `↑` / `↓`：在检索结果之间切换选中项。
- `Enter`：打开当前选中的文章。
- `Esc`：关闭搜索界面。

### 两层索引设计

为兼顾搜索界面的即时响应与深层正文检索能力，索引采用两层分立设计：

1. **第一层（`search-index.json`）**：仅包含标题、分类、标签与链接等核心元数据，体积精简，开启搜索界面时即时就绪。
2. **第二层（`search-index-body.json`）**：包含正文与代码片段的倒排索引，由前端在后台空闲时异步加载，用于支持深层全文检索。

### 索引生成与配置

在部署站点前，运行主题内置的Python脚本生成索引文件：

```bash
python3 themes/chaos/tools/build_search_index.py \
  --content content \
  --output assets/search-index.json
```

执行时，脚本默认会同时生成核心索引（`assets/search-index.json`）并自动推导生成正文索引（`assets/search-index-body.json`）。将索引输出至 `assets/` 便于 Hugo 在构建时为其计算指纹（Fingerprint）。上述参数亦为该脚本的默认值。

#### 单文件索引选项（`--single-file`）

若不希望拆分为两份文件，可在生成时附加 `--single-file` 参数：

```bash
python3 themes/chaos/tools/build_search_index.py --single-file
```

此时脚本会将标题、标签、分类以及正文与代码的全部倒排词条合并打包进单个 `assets/search-index.json` 中，且不生成 `-body.json` 文件。页面的 `search.js` 脚本完全向下兼容此模式：当检测到不存在第二层索引时，会自动跳过异步请求，直接基于单文件执行全量检索。

**两种模式的工程权衡**：
- **两层索引（默认推荐）**：
  - **优势**：初始加载极快。开启搜索弹窗时仅需下载核心元数据（通常仅占总索引体积的10%～15%），即可立即响应键入；正文索引在后台空闲时静默合并，避免长文较多的站点初次开启时产生网络等待。
  - **代价**：需发起两次独立的静态资源请求，构建过程需同时管理两份索引文件。
- **单文件索引（`--single-file`）**：
  - **优势**：部署结构简单清晰，单次HTTP请求即可获取完整索引，便于静态文件归档或在限制并发请求数的环境下分发。
  - **代价**：随文章数量增加，单次请求的JSON体积相对较大，网络较慢或初次开启搜索时可能产生短暂停顿。

在 `hugo.toml` 中开启搜索支持与快捷键监听：

```toml
[params.search]
  enable = true
```

> [!NOTE]
> 主题核心脚本经压缩后仅约2 KB。启用搜索后，会额外引入约2 KB的`search.js`（未压缩约5 KB），并在开启搜索界面时按需载入索引数据。

## 打印与导出PDF

纸质打印或导出PDF时，原本的超链接在纸质媒介上无法交互。Chaos在打印样式中自动提取正文外部链接，于篇末按序号附列为参考链接列表，同时隐藏导航栏与侧边栏等交互控件。

可在本页直接按下 `Cmd + P`（或 `Ctrl + P`）在浏览器打印预览中查验效果。例如正文中的这些链接：

- 查阅 [Hugo 官方网站](https://gohugo.io/)。
- 查阅 [MDN Web 文档](https://developer.mozilla.org/)。
- 查看 [W3C Speculation Rules 规范](https://wicg.github.io/nav-speculation/speculation-rules.html)。

## 页面跳转与预渲染

主题利用现代浏览器原生的 [Speculation Rules API](https://developer.mozilla.org/en-US/docs/Web/API/Speculation_Rules_API)，在指针悬停或轻触站内链接时预渲染目标页面，配合 [CSS View Transitions](https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API) 实现平滑过渡，无需引入外部路由框架。

## 无障碍辅助

- **跳过导航**：支持键盘焦点首项直达正文内容（[Skip to content](https://www.w3.org/WAI/WCAG21/Techniques/general/G1)）。
- **状态播报**：切换外观模式时利用 [`aria-live`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Live_Regions) 区域向辅助设备提供动态状态反馈。
- **色彩对比**：前景色与背景色严格遵循 [WCAG 2.1 AA](https://www.w3.org/TR/WCAG21/) 可访问性标准。


