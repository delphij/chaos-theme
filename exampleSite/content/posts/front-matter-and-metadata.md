---
title: "文章元数据与内容控制"
date: 2026-09-15
description: "介绍 Chaos 主题在 Front Matter 中支持的内容控制字段：内容过时降权、站内检索过滤、系列文章与自定义标题锚点。"
categories: ["指南"]
tags: ["Chaos", "Markdown", "元数据", "配置"]
series: "Chaos 主题指南"
---

在日常博客维护中，常会遇到早期技术文章失效、部分个人随笔不宜纳入站内检索、
或长篇内容需分篇连载等实际需求。Chaos在[Front Matter](https://gohugo.io/content-management/front-matter/)
中提供了若干字段以调控页面的呈现与索引行为。

<!--more-->

## 推荐的 Front Matter 结构

Chaos 推荐使用[TOML](https://toml.io/)或[YAML](https://yaml.org/)
格式组织文章元数据。以下为兼顾搜索引擎检索与内容分类的典型配置：

```yaml
---
title: "文章标题"
date: 2026-09-15T10:00:00+08:00
description: "简明扼要的摘要，会作为页面的 meta description 输出，便于搜索引擎收录呈现。"
categories: ["指南"]
tags: ["系统设计", "Web"]
series: "Chaos 主题指南"
# 内容控制开关（可选）：
deprecated: false
searchHidden: false
noindex: false
---
```

## 内容控制开关

### 1. 标记过时内容（`deprecated`）

对于成文较早、技术方案已废弃或配置已失效的文章，可显式声明：

```yaml
deprecated: true # 或 outdated: true
```

#### 实际效果
- **降低检索排序**：站内全文搜索算法会自动降低该文章的相关性得分（降权 75%），避免早期方案影响对有效解答的检索。
- **状态视觉标识**：在站内搜索结果列表中，该文章标题后会附加 `[已过时]` 标签。

### 2. 排除站内检索（`searchHidden`）

如果希望内容不参与站内技术检索。声明：

```yaml
searchHidden: true # 或 search: false
```

#### 实际效果
- 该文章**不编入站内离线搜索索引**。
- 文章仍正常发布，展示于首页与分类列表，并保留在 [`sitemap.xml`](https://www.sitemaps.org/) 中，外部搜索引擎仍可正常收录。

### 3. 避免搜索引擎索引（`noindex`）

若内容虽然仍然可以公开，但希望不被搜索引擎收录，则可声明：

```yaml
noindex: true
```

#### 实际效果
- 排除在站内搜索索引之外。
- 自动从 `sitemap.xml` 站点地图中移除。
- 页面 `<head>` 区域注入 [`<meta name="robots" content="noindex, nofollow">`](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)，指示搜索引擎不要索引该页面，亦不跟踪页面中的超链接。

## 系列文章（`series`）

为长篇连载指定统一的 `series` 名称：

```yaml
series: "Chaos 主题指南"
```

Chaos会自动关联同系列文章，并在[Open Graph](https://ogp.me/)元数据中注入系列信息。
配合站点的taxonomy配置，读者可通过`/series/chaos-主题指南/`查阅完整篇目列表。

## 扩展Markdown语法

### 自定义标题锚点ID

默认情况下，Hugo会根据标题文本自动生成锚点ID。若标题包含特殊字符或需要稳定、简短的引用路径，
可在标题后显式指定：

```markdown
### 核心架构与设计哲学 {#architecture}
```

渲染后对应的HTML元素将直接附带 `id="architecture"` 属性，便于在正文中通过 `[跳转至架构](#architecture)` 精确链接。

### 列表页摘要截断（`<!--more-->`）

在 Markdown 中单独放置一行 `<!--more-->`：

```markdown
这是文章的导言部分，会完整显示在首页和列表页的摘要中。

<!--more-->

这是正文的后续展开部分，进入文章详情页后方可阅读。
```

藉此可自主控制摘要的截断位置，避免整篇长文在列表页完整展开，以维持版面整洁。

