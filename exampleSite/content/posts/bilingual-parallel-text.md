---
title: "双语对照：两栏平行文本排版示例"
date: 2026-11-16
description: "介绍Chaos主题如何使用Markdown定义列表与{.bilingual}（及.even、.wide-ref修饰类）排印双语对照文章，并兼顾单栏选区复制与窄屏体验。"
categories: ["指南"]
tags: ["Chaos", "Markdown", "中文排版", "双语"]
series: "Chaos 主题指南"
---

翻译笔记、外文演讲摘录与诗词英译常见「两栏并排对照」的版式需求。Chaos延续`{.dialogue}`的设计思路，直接复用标准Markdown定义列表与`{.bilingual}`块属性实现左右对照：宽屏下按语言密度自动分配栏宽并逐段顶部对齐，手机端退化为「先中后外」堆叠，RSS/Atom订阅也能保持天然的可读结构。

<!--more-->

## 语法与设计 {#syntax}

在启用`[markup.goldmark.parser.attribute] block = true`的前提下，将主读语言（通常为简体中文）置于`<dt>`行，将外文对照置于`: <dd>`行，列表末尾附加`{.bilingual}`即可：

- **主左次右（默认`{.bilingual}`）**：中文信息密度高于英文，同等语意下英文篇幅往往是中文的1.3至1.6倍，因此采用`fit-content(44%) minmax(0, 1fr)`：长段散文按约`44% : 56%`分配栏宽，并将右栏外文微缩为`0.9em`、墨色设为`--muted`，使左右两段高度大致持平；遇到短句诗词时左栏则自动收缩到内容宽度，右栏紧随`column-gap`排出，不留大片空白。
- **单行`<dt>`约定**：Goldmark的定义列表会把` : `之前的多行分别解析为多个`<dt>`，因此左栏`<dt>`需保持单行；右栏`: <dd>`支持多行折行（续行缩进2空格）。
- **单栏连贯选区（`bilingual-select.js`）**：按DOM顺序直接拖选会把左右两栏交错选中。处于双栏网格状态时，鼠标从哪一栏起拖就只选那一栏（跨`<!--more-->`分段也可连续选中）；若要同时选中双语，从区块外起拖、按住`Alt`/`Option`或按`Ctrl`/`Cmd+A`即可。

## 散文对照示例（默认`{.bilingual}`） {#prose}

以下摘录《独立宣言》（1776年）开篇段落，演示默认`44% : 56%`与右栏微缩排版下的多段对齐效果：

在人类历史事件的进程中，当一个民族有必要解除其与另一个民族之间的政治纽带，并在世界列国之中取得自然法则与自然之神所赋予她的独立而平等的地位时，出于对人类舆论的恰当尊重，她应当把促使其独立的缘由昭告天下。
: When in the Course of human events, it becomes necessary for one people to
  dissolve the political bands which have connected them with another, and to
  assume among the powers of the earth, the separate and equal station to which
  the Laws of Nature and of Nature's God entitle them, a decent respect to the
  opinions of mankind requires that they should declare the causes which impel
  them to the separation.

我们认为下面这些真理是不言而喻的：人人生而平等，造物者赋予他们若干不可剥夺的权利，其中包括生命权、自由权和追求幸福的权利。为了保障这些权利，人类才在他们之间建立政府，而政府之正当权力，是经被治理者的同意而产生的。当任何形式的政府对这些目标具破坏作用时，人民便有权力改变或废除它，以建立一个新的政府；其赖以奠基的原则，其组织权力的方式，务使人民认为唯有这样才最可能获得他们的安全与幸福。
: We hold these truths to be self-evident, that all men are created equal, that
  they are endowed by their Creator with certain unalienable Rights, that among
  these are Life, Liberty and the pursuit of Happiness. — That to secure these
  rights, Governments are instituted among Men, deriving their just powers from
  the consent of the governed, — That whenever any Form of Government becomes
  destructive of these ends, it is the Right of the People to alter or to
  abolish it, and to institute new Government, laying its foundation on such
  principles and organizing its powers in such form, as to them shall seem most
  likely to effect their Safety and Happiness.
{.bilingual}

## 等宽诗歌示例（`{.bilingual .even}`） {#even}

对于诗歌、歌词或短句格言，附加`.even`可将左栏上限放宽至`50%`（长段`50% : 50%`等宽，短诗仍贴合左栏内容宽度），并使右栏使用与正文相同的字号与墨色。配合`{.keep-space}`与行尾双空格硬换行，还能在中文格律句中保留停顿空格（下例引用《诗经·关雎》与James Legge英译本）：

关关雎鸠  在河之洲
: Guan-guan go the ospreys,  
  On the islet in the river.

窈窕淑女  君子好逑
: The modest, retiring, virtuous, young lady:  
  For our prince a good mate she.
{.bilingual .even .keep-space}

## 简注配长文示例（`{.bilingual .wide-ref}`） {#wide-ref}

若左栏只是精炼的条款提要或译注，而右栏需要展示较长的原始条文或文献，可附加`.wide-ref`将左栏上限收窄至`38%`（长段约`38% : 62%`）：

条文编号与核心原则：若列表本身使用编号，可用`1\. `转义以免Goldmark拆出有序列表。
: 1\. Prudence, indeed, will dictate that Governments long established should not
  be changed for light and transient causes; and accordingly all experience hath
  shewn, that mankind are more disposed to suffer, while evils are sufferable,
  than to right themselves by abolishing the forms to which they are accustomed.

当长久以来的滥权与篡夺指向绝对专制时，推翻旧制与设立新保障既是权利，也是义务。
: 2\. But when a long train of abuses and usurpations, pursuing invariably the
  same Object evinces a design to reduce them under absolute Despotism, it is
  their right, it is their duty, to throw off such Government, and to provide
  new Guards for their future security.
{.bilingual .wide-ref}
