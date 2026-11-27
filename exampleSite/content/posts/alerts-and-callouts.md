---
title: "提示框的语义类型与语法"
date: 2026-05-04
description: "介绍Chaos主题支持的提示框类型：NOTE、TIP、IMPORTANT、WARNING、CAUTION、HISTORICAL、DISCLAIMER、可折叠的DETAILS与选项卡TAB，以及自定义标题与多语言适配。"
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

### 容器内嵌套外挂组件（代码块与对话列表）

顶层正文中的带行号代码块与`{.dialogue}`列表在宽屏下会将行号或话者外挂至左侧页边距；而放入`blockquote`、提示框或`[!DETAILS]`折叠卡片等有边界容器内时，主题会自动收拢外挂边距（`--prose-outdent: 0`），避免行号或左栏被卡片边界裁切。

> [!DETAILS]+ 折叠卡片内嵌套带行号代码块、自动换行代码块与 `{.dialogue .script}`
> 普通带行号代码块（行号收拢在代码块内部，不会被 `overflow: hidden` 裁掉）：
>
> ```go
> package main
>
> import "fmt"
>
> func main() {
> 	fmt.Println("line numbers stay inside the disclosure card")
> }
> ```
>
> 启用 `{.wrap}` 的长行代码块（行号计数器自动向内留出边距）：
>
> ```sh {.wrap}
> # 模拟一条较长的命令行，用于验证折叠卡片内启用 .wrap 时的折行挂钩与行号对齐效果
> hugo --minify --printI18nWarnings --printPathWarnings --panicOnWarning --baseURL https://example.org/docs/
> ```
>
> 嵌套的 `{.dialogue .script}` 列表（左栏留在卡片内部，不再向页边距外挂）：
>
> 09:00
> : 收到告警并确认受影响范围，开始采集日志。
>
> 09:15
> : 定位到上游配置变更，回滚并验证服务恢复正常。
> {.dialogue .script}

> [!NOTE]
> 普通引用块与非折叠提示框内的带行号代码块同样会自动收拢行号，不会穿透左侧边界：
>
> ```ini
> [server]
> host = 192.0.2.10
> port = 8443
> tls = true
> workers = 4
> ```

## 选项卡切换：`TAB` {#tabs}

当同一项配置或操作步骤存在多种等价写法（例如`TOML` / `YAML` / `JSON`，或不同操作系统的安装命令）时，将多个`> [!TAB] 标题`块连续写出即可自动编组为选项卡面板。

### 基本用法

只需要按顺序写出相邻的`> [!TAB] 标题`块（中间不穿插其他段落）；可选在首个块末尾附加`{group="组名" label="无障碍名称"}`：

````markdown {.wrap}
> [!TAB] TOML
> ```toml
> [params.search]
>   enable = true
> ```
{label="配置格式"}

> [!TAB] YAML
> ```yaml
> params:
>   search:
>     enable: true
> ```

> [!TAB] JSON
> ```json
> {
>   "params": {
>     "search": { "enable": true }
>   }
> }
> ```
````

渲染效果：

> [!TAB] TOML
> ```toml
> [params.search]
>   enable = true
> ```
{label="配置格式"}

> [!TAB] YAML
> ```yaml
> params:
>   search:
>     enable: true
> ```

> [!TAB] JSON
> ```json
> {
>   "params": {
>     "search": { "enable": true }
>   }
> }
> ```

### 自动联动、`.nogroup` 与嵌套能力

同一篇文章里，只要多组选项卡拥有相同的标签标题集合（顺序无关），就会**自动联动**，无需手写组名：切换其中任意一处时，其余同集合选项卡会同步切到同名标签。如果某组恰好使用了通用标题（如「方案一 / 方案二」）但不希望与页面其他选项卡联动，在首个`> [!TAB]`末尾加`{.nogroup}`即可退出；若两组标签互为子集（例如三选一与二选一）仍想联动，可显式附加`{group="组名"}`（选中对方不存在的标签时，对方保持原状不动）。

由于`> [!TAB]`与正文共享单次Goldmark主解析，选项卡内可自由嵌套带行号代码块、标准脚注与`> > [!NOTE]`提示框，且行号与列表编号同样自动收拢在卡片内部。试着在下面两组未声明`group`的选项卡之间点击切换（或用键盘左右方向键、`Home`、`End`切换）：

> [!TAB] macOS (Homebrew)
> 使用Homebrew安装Hugo与`xsltproc`（macOS已自带`xsltproc`）：
>
> ```sh
> brew install hugo
> hugo version
> ```
{label="安装 Hugo"}

> [!TAB] Debian / Ubuntu
> 从官方Release下载标准版二进制并安装`xsltproc`[^tab-xslt]：
>
> ```sh
> sudo apt-get update
> sudo apt-get install -y xsltproc
> ```

> [!TAB] FreeBSD
> 通过`pkg`直接安装：
>
> ```sh
> pkg install gohugo libxslt
> ```

第二步验证构建（未写`group`属性，切换上方系统标签时此处自动同步联动）：

> [!TAB] macOS (Homebrew)
> 本地预览并检查构建：
>
> ```sh
> hugo --gc --minify --panicOnWarning
> sh themes/chaos/tools/post_build.sh public
> python3 themes/chaos/tools/check.py --public public
> ```
>
> > [!NOTE]
> > 选项卡内的嵌套提示框、文末脚注与五行及以上带行号代码块均原生正常，行号不会穿透卡片左缘。
{label="验证构建"}

> [!TAB] Debian / Ubuntu
> 在Debian / Ubuntu上执行相同构建流程：
>
> ```sh
> hugo --gc --minify --panicOnWarning
> sh themes/chaos/tools/post_build.sh public
> python3 themes/chaos/tools/check.py --public public
> ```

> [!TAB] FreeBSD
> 在FreeBSD上执行相同构建流程：
>
> ```sh
> hugo --gc --minify --panicOnWarning
> sh themes/chaos/tools/post_build.sh public
> python3 themes/chaos/tools/check.py --public public
> ```

> [!TIP]
> **溢出跳转、搜索、打印与订阅源降级**：当选项较多超出容器宽度时，标签栏保持单行横向滚动并在截断边缘呈现柔和渐隐，同时在右侧显示`⋯`弹出菜单方便一键跳转；隐藏面板使用`hidden="until-found"`并监听`beforematch`事件，浏览器页内查找（`Cmd+F` / `Ctrl+F`）命中非当前标签内容时会自动切换展开；打印页面（`@media print`）与RSS/Atom订阅源则会将全部标签按各自标题顺序平铺展开，不遗漏任何方案。更多实战用法参见[](../quick-start/)。

[^tab-xslt]: 现代浏览器正逐步移除原生XSLT支持，`xsltproc`用于在构建后为`sitemap.xml`生成静态HTML伴生页，详见[快速安装与部署](../quick-start/#build-script)。
