---
title: "引用外部数据：YouTube与X静态嵌入"
date: 2026-11-18
description: "介绍如何在Chaos主题中嵌入YouTube视频与静态缓存的X（Twitter）帖子，兼顾页面性能、打印二维码降级与访客隐私。"
categories: ["指南"]
tags: ["Chaos", "YouTube", "X", "短代码", "隐私"]
series: "Chaos 主题指南"
code_vars:
  - name: youtube_id
    default: "aqz-KE-bpKQ"
    desc: "YouTube视频ID"
  - name: x_user
    default: "delphij"
    desc: "X用户名"
  - name: x_id
    default: "204125811366830080"
    desc: "X帖文ID"
---

在技术博客中常需要引用外部视频或社交平台上的原帖。
为了避免第三方嵌入脚本拖慢页面加载、追踪访客或因原帖删除而失效，
Chaos为YouTube与X（Twitter）分别设计了兼顾屏幕阅读、打印与订阅源的静态化嵌入方案。

<!--more-->

> [!TIP]
> X（Twitter）静态卡片需要在构建前运行`python3 themes/chaos/tools/fetch_x_embed.py`将目标帖文抓取并清洗到站点的`data/x_embeds/`目录（依赖Python 3与外网访问）；未缓存对应帖文时短代码仅输出降级链接。YouTube嵌入无需构建期工具，播放时按需加载官方播放器。

## YouTube视频嵌入（`youtube`）

主题内置的`youtube`短代码支持位置参数与命名参数两种写法：

```markdown {.wrap}
{{</* youtube aqz-KE-bpKQ */>}}

{{</* youtube id="aqz-KE-bpKQ" title="Big Buck Bunny (Blender Foundation)" start=10 */>}}
```

以Blender Foundation的开源动画短片*Big Buck Bunny*为例，实际渲染效果如下：

{{< youtube id="aqz-KE-bpKQ" title="Big Buck Bunny (Blender Foundation)" >}}

该短代码针对不同阅读媒介做了三层适配：

- **桌面与移动屏幕**：生成响应式`16:9`容器并设置`loading="lazy"`，无需内联样式技巧即可自适应版心宽度。
- **打印与导出PDF**：自动隐藏视频播放框，并在原地替换为紧凑的二维码卡片与`youtu.be/...`短链接（二维码图片仅在`@media print`下加载，平时零额外请求；其它打印优化见[全文检索与阅读交互](../search-and-reading-experience/#打印与导出pdf)）。
- **RSS / Atom订阅源**：外包一层`<figure>`并在`<figcaption>`中附带直达观看链接，确保在剥离`<iframe>`的阅读器里也能顺利打开视频。

> [!TIP]
> 若站点配置了`[privacy.youtube] privacyEnhanced = true`，短代码会自动切换至`youtube-nocookie.com`域名。

## X（Twitter）静态卡片（`x`）

官方的X嵌入脚本会在客户端加载大量外部JavaScript并追踪读者。
Chaos改为在构建前由`tools/fetch_x_embed.py`预先抓取帖子正文并清洗掉所有`<script>`、事件处理器与`<iframe>`，
将纯静态数据缓存于站点的`data/x_embeds/`目录，构建时再由`x`短代码直接渲染为静态卡片。

先在终端抓取并缓存目标帖文（支持完整链接、纯ID或批量文件）：

```bash {.wrap}
python3 themes/chaos/tools/fetch_x_embed.py https://x.com/delphij/status/204125811366830080

# 批量抓取或刷新已有缓存：
python3 themes/chaos/tools/fetch_x_embed.py --batch tweets.txt
python3 themes/chaos/tools/fetch_x_embed.py --refresh 204125811366830080
```

随后在文章Markdown中通过短代码引用：

```markdown
{{</* x user="delphij" id="204125811366830080" */>}}
```

实际渲染效果如下：

{{< x user="delphij" id="204125811366830080" >}}

由于缓存文件直接纳入Git版本库，即使原帖日后被删除或网络受限，页面依然能够以极低的体积稳定呈现引用内容（更多关于零外部运行时依赖的取舍见[少即是多：静态博客的依赖取舍](../on-minimalism/)）。上方代码块已配合[`code_vars`](../code-and-diagrams/#code-vars)启用了参数联动，可在面板中直接修改视频ID与帖文参数。
