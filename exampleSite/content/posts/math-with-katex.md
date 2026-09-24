---
title: "用 KaTeX 书写数学公式"
date: 2026-07-18
description: "演示 Chaos 主题内置的 KaTeX 数学公式支持：行内公式与块级公式。"
categories: ["写作"]
tags: ["KaTeX", "数学", "Markdown"]
series: "Chaos 主题指南"
---

Chaos 内置了 KaTeX，公式在构建时由 Hugo 渲染为 HTML，读者的浏览器无需再执行任何脚本。

<!--more-->

## 行内公式

质能方程 \(E = mc^2\) 大概是最有名的公式；而欧拉恒等式 \(e^{i\pi} + 1 = 0\)
则常被称为最美的公式。

## 块级公式

高斯积分：

$$
\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}
$$

洛伦兹系统——「混沌」一词在数学上的经典范例：

$$
\begin{aligned}
\frac{dx}{dt} &= \sigma (y - x) \\[6pt]
\frac{dy}{dt} &= x (\rho - z) - y \\[6pt]
\frac{dz}{dt} &= xy - \beta z
\end{aligned}
$$

当 \(\sigma = 10\)、\(\rho = 28\)、\(\beta = 8/3\) 时，系统的轨迹呈现出著名的蝴蝶形吸引子。

> [!NOTE]
> 需要在站点配置中启用 Goldmark 的 passthrough 扩展，详见主题 README。
