---
title: "少即是多：静态博客的依赖取舍"
date: 2024-10-15
description: "探讨尽量不引入冗余外界依赖的工程取舍，以及各项资源特性的实际体积对比。"
categories: ["随笔"]
tags: ["性能", "Web", "Chaos", "排版"]
series: "Chaos 主题指南"
---

以文字内容为主的博客，真正依赖客户端脚本的交互并不繁复：
外观模式切换、移动端导航折叠、代码复制以及目录的滚动定位。
其余呈现与版面布局，现代HTML与CSS标准已完全足以胜任。

<!--more-->

## 避免引入冗余依赖

主题的设计原则是**避免引入不必要的外部依赖**。凡可通过标准HTML与CSS实现的功能
（如深浅外观、响应式版面排版），均不引入额外的运行时脚本。

数学公式在站点构建时直接编译为HTML与[MathML](https://developer.mozilla.org/en-US/docs/Web/MathML)，
图片交由Hugo处理生成[WebP](https://zh.wikipedia.org/wiki/WebP)，
页面跳转过渡则依托浏览器原生的[Speculation Rules](https://developer.mozilla.org/en-US/docs/Web/API/Speculation_Rules_API)
与[View Transitions](https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API)规范。

## 资源尺寸对照

现代Web服务器与浏览器通常支持压缩效率更高的[Brotli](https://zh.wikipedia.org/wiki/Brotli)，
同时向下兼容历史更久的[Gzip](https://zh.wikipedia.org/wiki/Gzip)。

以下数据测自主题 `v1.0.0`，供使用者参考；随版本演进，具体尺寸可能略有浮动：

| 资源与特性 | 加载形式 | 原始尺寸 | Gzip 压缩 | Brotli 压缩 | 说明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 主题核心样式(CSS) | 基础资源 | 约 32 KB | 约 8 KB | 约 7 KB | 基础配色、排版、深浅色、响应式网格 |
| 等宽字体子集(WOFF2) | 按需加载 | 约 16 KB | - | - | [Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono) 拉丁子集，用于代码与数字（本身已压缩） |
| 核心脚本(main.js) | 基础资源 | 约 6 KB | 约 2 KB | 约 2 KB | 深浅色切换、移动端菜单、代码复制、目录高亮 |
| 全文检索模块(search.js) | 可选加载 | 约 5 KB | 约 2 KB | 约 2 KB | 离线索引检索驱动，不含按需获取的索引数据文件 |
| KaTeX样式与字体 | 按需加载 | 样式约 25 KB | 样式约 4 KB | 样式约 3 KB | 显示公式时还会下载所需的字体切片（每切片约3~27 KB） |
| Mermaid运行时(JS) | 按需加载 | 约 3570 KB | 约 980 KB | 约 750 KB | 仅在正文包含Mermaid图表时单页按需载入 |

> [!NOTE]
> 关于字体的说明：
> - **正文与标题**：优先使用用户操作系统的默认无衬线字体，不依赖外部网络字体。
> - **等宽字体**：内置精简后的[Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono)拉丁字母与数字子集（约 16 KB），确保代码与数字排版等宽，中文注释则回退至系统内置字体。[WOFF2](https://en.wikipedia.org/wiki/Web_Open_Font_Format)格式内部已采用Brotli压缩，网络传输大小即为文件本身大小。
> - **数学公式**：KaTeX样式表约25 KB；公式中的特殊符号（如积分号、希腊字母）由浏览器按需下载对应的WOFF2字体文件，单个切片约3 KB至27 KB不等，常规公式页面通常只需获取两至三个切片。
