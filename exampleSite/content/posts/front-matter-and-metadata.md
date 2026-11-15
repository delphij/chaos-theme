---
title: "文章元数据与内容控制"
date: 2026-09-15
description: "介绍Chaos主题在Front Matter中支持的内容控制字段：内容过时降权、站内检索过滤、系列导航面板与标题段落链接。"
categories: ["指南"]
tags: ["Chaos", "Markdown", "元数据", "配置"]
series: "Chaos 主题指南"
---

在日常博客维护中，常会遇到早期技术文章失效、部分个人随笔不宜纳入站内检索、
或长篇内容需分篇连载等实际需求。Chaos在[Front Matter](https://gohugo.io/content-management/front-matter/)
中提供了若干字段以调控页面的呈现与索引行为。

<!--more-->

## 推荐的Front Matter结构

Chaos推荐使用[TOML](https://toml.io/)或[YAML](https://yaml.org/)
格式组织文章元数据。以下为兼顾搜索引擎检索与内容分类的典型配置：

```yaml
---
title: "文章标题"
date: 2026-09-15T10:00:00+08:00
description: "简明扼要的摘要，会作为页面的 meta description 输出，便于搜索引擎收录呈现。"
categories: ["指南"]
tags: ["系统设计", "Web"]
series: "Chaos 主题指南"
series_title: "元数据与内容控制" # 可选：在系列导航面板与系列汇总页中使用的简短篇名
# 内容控制开关（可选）：
deprecated: false
searchHidden: false
noindex: false
# 可交互代码参数（可选）：
code_vars:
  - name: host
    default: "router.example.net"
    desc: "网关主机名"
---
```

## 内容控制开关

### 1. 标记过时内容（`deprecated`）

对于成文较早、技术方案已废弃或配置已失效的文章，可显式声明：

```yaml
deprecated: true # 或 outdated: true
```

#### 实际效果
- **降低检索排序**：站内全文搜索算法会自动降低该文章的相关性得分（降权75%），避免早期方案影响对有效解答的检索。
- **状态视觉标识**：在站内搜索结果列表中，该文章标题后会附加`[已过时]`标签。

### 2. 排除站内检索（`searchHidden`）

如果希望内容不参与站内技术检索，可声明：

```yaml
searchHidden: true # 或 search: false
```

#### 实际效果
- 该文章**不编入站内离线搜索索引**。
- 文章仍正常发布，展示于首页与分类列表，并保留在[`sitemap.xml`](https://www.sitemaps.org/)中，外部搜索引擎仍可正常收录。

### 3. 避免搜索引擎索引（`noindex`）

若内容虽然仍然可以公开，但希望不被搜索引擎收录，则可声明：

```yaml
noindex: true
```

#### 实际效果
- 排除在站内搜索索引之外。
- 自动从`sitemap.xml`站点地图中移除。
- 页面`<head>`区域注入[`<meta name="robots" content="noindex, nofollow">`](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)，指示搜索引擎不要索引该页面，亦不跟踪页面中的超链接。

### 4. 发布页面但不列入任何集合（`build.list`）

若某篇内容需要生成独立网页供链接直接访问，但不希望出现在首页、分类、归档与站点地图等任何页面集合中，请直接使用Hugo原生的构建选项（旧版的`hidden`字段已移除，`excludedTypes`参数已标记弃用）：

```yaml
build:
  list: never
```

## 系列文章（`series`）

为多篇连载文章指定统一的`series`名称，并可按需设置简短的章节名`series_title`：

```yaml
series: "Chaos 主题指南"
series_title: "元数据与内容控制"
```

启用后，主题会围绕同一系列提供三处联动支持：

- **文末系列导航面板**：当同一系列下存在两篇及以上文章时，正文末尾会自动渲染按时间正序（从第一章读起）排列的章节目录卡片，并高亮当前所处篇章。
- **系列时间线汇总页**：访问`/series/`可按最近更新时间倒序浏览全站所有系列的时间线，进入具体系列页（如`/series/chaos-主题指南/`）则可查阅该系列全部篇目。
- **结构化元数据**：自动在[Open Graph](https://ogp.me/)元数据中注入同系列关联信息。

## 可交互代码参数（`code_vars`）

对于包含具体网络配置、系统管理命令或安装部署脚本的文章，可在Front Matter中通过`code_vars`声明允许读者动态调整的参数：

```yaml
code_vars:
  - name: host
    default: "router.example.net"
    desc: "网关主机名"
  - name: ip
    default: "192.0.2.1"
    desc: "网关管理IP"
```

### 实际效果

- **参数联动面板**：主题自动在首个匹配代码块上方挂载可折叠的参数面板，并将代码块内对应的默认值标记为可交互的`<var class="code-var">`。
- **全局同步与复制**：读者在面板或代码块中修改参数后，全文代码块即时同步，右上角复制按钮自动复制替换后的真实内容。
- **URL参数共享**：非默认修改自动同步至URL查询字符串（如`?host=node1.example.org`），便于分享与预设填入。
- **正文行内代码同步**：正文行内代码中的默认值同样跟随参数变化，也可直接编辑（标题除外）；正文本身讨论这些字面值时，可用`code_vars_inline: false`关闭。
- **局部代码块免替换**：通过 ```` ```text {code_vars="false"} ```` 可保留固定的输出或真实日志。

详细交互机制与配置规范参见[代码语法高亮、交互参数与Mermaid图表](../code-and-diagrams/#code-vars)。

## 扩展Markdown语法

### 标题段落链接与自定义锚点ID

文章正文的各级小标题（`h2`–`h6`）在鼠标悬停或键盘`Tab`聚焦时会自动浮现`#`锚点按钮，点击即可复制指向该节的完整链接（若页面带有已修改的`code_vars`查询参数亦会一并保留）并原地更新地址栏哈希。

默认情况下，Hugo会根据标题文本自动生成锚点ID。若标题包含特殊字符或需要稳定、简短的引用路径，可在标题后显式指定：

```markdown
### 核心架构与设计哲学 {#architecture}
```

渲染后对应的HTML元素将直接附带`id="architecture"`属性，便于在正文中通过`[跳转至架构](#architecture)`精确链接。

### 列表页摘要截断（`<!--more-->`）

在Markdown中单独放置一行`<!--more-->`：

```markdown
这是文章的导言部分，会完整显示在首页和列表页的摘要中。

<!--more-->

这是正文的后续展开部分，进入文章详情页后方可阅读。
```

藉此可自主控制摘要的截断位置，避免整篇长文在列表页完整展开，以维持版面整洁。

