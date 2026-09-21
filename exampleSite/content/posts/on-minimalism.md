+++
title = '少即是多：一个博客需要多少 JavaScript'
date = '2024-10-15'
description = '关于个人博客的性能预算，以及为什么 3KB 的脚本已经足够。'
categories = ['随笔']
tags = ['性能', 'Web', 'Chaos']
+++

一个以文字为主的博客，真正需要脚本的地方屈指可数：切换深浅色模式、移动端的菜单、
目录的滚动高亮。其余的事情，HTML 和 CSS 早就可以独立完成了。

<!--more-->

Chaos 给自己定下的预算是：全部 JavaScript 压缩后约 3KB，不引入任何框架，
不依赖任何外部 CDN。数学公式在构建时渲染，图片由 Hugo 生成响应式的 WebP，
页面之间的跳转交给浏览器原生的 Speculation Rules 与 View Transitions。

省下来的每一个字节，最终都会变成读者那边更快出现的第一行字。
