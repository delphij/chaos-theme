---
title: "样张：中西文混排与细节排版"
date: 2024-01-02
description: "用真实长度的技术段落检验中西文间距、全角标点挤压与悬挂、楷体字重补偿、着重号、长标识符软断行与列表对齐。"
categories: ["指南"]
tags: ["Chaos", "CJK", "中文排版", "样张"]
---

[组件一览](../specimen/)按顺序罗列每一类元素，但只有一两行短句看不出段落边缘、字重灰度与断行河流线。这一页改用接近真实技术文章的混排长段落，专门检验桌面端两端对齐与窄屏左对齐下的细节表现。

<!--more-->

## 两端对齐、标点挤压与行末悬挂 {#justification}

在桌面端`780px`版心（`16px`字号下每行约48个全角汉字、`1.7`倍行高）中，正文采用两端对齐（`text-align: justify`），依靠汉字之间的微量弹性吸收行尾余量；进入`768px`以下的窄屏后则切换为左对齐（`text-align: start`），避免每行字数过少时被西文单词撑开字距。观察本段右边缘与连续标点：当句中连续出现全角括号、引号与句读标点——例如「连续标点挤压（即OpenType的`chws`特性与CSS的`text-spacing-trim: normal`）」，或是《庄子·应帝王》所谓「日凿一窍，七日而浑沌死。」——相邻全角标点之间的多余半角留白应当自动收紧，如「（测试）」、「『内层引号』」，以及句尾的「括号加句号（像这样）。」同时，行首与行末的逗号、句号、引号在支持`hanging-punctuation`的浏览器中会探出版心边缘，使整段右侧维持齐整的汉字网格线。

