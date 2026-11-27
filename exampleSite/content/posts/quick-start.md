---
title: "快速安装与部署：配置、构建脚本与上线指南"
date: 2026-11-27
description: "Chaos主题中文快速上手：安装方式、推荐与可选hugo.toml配置、示例build.sh构建脚本，以及Nginx/rsync、GitHub Pages等常见部署流程。"
categories: ["指南"]
tags: ["Chaos", "Hugo", "入门", "部署"]
series: "Chaos 主题指南"
code_vars:
  - name: site_dir
    default: "my-blog"
    desc: "本地站点目录名"
  - name: domain
    default: "blog.example.org"
    desc: "站点正式域名"
  - name: site_title
    default: "我的博客"
    desc: "站点标题"
  - name: author
    default: "作者名"
    desc: "默认作者名"
  - name: github_user
    default: "yourname"
    desc: "GitHub 用户名"
  - name: ssh_target
    default: "user@your-server"
    desc: "服务器 SSH 目标"
  - name: web_root
    default: "/var/www/blog"
    desc: "服务器站点根目录"
code_vars_inline: false
---

初次使用Chaos主题时，只需按安装主题、配置`hugo.toml`、编写构建脚本与部署上线这四步依次进行即可。

若只是预览主题效果，可以直接访问[线上演示站](https://delphij.github.io/chaos-theme/)[^preview-example]。

本文中的站点目录、域名、标题与服务器路径均可在线修改：展开首个代码块上方的参数面板，填好自己的取值，全文示例会随之同步更新。

<!--more-->

## 环境要求与安装方式 {#install}

Chaos要求 **Hugo 0.158.0或更高版本**（标准版即可，不依赖Extended版与Node.js）。按维护习惯任选以下一种安装方式：

> [!TAB] Git 子模块（推荐）
> 如果打算使用主题自带的`tools/`脚本（离线搜索索引、字体切片、构建后处理与自检），推荐以Git子模块方式引入，路径固定在`themes/chaos/`：
>
> ```sh
> hugo new site my-blog --format toml
> cd my-blog
> git init
> git submodule add https://github.com/delphij/chaos-theme.git themes/chaos
> ```
>
> 在站点根目录的`hugo.toml`中指定主题：
>
> ```toml
> theme = 'chaos'
> ```
>
> 日后升级主题只需更新子模块并提交指针：
>
> ```sh
> git submodule update --remote themes/chaos
> git add themes/chaos
> git commit -m "site: update chaos theme"
> ```
{label="安装方式"}

> [!TAB] Hugo Modules
> 若本机已安装Go工具链，也可通过Hugo Modules管理版本依赖：
>
> ```sh
> hugo mod init github.com/yourname/my-blog
> ```
>
> 在`hugo.toml`中导入模块（此时无需设置`theme = 'chaos'`）：
>
> ```toml
> [module]
>   [[module.imports]]
>     path = 'github.com/delphij/chaos-theme'
> ```
>
> 使用`hugo mod get -u github.com/delphij/chaos-theme`即可升级。需要注意，采用Hugo Modules时`themes/chaos/tools/`不会出现在工作区，若需运行搜索索引、字体或后处理脚本，应另行检出主题仓库。

> [!TAB] 发行版压缩包
> 从[GitHub Releases](https://github.com/delphij/chaos-theme/releases)下载`chaos-theme-<version>.tar.xz`，直接解压至`themes/`目录（会自动展开为`themes/chaos/`），再在`hugo.toml`中设置`theme = 'chaos'`：
>
> ```sh
> mkdir -p themes
> tar -xJf chaos-theme-<version>.tar.xz -C themes
> ```

## 推荐基础配置（`hugo.toml`） {#config}

Hugo只会合并主题配置中的部分区段（`[params]`、`[menus]`、`[markup]`等），而不会继承站点级配置与`[outputs]`。因此新建站点时，建议直接以`exampleSite/hugo.toml`为底本，保留以下必选与推荐项：

```toml
theme = 'chaos'
baseURL = 'https://blog.example.org/'
locale = 'zh-cn'
defaultContentLanguage = 'zh-cn'
title = '我的博客'

# 必须启用：让Hugo按字符统计中文字数并正常截断列表摘要
hasCJKLanguage = true

[pagination]
  pagerSize = 10

[taxonomies]
  category = 'categories'
  tag = 'tags'
  series = 'series'

# Hugo不会从主题继承[outputs]，必须显式声明才会生成Atom、RSS与XSLT样式表
[outputs]
  home = ['HTML', 'ATOM', 'sitemapxsl', 'RSS', 'feedxsl', 'REDIR']
  section = ['HTML']
  taxonomy = ['HTML']
  term = ['HTML']

# 解析期折叠中文段落中的软换行，避免源码72列折行产生多余空格
[markup.goldmark.extensions.cjk]
  enable = true
  eastAsianLineBreaks = true
  eastAsianLineBreaksStyle = 'css3draft'
  escapedSpace = true

# 代码块使用CSS类而非内联style，配合主题的浅/深色和色配色
[markup.highlight]
  noClasses = false

# 块级属性支持（{.mizige}、{.vertical}、{.bilingual}、{.dialogue}等）
[markup.goldmark.parser.attribute]
  block = true

# KaTeX数学公式透传（仅在包含公式的页面按需加载KaTeX）
[markup.goldmark.extensions.passthrough]
  enable = true
  [markup.goldmark.extensions.passthrough.delimiters]
    block = [['$$', '$$']]
    inline = [['\(', '\)']]

[menus]
  [[menus.main]]
    identifier = 'home'
    pageRef = '/'
    weight = 10

  [[menus.main]]
    identifier = 'archives'
    pageRef = '/archives'
    weight = 20

  [[menus.main]]
    identifier = 'categories'
    pageRef = '/categories'
    weight = 30

  [[menus.main]]
    identifier = 'series'
    pageRef = '/series'
    weight = 35

  [[menus.main]]
    identifier = 'tags'
    pageRef = '/tags'
    weight = 40

  [[menus.main]]
    name = '关于'
    pageRef = '/pages/about'
    weight = 50

[params]
  subtitle = '副标题（支持*Markdown*）'
  description = '站点SEO与订阅源描述'
  mainSections = ['posts']

  [params.author]
    name = '作者名'
```

> [!IMPORTANT]
> 导航菜单请使用`pageRef`而非硬编码`url`，这样主题才能自动高亮当前所在栏目并通过`check.py`的导航自检。同时建议创建`content/archives/_index.md`（只需`title: "归档"`）以启用归档页。

> [!DETAILS] 推荐目录结构与 `.gitignore` 示例
> 新建站点时可参考以下目录组织：
>
> ```text
> my-blog/
> ├── content/
> │   ├── archives/_index.md    # 归档页入口
> │   ├── pages/about.md        # 独立静态页（如关于页）
> │   └── posts/                # 博客文章（建议按 YYYY/MM/slug/index.md 组织）
> ├── themes/chaos/             # 主题子模块
> ├── build.sh                  # 构建脚本
> └── hugo.toml                 # 站点配置
> ```
>
> 若启用了离线搜索或自托管中文字体，建议在`.gitignore`中排除构建期生成目录：
>
> ```gitignore {code_vars="false"}
> public/
> resources/
> assets/_data/
> assets/_fonts/
> static/_fonts/
> ```

### 准备自托管中文字体（`fetch_webfonts.py`） {#webfonts}

大多数桌面与移动系统并未默认预装楷体，因此推荐在`hugo.toml`中开启`[params.webfonts] enable = true`，并在本地`hugo server`预览或线上部署前运行一次字体切片脚本（即使未运行也不会报错，CSS仍会自动回退至访客本机的系统字体，只是米字格、楷体强调与竖排古籍的字形效果会打折扣）：

```sh
python3 themes/chaos/tools/fetch_webfonts.py --cleanup
```

脚本会按`themes/chaos/assets/data/webfonts.json`中锁定的SHA-512校验值下载开源楷体（米字格与`*...*`强调）及思源宋体（竖排古籍），按常用字频次切分为按需加载的WOFF2子集并写入`static/_fonts/`与`assets/_fonts/`：

- **首次运行**：需要Python的`fonttools`与`brotli`（如Debian/Ubuntu安装`python3-fonttools python3-brotli`，macOS可用`pip3 install fonttools brotli`）；上游字体包会缓存到`${XDG_CACHE_HOME:-~/.cache}/chaos-webfonts/`。
- **后续运行**：已通过校验的切片会仅凭Python标准库直接跳过，不访问网络、也不重复切片；`--cleanup`会顺带清理旧版本的残留切片。

## 常用可选项 {#options}

以下选项默认关闭或取保守值，可按需在`hugo.toml`中开启（详细参数与行为见文末脚注）：

| 功能 | 配置入口 | 构建脚本配合 |
| :--- | :--- | :--- |
| 离线全文检索[^opt-search] | `[params.search]` `enable = true` | `hugo`前运行`build_search_index.py` |
| 自托管中文字体[^opt-webfonts] | `[params.webfonts]` `enable = true` | `hugo`前运行`fetch_webfonts.py --cleanup` |
| 站点地图可读伴生页（SEO）[^opt-xsl] | 默认随`sitemapxsl`启用 | `hugo`后运行`post_build.sh`（需`xsltproc`） |
| Remark42评论[^opt-remark] | `[params]` `remarkURL`等 | 无 |
| Wiki / 知识库模式[^opt-wiki] | `[params]` `listStyle = "index"`等 | 无 |
| 代码块默认软折行[^opt-codewrap] | `[params]` `codeWrap = true` | 无 |
| 任务列表勾选样式[^opt-task] | `[params]` `taskListChecked` | 无 |
| 时间戳与翻页范围[^opt-pager] | `[params]` `showTime` / `pagerScope` / `pagerOrder` | 无 |
| 分类/标签展示过滤[^opt-tax] | `[params]` `excludedCategories` / `excludedTags` / `featuredCategories` | 无 |
| 路径重定向与`/llms.txt`[^opt-route] | `[params]` `redirects` / `[outputs]`追加`'LLMS'` | 无 |

## 示例构建脚本（`build.sh`） {#build-script}

由于现代浏览器已逐步淘汰原生XSLT支持，只要启用了站点地图（SEO），构建后通过`post_build.sh`调用`xsltproc`生成`sitemap.xml.html`伴生页就不再是可选项，而是标准构建流程的一部分。下面是一份可直接改用的站点根目录`build.sh`：

```sh
#!/bin/sh
# Chaos 站点完整构建脚本示例（按站点配置启用或注释可选步骤）
# 必选依赖：hugo (>= 0.158.0)、xsltproc（站点地图伴生页，启用 SEO 站点地图时必需）
# 可选依赖：python3（搜索/字体/自检）、brotli、gzip（或 ect / zopfli）

set -eu

PUBLIC_DIR="${1:-public}"
TOOLS_DIR="themes/chaos/tools"

# 1. 可选：启用 [params.webfonts] enable = true 时取消注释，在 hugo 之前准备字体切片
# python3 "$TOOLS_DIR/fetch_webfonts.py" --cleanup

# 2. 可选：启用 [params.search] enable = true 时保留，在 hugo 之前生成离线搜索索引
#    若部署在子路径（如 https://yourname.github.io/my-blog/），追加 --base-url "/my-blog/"
python3 "$TOOLS_DIR/build_search_index.py"

# 3. 执行 Hugo 生产构建
#    --panicOnWarning 配合 --printI18nWarnings / --printPathWarnings
#    可在翻译缺失或输出路径冲突时第一时间中止构建
hugo --minify \
  --cleanDestinationDir \
  --destination "$PUBLIC_DIR" \
  --printI18nWarnings \
  --printPathWarnings \
  --panicOnWarning

# 4. 运行主题内置自检（检查 feed 空白、XSLT 合法性、菜单高亮、搜索链接、JSON-LD 等）
python3 "$TOOLS_DIR/check.py" --public "$PUBLIC_DIR"

# 5. 运行主题构建后处理（压缩 XSLT 空白 + 用 xsltproc 为 sitemap.xml 生成静态 HTML 伴生页）
sh "$TOOLS_DIR/post_build.sh" "$PUBLIC_DIR"

# 6. 可选：自建 Nginx/Caddy 时预生成 .br 与 .gz 静态压缩文件，降低线上 CPU 开销
if command -v brotli >/dev/null 2>&1; then
  find "$PUBLIC_DIR" -type f \
    \( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.json' \
       -o -name '*.xml' -o -name '*.xsl' -o -name '*.svg' -o -name '*.txt' \) \
    -size +256c -print0 | xargs -0 -P 4 -n 8 brotli -k -f --best
fi
# gzip 预压缩：追求更小体积时可用 ect（Efficient Compression Tool）或 zopfli 替代 gzip -9
if command -v gzip >/dev/null 2>&1; then
  find "$PUBLIC_DIR" -type f \
    \( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.json' \
       -o -name '*.xml' -o -name '*.xsl' -o -name '*.svg' -o -name '*.txt' \) \
    -size +256c -print0 | xargs -0 -P 4 -n 8 gzip -k -f -9
fi
```

> [!TIP]
> 写作阶段仍使用`hugo server -D`做实时热重载预览；只有准备发布时才运行`sh build.sh`。对于静态预压缩的`.gz`文件，若构建耗时不敏感、希望进一步压低传输体积，可用[ect](https://github.com/fhanau/Efficient-Compression-Tool)（`ect -9 -gzip -keep`）或[zopfli](https://github.com/google/zopfli)替代标准`gzip -9`，在完全兼容gzip协议的前提下通常还能再省下3%–5%体积。

## 常见部署方式 {#deploy}

Chaos生成的是纯静态文件目录（`public/`），不依赖后端运行时，可按托管环境选择以下常见部署方式：

> [!TAB] 自建服务器（rsync + Nginx）
> 适合自备VPS或独立主机的场景，也是能完整发挥Brotli/Gzip预压缩与`sitemap.xml`伴生页能力的部署方式。
>
> 1. **同步产物**：在`build.sh`末尾追加`rsync`同步命令。建议加上 `-O`（`--omit-dir-times`，避免Hugo每次重建目录mtime导致无谓刷新）与 `--delay-updates --delete-after`（先传完新文件再原子替换并清理旧文件，避免部署瞬间出现404）：
>
> ```sh
> rsync -zzavO --delete --delay-updates --delete-after \
>   public/ user@your-server:/var/www/blog/
> ```
>
> 2. **Nginx推荐配置**：现代浏览器在HTTPS连接中默认优先请求Brotli，因此建议同时开启`brotli_static on;`[^nginx-brotli]与`gzip_static on;`；带哈希指纹的静态资源可设为长期缓存，并按`Sec-Fetch-Dest`将浏览器对`/sitemap.xml`的访问改由`post_build.sh`生成的`sitemap.xml.html`响应（爬虫仍获取原始XML）：
>
> ```nginx
> # 放在 http {} 块中
> map $http_sec_fetch_dest $xslc_nav {
>     default  "";
>     document ".html";
> }
>
> server {
>     listen 443 ssl http2;
>     server_name blog.example.org;
>     root /var/www/blog;
>     index index.html;
>
>     # 启用构建期预生成的静态压缩文件（浏览器优先协商 Brotli，旧客户端回退 Gzip）
>     brotli_static on;
>     gzip_static on;
>
>     # 浏览器直接打开 sitemap.xml 时展示伴生 HTML，爬虫保持纯 XML
>     location = /sitemap.xml {
>         add_header Vary "Sec-Fetch-Dest";
>         try_files $uri$xslc_nav $uri =404;
>     }
>
>     # 带哈希指纹的资源与字体切片可长期缓存
>     location ~* ^/(_fonts/|css/|js/|.*\.[0-9a-f]{16,}\.(css|js|webp|woff2))$ {
>         add_header Cache-Control "public, max-age=31536000, immutable";
>     }
>
>     location / {
>         try_files $uri $uri/ =404;
>     }
> }
> ```
>
> > [!NOTE]
> > Nginx子`location`中一旦写了`add_header`，会覆盖外层`server {}`继承的安全响应头（如`Strict-Transport-Security`、`X-Content-Type-Options`）；如果外层设置了统一响应头，记得在子`location`中一并补齐或通过`include`复用。
{label="部署方式"}

> [!TAB] GitHub Pages
> 使用GitHub Pages时，无需提交`public/`，在站点仓库新增`.github/workflows/deploy.yml`即可在每次推送`main`时自动构建并发布（若部署在仓库子路径`https://yourname.github.io/my-blog/`，记得同步传给`build_search_index.py`的 `--base-url` 与`hugo`的 `--baseURL`）：
>
> ```yaml
> name: Deploy Chaos Blog
>
> on:
>   push:
>     branches: [main]
>   workflow_dispatch:
>
> permissions:
>   contents: read
>   pages: write
>   id-token: write
>
> concurrency:
>   group: pages
>   cancel-in-progress: false
>
> jobs:
>   build:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v4
>         with:
>           submodules: recursive
>
>       - name: Install Hugo
>         run: |
>           HUGO_VERSION="0.170.1"
>           curl -fsSL "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz" \
>             | tar -xz -C /usr/local/bin hugo
>
>       - name: Cache self-hosted webfonts
>         id: webfonts-cache
>         uses: actions/cache@v4
>         with:
>           path: |
>             static/_fonts
>             assets/_fonts
>           key: webfonts-${{ hashFiles('themes/chaos/assets/data/webfonts.json', 'themes/chaos/tools/fetch_webfonts.py') }}
>
>       - name: Build site
>         run: |
>           sudo apt-get update -q
>           pkgs="xsltproc"
>           if [ "${{ steps.webfonts-cache.outputs.cache-hit }}" != "true" ]; then
>             pkgs="$pkgs python3-fonttools python3-brotli"
>           fi
>           sudo apt-get install -y -q --no-install-recommends $pkgs
>           # 如未开启 webfonts 或 search，可注释对应行
>           python3 themes/chaos/tools/fetch_webfonts.py --cleanup
>           python3 themes/chaos/tools/build_search_index.py
>           hugo --gc --minify --panicOnWarning --printI18nWarnings --printPathWarnings
>           python3 themes/chaos/tools/check.py --public public
>           sh themes/chaos/tools/post_build.sh public
>
>       - uses: actions/upload-pages-artifact@v3
>         with:
>           path: public
>
>   deploy:
>     needs: build
>     runs-on: ubuntu-latest
>     environment:
>       name: github-pages
>       url: ${{ steps.deployment.outputs.page_url }}
>     steps:
>       - id: deployment
>         uses: actions/deploy-pages@v4
> ```

> [!TAB] Cloudflare Pages / Netlify
> Cloudflare Pages与Netlify均支持直接连接Git仓库自动构建，只需在平台后台做两处设置：
>
> 1. **指定Hugo版本**：在环境变量中设置`HUGO_VERSION = 0.170.1`（或任意≥`0.158.0`的版本，避免平台默认回退到过旧的Hugo）。
> 2. **设置构建命令与输出目录**：
>    - 构建命令：`sh build.sh`（若不需要预压缩与字体拉取，也可精简为`python3 themes/chaos/tools/build_search_index.py && hugo --gc --minify --panicOnWarning && sh themes/chaos/tools/post_build.sh public`；CDN边缘节点会自动处理Brotli/Gzip压缩）。
>    - 输出目录：`public`。

## 首次上线前检查清单 {#checklist}

- `baseURL`已改为正式HTTPS域名且以`/`结尾。
- `hasCJKLanguage = true`与`[markup.goldmark.extensions.cjk]`均已启用，文章字数统计与首页摘要截断正常。
- 已安装`xsltproc`并运行`post_build.sh`，确认`public/sitemap.xml.html`已生成。
- 运行`python3 themes/chaos/tools/check.py --public public`无报错。
- 在浅色与深色模式下各检查一次首页、文章页、归档页与搜索弹窗，确认菜单高亮、字体与链接均正常。

[^preview-example]: 如需在本地运行演示站，可在主题根目录执行`hugo server --source exampleSite`。`exampleSite/hugo.toml`默认开启了自托管中文字体（`[params.webfonts]`），缺失切片时会自动回退到系统字体；若希望看到完整的开源楷体（米字格、楷体强调）与思源宋体（竖排古籍）效果，可先执行`python3 tools/fetch_webfonts.py --out exampleSite/static/_fonts --css-out exampleSite/assets/_fonts`（如需体验站内检索，再执行`python3 tools/build_search_index.py --content exampleSite/content`）。
[^opt-search]: 启用后在导航栏展示搜索按钮并支持`/`快捷键；可追加`fingerprint = true`为索引文件附加内容哈希，详见[全文检索与阅读交互](../search-and-reading-experience/)。
[^opt-webfonts]: 按字频切片自托管开源楷体（米字格与`*...*`强调）与思源宋体（竖排古籍），执行方式与依赖见上文[准备自托管中文字体](#webfonts)小节。
[^opt-xsl]: 现代浏览器正逐步移除原生XSLT支持。订阅源（`atom.xml` / `index.xml`）由主题内嵌的`polyxslt`在浏览器端完成渲染；而`sitemap.xml`必须保持标准的sitemaps.org XML格式、不能夹带脚本，因此需要在构建时用`xsltproc`预生成`sitemap.xml.html`伴生页，再由Web服务器按`Sec-Fetch-Dest`请求头返回给浏览器。
[^opt-remark]: 配置自托管[Remark42](https://remark42.com/)评论系统，常用字段为`remarkURL = "https://remark.example.org"`、`remarkSiteId = "remark"`、`remarkLocale = "zh"`与`remarkNoFooter = "true"`。
[^opt-wiki]: 配合`listStyle = "index"`、`hidePostDate = true`、`hideReadingStats = true`、`alwaysShowLastmod = true`与`categoryPreviewCount = 10`可将站点切换为紧凑目录式的个人Wiki或速查手册，并支持通过Hugo的`[[cascade]]`按栏目单独覆写。
[^opt-codewrap]: 全局默认开启代码块软折行；单篇文章可在Front Matter中用`codeWrap`覆写，单个代码块可用`{.wrap}` / `{.nowrap}`按需开关。
[^opt-task]: 支持`"none"`（默认，仅勾选框）、`"muted"`（文字弱化）或`"strikethrough"`（弱化加删除线）；单篇文章可用`taskListChecked`覆写，单个列表可用`{.task-plain}` / `{.task-muted}` / `{.task-strike}`控制。
[^opt-pager]: `showTime`控制是否显示`HH:MM`（省略为自动检测，`true`/`false`全局强制）；`pagerScope`设翻页范围（`"section"` / `"mainSections"` / `"site"`），`pagerOrder`设排序方式（`"date"` / `"section"` / `"category"` / `"title"`）。
[^opt-tax]: `excludedCategories`与`excludedTags`用于隐藏不想出现在首页「核心分类」或「热门标签」中的条目；`featuredCategories`可置顶指定分类，`featuredCategoriesRecentYears`控制按近期活跃度排序的时间窗口（默认5年，设0按全量统计）。
[^opt-route]: `redirects = [{ from = "/posts/", to = "/archives/" }]`会在`/redirects.txt`生成重定向规则并将源路径排除出站点地图，可配合`archiveBreadcrumbSections = ["posts"]`同步调整面包屑；在`[outputs]`的`home`列表中追加`'LLMS'`可生成`/llms.txt`（可用`[params.llms] limit = 0`限制条数）。
[^nginx-brotli]: 需Nginx已加载`ngx_brotli`模块（大多数现代Linux发行版及FreeBSD均提供`nginx-module-brotli`或`www/nginx`编译选项；Caddy则原生支持预压缩文件）。
