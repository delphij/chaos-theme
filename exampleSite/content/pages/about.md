---
title: "关于"
date: 2026-01-01
type: "page"
url: "/about/"
---

这是[Chaos](https://github.com/delphij/chaos-theme)主题的示例站点（线上演示地址：<https://delphij.github.io/chaos-theme/>）。

Chaos是一个专为个人博客、个人Wiki与技术知识库设计的极简[Hugo](https://gohugo.io/)主题，注重资源精简、[无障碍访问](https://www.w3.org/WAI/fundamentals/accessibility-intro/zh-hans)与中文排版细节。站点收录的内容主要用于展示主题在文字排版、数学公式、图表渲染及内容组织等方面的功能与配置示例。

如需在自己的站点上安装与部署Chaos，请先阅读[](/posts/quick-start/)；如需一页对照全部组件与混排效果，可查阅[](/posts/specimen/)与[](/posts/typography-specimen/)。

## 本地预览

若需在本地预览本示例站点，可在主题根目录下执行：

```bash
# 可选但推荐：预先拉取自托管楷体与思源宋体切片（未执行时自动回退至系统字体）
python3 tools/fetch_webfonts.py --out exampleSite/static/_fonts --css-out exampleSite/assets/_fonts
# 如需体验站内离线检索
python3 tools/build_search_index.py --content exampleSite/content
# 启动本地开发服务器
hugo server --source exampleSite
```