源码不手动在中文与English或数字2026之间敲入空格，交由CSS的`text-autospace: normal`自动留出约`2px`（八分之一字宽）的匀称间隙，阅读FreeBSD 15.0、UTF-8编码、TLS 1.3握手、HTTP/3协议或WCAG 2.1 AA对比度规范时既不粘连也不松散。即便历史文章源码中习惯性地在汉字与西文之间输入了空格——例如 输入 空格 的 源码 与 **加粗文本** 或 *楷体文本* 以及 [普通链接](#justification) 两侧的空白——构建期模板也会将其剔除并统一交给`text-autospace`处理，使全站新旧文章保持同一种字距肌理。

## 粗体、楷体变体与着重号灰度对照 {#emphasis}

中文印刷传统里没有西文式的斜体字形，浏览器对无斜体中文字体直接施加机械斜切（伪斜体）会导致笔画重心失衡；而传统楷体或宋体的Regular字重（在`16px`下墨迹面积约`54–75px²`、字面率约`82%`）混入现代黑体正文（墨迹面积约`87px²`、字面率约`92%`）时，又往往显得单薄发虚、字号偏小。本段用来在正常阅读距离下微眯双眼检查整段灰度是否均匀：普通黑体正文之中穿插*一段中文楷体与Latin true italic混排的强调文字——包括「（强调段内的连续标点挤压）。」与FreeBSD内核中uma_zalloc的注释*，紧接着切回普通正文，再对比**纯字重加粗的粗体术语**、***同时启用加粗楷体与西文Bold Italic的粗斜体文字***，以及保持正体与常规字重、仅在字下加点的[着重号强调]{.}。理想状态下，*楷体或衬线回退片段*经过光学字重匹配与`106%`字面放大补偿，且全角标点保持黑体`1em`字宽并正常挤压后，视觉黑度、字高与标点间距应与前后黑体自然衔接，既不发灰塌陷，也不会撑高所在行的`1.7`倍行距。

下面几处组合检验行内嵌套时的退避细节：当[着重号内部夹带`inline_code`等宽标识符]{.}时，代码本身不打着重号圆点；当正文出现[内含[着重号]{.}的链接](#emphasis)或[整段着重号内嵌[局部链接](#emphasis)的写法]{.}时，链接的虚线下划线会向下让出空间，不与字下的圆点重叠粘连。

### 小标题中的*楷体变体*与`inline_code`比例 {#heading-inline}

> [!NOTE] 提示框标题（`600`半粗体）中的*楷体字重映射*与*Latin Italic*混排
> 检查小标题与提示框标题中的`*强调文字*`是否自动匹配到高一档的加粗楷体面，行内代码`0.9em`字号是否随父级标题与提示框字号等比缩放。

## 长标识符、路径与裸链接软断行 {#soft-breaks}

桌面端两端对齐最怕遇到无法折行的超长等宽标识符或URL：一旦整串字符掉到下一行，上一行仅剩的十几个汉字就会被强行拉出刺眼的空白「河流线」。构建期模板为16字符以上的行内代码与24字符以上的裸链接按URL排版惯例注入零宽软断点（`<wbr>`，复制文本时完全透明）：在点号、斜杠、反斜杠、双冒号、箭头与下划线处将分隔符留在下一行行首。试将浏览器窗口在`780px`至`1100px`之间缓慢拖动，观察这段混排文字中各标识符的折行位置：`security.bsd.unprivileged_idprio`、`td->td_sched->ke_runq->rq_queues`、`X509_V_FLAG_TRUSTED_FIRST`、`std::filesystem::directory_iterator`、`boost::asio::ip::tcp::socket`与DNS记录`_25._tcp.mail.example.com`会在分隔符前自然断开；路径`/.well-known/acme-challenge/long-token`、`~/.local/share/containers/storage.conf`、`../../usr/local/etc/pkg/repos/FreeBSD.conf`与Windows注册表项`HKEY_CURRENT_USER\Software\Microsoft\Office\11.0\Outlook\Security`保持`/.`、`~/`、`../`前缀完整，同时支持反斜杠分段折行；而Git范围`git diff c689f41..HEAD -- assets/css/prose.css`、命令行开关`--signed-tags=strip`、展开语法`call(...very_long_argument_list)`、通配符`content/posts/2026/**/*.md`以及版本号与IP地址`FreeBSD 14.2-RELEASE-p3 (GENERIC)`、`192.168.100.254/255.255.255.0`、`2001:db8:55aa::2`中的等号、连续点号、小数点与IPv6压缩冒号则绝不从中间拆散。

行内代码内部的字面空格与外侧符号边界同样需要兼顾：像`dig 域名 ds`或`mount -t zfs 池名 /mnt`这样包含中文占位符的命令，内部参数空格必须原样保留；而没有背景底色的行内代码紧邻汉字且以符号开头或结尾时——例如在源码中手敲了空格的 使用 `--bare` 参数、编辑 `/usr/local/etc/rc.conf` 文件、编写 `sh(1)` 脚本——由于`text-autospace`不在汉字与`-`、`/`、`)`之间留白，模板会保留这处唯一的视觉分隔；但若紧邻自带半角空白的全角标点（如 ， `/404.html` 、 `.` ，），多余空格仍会被干净剔除。超长裸链接则在协议头`://`、`=`与`&`之后，以及路径`/`、`?`与锚点`#`之前断行，例如查阅手册页<https://www.freebsd.org/cgi/man.cgi?query=arc4random_uniform&sektion=3&format=html#DESCRIPTION>或标准条目<https://en.wikipedia.org/wiki/C++#Standardization>时，上一行正文依然保持均匀紧凑。

汉字紧接一个以字母或数字开头的内联元素时，还要绕开Chromium的一处折行缺陷：当行尾汉字本身放得下、算上跨元素`text-autospace`的1/8字宽间隙才溢出时，Blink会把整个文本节点退回到上一个内联标签处，留下大半行空白。因此模板在这类元素前的最后一个可断行字元之前插入`<wbr>`，将回退限制在最后一个断行单元之内；开括号随这个字一起换行，紧邻的闭开标点保持半宽挤压，小假名、长音符与叠字符号则附着在前一字后而不会被拆到行首。在Chrome中拖动窗口宽度，观察下列元素前的行尾：先用`sysctl`查看当前取值，再按[FreeBSD手册](https://docs.freebsd.org/en/books/handbook/)的说明修改`/boot/loader.conf`，必要时**ZFS**的*ARC*上限也一并调整，遵循「先备份配置」（见`README.md`）的原则，然后「用`pkg`安装」所需软件；日文资料中的「キャッシュ`ARC`」与「ディレクトリー`DNLC`」则只会在`シュ`与`リー`前折行，不会在`ュ`或`ー`之前断开。

行内色卡同样不能独自留在行尾。色卡是不含文字的inline-block，Blink即使在它后面放了U+2060也照样断行，因此模板用`white-space: nowrap`把色卡与紧随其后的第一个单元绑在一起：短单元整体绑定，如[]{#9E3D3F}[蘇芳]{すおう}、[]{#165E83}`#165E83`与[**藍色**]{#165E83}；遇到较长的加粗、链接或行内代码，色卡移入该元素内部，只与首字绑定，长标签照常折行，如[**这条加粗色名标签故意写得很长以便观察它在窄屏上能否正常折行**]{#9E3D3F}、[[一条指向日本传统色维基百科条目的较长链接文字](https://zh.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E4%BC%A0%E7%BB%9F%E8%89%B2%E7%B3%BB)]{#165E83}以及路径[]{#595857}`/usr/local/share/chaos/swatches/sumi.css`。拖动窗口宽度时，色卡应始终与右侧紧邻的字留在同一行，而长标签本身可以在任意字间断开。

## 注音、义训与段落行距稳定性 {#ruby}

当段落中间穿插HTML `<ruby>`注音或「义训」双关注释时，小字号的`<rt>`注文应当安稳落在行间留白之内，不把所在行单独顶高而造成段落行距忽宽忽窄。这里在同一段连续排入日文振假名（主题浅色底色取自和色中的[]{#FBFAF5}[生成り色]{きなりいろ}，主色为[]{#9E3D3F}[蘇芳]{すおう}，链接取[]{#165E83}[藍色]{あいいろ}）、汉语拼音（《庄子》中的[儵]^(shū)、[忽]^(hū)与[浑沌]^(hùn dùn)）、注音符号（中文[排]^(ㄆㄞˊ)[版]^(ㄅㄢˇ)细节）以及技术写作常见的义训吐槽（把踩坑攒下的[经]{工}[验]{伤}写成文档，防止下一次[临时绕过方案]{永久线上架构}重演），供对照第一行至末行的基线间距是否始终如一；不支持`<ruby>`的阅读器则会由`<rp>`平稳退化为全角括号注记。

### 米字格字帖展示与楷体中宫对齐 {#mizige}

段落附加`{.mizige}`时排作居中展示的米字格大字字帖：格内汉字采用常规字重的原比例楷体（约占外框七成半，符合传统字帖「中宫收紧、四周留白」的比例），并针对不同字库的字面基线逐一校准，使汉字视觉重心精确落在米字虚线的中心交点上；上方`<rt>`注文固定为无衬线正体，在中轴线上与单格对齐并留出容纳`g`、`p`、`q`、`y`下延笔画与`ǚ`叠音符的呼吸间隙：

[青出于蓝]{qīng chū yú lán}
{.mizige}

语出《荀子·劝学》「青，取之于蓝，而青于蓝」，比喻学生胜过老师或后人超越前人。米字格仅承担题字展示锚点，紧随其后的释义保持普通正文的两端对齐与行宽节奏。下面再排入局部训诂与跨格义训的混排条目，检查无注音单字、单字训诂与双字连绵义训在同一行中的底边对齐与十字中心对位：

守[株]{树桩}待兔，[犹豫]{双声}不决
{.mizige}

格内只保留汉字、注音与脚注，其余行内标记在构建期拆格时剥去标签、只留文字。下面这条《礼记·礼运》选段同时混入了引号、加粗、斜体、普通着重号与包住注音的嵌套着重号，应当排出与纯文本完全一致的方格，引号向格外零宽悬挂，注音依旧逐字对位：

「**天下**为[公]{.}」，[[选]{xuǎn}贤]{.}与*能*
{.mizige}

行末硬换行与全角空格一样视作子句分隔：版心够宽时两句仍并排居中，收窄时优先在换行处折断，而不会把两句粘成一串。下例取自《诗经·周南·葛覃》，首字「葛󠄀」附带了表意文字异体选择符（IVS，`U+E0100`），选择符应随基字留在同一格内，不会单独占出一个空格子：

葛󠄀之覃兮\
施于中谷
{.mizige}

米字格段落也可以嵌在`{.keep-space}`引用块里：引用块中的诗句保留手敲的停顿空格，其中的字帖照常拆格（两者先后从页面中切出、再按相反顺序放回）：

> 明月 几时有
>
> [把酒问青天]{bǎ jiǔ wèn qīng tiān}
> {.mizige}
{.keep-space}

## 列表左对齐、窄栏容器与等宽代码块 {#lists-and-blocks}

正文段落使用两端对齐，但列表、引用块等窄栏或短行容器刻意固定为左对齐（`text-align: start`），桌面端项目符号与两位数编号采用等宽数字（`tabular-nums`）悬挂在版心左侧栏外，文字左缘与上下正文严格平齐：

1. 短列表项自然收尾，右侧参差本就是列表的阅读节奏。
2. 技术列表常密集出现十余字符的驼峰开关与属性名（无分隔符可插断点，或未达16字符软断行阈值），例如`--printI18nWarnings`、`font-synthesis-style`、`text-spacing-trim`与`overflow-wrap: break-word`；左对齐让这些词条平稳落入第二行，而不会把第一行的汉字间距强行拉开。
3. 嵌套列表向内缩进，行宽进一步收窄：
   - 子项中的`code_vars_inline`、`hanging-punctuation`与`line-break: strict`同样保持自然字距；
   - 中英文混排短句（如在macOS与Linux下对比Noto Sans SC和PingFang SC的渲染）不会产生字距抖动。
4. 第4项用于填充有序列表编号序列。
5. 第5项继续延伸，准备检验个位数到两位数的悬挂对齐。
6. 第6项。
7. 第7项。
8. 第8项。
9. 第9项：注意下一条编号`10.`的小数点位置是否与`9.`严格纵向对齐。
10. 两位数编号项：依靠`font-variant-numeric: tabular-nums`与左侧悬挂区，十位数字向左延伸而正文左缘丝毫不偏。

> 引用块字号略收至`0.95em`并内缩边距，单行字数少于正文版心，因此同样保持左对齐（`text-align: start`）。在这里一并检查「连续标点挤压（如『引号嵌套』与括号）。」以及中英文混排（如POSIX.1-2024标准与`arc4random_uniform(3)`接口）在浅灰暖底`--ground`上的阅读质感。

独立代码块（`<pre>`）必须彻底关闭从正文继承来的`text-autospace`、`text-spacing-trim`与OpenType `chws`标点挤压，确保全角字符与等宽ASCII表格在代码块内维持严格的字格对齐：

```c {.nowrap}
/*
 * 检验代码块内不触发正文的 chws 标点挤压与中西文自动留白：
 *
 *   字段名           示例值                   说明（「全角引号」与（括号）保持完整字宽）
 *   --------------  ----------------------  ----------------------------------------
 *   zone            "sjc.example.net"       目标域名（含 2026 年 SOA 序列号）
 *   key_algorithm   "hmac-sha256"           TSIG 算法：「推荐」（默认启用）
 */
static const char *default_zone = "sjc.example.net";
```

## 行内公式与句读禁则 {#inline-math}

数学公式与中文句读混排时，公式包裹在原子行内盒（`.math-inline`）中并在末尾附带字连接符（`U+2060`），防止紧随其后的全角逗号、句号、顿号或右括号在折行时孤零零掉到下一行行首。拖动窗口宽度检验下列公式与标点的粘合度：设倒排索引第一层词项集合为\(P_{T_1}(w)\)、第二层正文词项集合为\(P_{T_2}(w)\)，构建脚本保证两层严格不相交（即\(P_{T_1}(w) \cap P_{T_2}(w) = \emptyset\)），检索合并复杂度保持在\(O(|P_{T_1}| + |P_{T_2}|)\)，单次查询耗时通常低于\(1\,\text{ms}\)。当逻辑斯谛映射参数落入\(3.56995 < r \le 4\)区间时，微小初值扰动\(\delta_0 = 10^{-12}\)会按指数率\(\lvert\delta_n\rvert \approx \lvert\delta_0\rvert e^{\lambda n}\)迅速放大（其中Lyapunov指数\(\lambda > 0\)）：此时即便双精度浮点数的机器精度达到\(\varepsilon = 2^{-53}\)，迭代数十步后轨迹也会彻底分道扬镳。

## 英文换行句末空格恢复与标识符豁免 {#sentence-space}

Goldmark 1.8的`css3draft`断行规则会把任意Unicode标点（而非仅全角标点）旁的软换行当成无空格边界吞掉，导致英文段落折行处若恰好落在句号之后，渲染后会发生前后两句粘连。下面摘录《独立宣言》段落，刻意将句子断点放在小写词末尾（`accustomed.\nBut`）与首字母大写的3字母以上词末尾（`Government.\nThe`），检验`typeset-content.html`是否能准确补回句间空格：

> We hold these truths to be self-evident, that all men are created equal, that
> they are endowed by their Creator with certain unalienable Rights, that among
> these are Life, Liberty and the pursuit of Happiness. That to secure these
> rights, Governments are instituted among Men, deriving their just powers from
> the consent of the governed.
>
> Prudence, indeed, will dictate that Governments long established should not be
> changed for light and transient causes; and accordingly all experience hath
> shewn, that mankind are more disposed to suffer, while evils are sufferable,
> than to right themselves by abolishing the forms to which they are accustomed.
> But when a long train of abuses and usurpations, pursuing invariably the same
> Object evinces a design to reduce them under absolute Despotism, it is their
> right, it is their duty, to throw off such Government, and to provide new
> Guards for their future security. Such has been the patient sufferance of
> these Colonies; and such is now the necessity which constrains them to alter
> their former Systems of Government.
> The history of the present King of Great Britain is a history of repeated
> injuries and usurpations, all having in direct object the establishment of an
> absolute Tyranny over these States.

同一`css3draft`缺陷还会在下一行以ASCII标点（`**`、`[`、`` ` ``、`"`、`'`）开头时吞掉软换行。下面段落刻意在这些定界符前折行，检验渲染后是否均保留了词间空格：

> When a wrapped line opens with
> **strong emphasis**, a
> [Markdown link](https://example.org/),
> "double quotes", or
> 'single quotes', or when inline code opens with a symbol such as
> `--flag` or
> `/etc/rc.conf`, or follows an ASCII arrow like `TIME_OK` ->
> `TIME_INS`, the space ahead of each token must remain intact.

与此同时，正则必须放过域名、方法调用、人名与字段属性：正文里的 www.FreeBSD.org、Worm.Gibe.F、this.Think()、Dr.Web、Zoom.Quiet、User.Id 与 Order.Is 必须保持紧凑无空格；而带有`{.keep-space}`的区块则完整保留作者手写的节奏空格：

> 白日依山尽 黄河入海流  
> 欲穷千里目 更上一层楼
{.keep-space}
