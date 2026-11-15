---
title: "全文检索与阅读交互"
date: 2026-09-18
description: "介绍Chaos主题的离线全文检索、打印排版与文末二维码、页面即时预渲染与无障碍辅助设计。"
categories: ["指南"]
tags: ["Chaos", "搜索", "性能", "排版", "无障碍"]
series: "Chaos 主题指南"
---

静态博客以文字阅读为主，但随文章积累，离线全文检索、纸质打印排版以及页面平滑导航等辅助支持亦不可或缺。
Chaos在不引入额外前端框架的前提下，提供了若干实用的交互功能。

<!--more-->

## 站内全文检索

Chaos内置了轻量级的客户端离线全文检索，无需依赖任何第三方外部搜索服务，原生支持中文分词、繁简互通（输入简体或繁体均可命中）、拉丁词单步拼写容错，并完整保留代码片段与`<ruby>`注音词条。

### 快捷键

- `/`：开启搜索界面并聚焦输入框。
- `↑` / `↓`：在检索结果之间切换选中项。
- `Enter`：打开当前选中的文章。
- `Esc`：关闭搜索界面。

### 两层索引设计

为兼顾搜索界面的即时响应与深层正文检索能力，索引采用两层零冗余设计：

1. **第一层（`search-index.json`）**：包含标题、分类、标签与链接等核心元数据及标题/标签倒排索引，体积精简，开启搜索界面时即时就绪。
2. **第二层（`search-index-body.json`）**：仅包含第一层未出现过的正文与代码片段词项，由前端在后台空闲时异步加载并静默合并。

### 索引生成与配置

在部署站点前，运行主题内置的Python脚本生成索引文件：

```bash
python3 themes/chaos/tools/build_search_index.py \
  --content content \
  --output assets/search-index.json
```

执行时，脚本会调用`hugo list published`读取实际发布的页面列表，默认同时生成核心索引（`assets/search-index.json`）与正文索引（`assets/search-index-body.json`）；若站点存在`data/stopwords.txt`，其中的自定义停用词会自动并入默认列表。将索引输出至`assets/`便于Hugo在构建时计算指纹（若希望增量部署时固定索引文件名、避免每篇文章随索引哈希改变而重传，可在`[params.search]`中设`fingerprint = false`并由服务器配置缓存重验证）。

#### 单文件索引选项（`--single-file`）

若不希望拆分为两份文件，可在生成时附加`--single-file`参数：

```bash
python3 themes/chaos/tools/build_search_index.py --single-file
```

此时脚本会将标题、标签、分类以及正文与代码的全部倒排词条合并打包进单个`assets/search-index.json`中，且不生成`-body.json`文件。页面的`search.js`脚本完全向下兼容此模式：当检测到不存在第二层索引时，会自动跳过异步请求，直接基于单文件执行全量检索。

**两种模式的工程权衡**：
- **两层索引（默认推荐）**：
  - **优势**：初始加载极快。开启搜索弹窗时仅需下载核心元数据（通常仅占总索引体积的10%～15%），即可立即响应键入；正文索引在后台空闲时静默合并，避免长文较多的站点初次开启时产生网络等待。
  - **代价**：需发起两次独立的静态资源请求，构建过程需同时管理两份索引文件。
- **单文件索引（`--single-file`）**：
  - **优势**：部署结构简单清晰，单次HTTP请求即可获取完整索引，便于静态文件归档或在限制并发请求数的环境下分发。
  - **代价**：随文章数量增加，单次请求的JSON体积相对较大，网络较慢或初次开启搜索时可能产生短暂停顿。

在`hugo.toml`中开启搜索支持与快捷键监听：

```toml
[params.search]
  enable = true
```

> [!NOTE]
> 启用搜索后，页面会按需引入独立的`search.js`，并在首次打开搜索面板时才请求索引数据（各项脚本与资源的具体体积对照见[少即是多：静态博客的依赖取舍](../on-minimalism/)）。

## 打印与导出PDF

纸质打印或导出PDF时，Chaos会自动隐藏导航栏与交互控件，并对长文引用与代码块做专门的版式重排（屏幕阅读完全不受影响）：

- **统一悬挂注释与可点击网址**：正文中的跨页链接（含外部链接与指向站内其他页面的内部链接；页内`#`锚点保持原样）与Markdown脚注按出现顺序合编为同一组「注释」，于正文之后、标签之前列出，编号悬挂于版心左侧。网址以等宽字体排印并省去默认端口的`https://`前缀与裸域名末尾斜杠，同时在导出的PDF中保留完整的可点击双向跳转。
- **代码块折行与悬挂行号**：带行号代码块在纸面上自动折行并将行号悬挂于左侧栏外；深色模式下的代码与Mermaid图表自动切换为浅色高对比度配色。
- **文末永久链接二维码**：文章末尾附带构建期生成的永久链接二维码（`qr/*.png`，仅在打印时请求加载）与站点名称，便于纸质读者扫码回到线上原文或参与讨论。

可在本页直接按下`Cmd + P`（或`Ctrl + P`）在浏览器打印预览中查验效果。例如正文中的这些链接：

- 查阅[Hugo官方网站](https://gohugo.io/)或站内的[少即是多：静态博客的依赖取舍](../on-minimalism/)。
- 查阅[MDN Web文档](https://developer.mozilla.org/)。
- 查看[W3C Speculation Rules规范](https://wicg.github.io/nav-speculation/speculation-rules.html)。

## 页面跳转与预渲染

主题利用现代浏览器原生的[Speculation Rules API](https://developer.mozilla.org/en-US/docs/Web/API/Speculation_Rules_API)，在指针悬停或轻触站内链接时预渲染目标页面，配合[CSS View Transitions](https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API)实现平滑过渡，无需引入外部路由框架。

## 无障碍辅助

- **跳过导航与键盘可达**：支持首项焦点直达正文（[Skip to content](https://www.w3.org/WAI/WCAG21/Techniques/general/G1)），章节标题聚焦自动浮现复制锚点，代码块仅在横向溢出需要滚动时才纳入`Tab`焦点序列。
- **语义控件与状态播报**：搜索弹窗遵循ARIA 1.2 `combobox`/`listbox`规范并实时播报检索状态与结果数；切换外观模式或复制内容时均通过[`aria-live`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Live_Regions)区域向辅助设备反馈。
- **色彩对比与高对比模式**：前景色与各级底色严格满足[WCAG 2.1 AA](https://www.w3.org/TR/WCAG21/)对比度要求，并在系统强制颜色模式（`forced-colors`）下自动补齐组件边界。

