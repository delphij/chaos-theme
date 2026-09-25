---
title: "用 KaTeX 书写数学公式"
date: 2026-07-18
description: "介绍 Chaos 主题对 KaTeX 数学公式的支持：行内公式、块级方程式与站点解析配置。"
categories: ["指南"]
tags: ["Chaos", "KaTeX", "数学", "Markdown"]
series: "Chaos 主题指南"
---

Chaos集成了[KaTeX](https://katex.org/)数学排版引擎，
数学公式直接在站点构建期渲染为静态HTML与MathML，读者端无需执行额外脚本。

<!--more-->

## 站点配置

若需在Markdown正文中直接书写LaTeX公式，
需在站点的 `hugo.toml` 中启用[Goldmark](https://github.com/yuin/goldmark)的passthrough扩展：

```toml
[markup.goldmark.extensions.passthrough]
  enable = true
  [markup.goldmark.extensions.passthrough.delimiters]
    block = [['$$', '$$']]
    inline = [['\(', '\)']]
```

## 行内公式

在正文中使用 `\(` 和 `\)` 包裹[LaTeX](https://zh.wikipedia.org/wiki/LaTeX)数学表达式。

```markdown
[质能方程](https://zh.wikipedia.org/wiki/%E8%B4%A8%E8%83%BD%E7%AD%89%E4%BB%B7) \(E = mc^2\) 是现代物理学的基石；而[欧拉恒等式](https://zh.wikipedia.org/wiki/%E6%AC%A7%E6%8B%89%E6%81%92%E7%AD%89%E5%BC%8F) \(e^{i\pi} + 1 = 0\) 则融合了五个最重要的数学常数。
```

渲染效果：

[质能方程](https://zh.wikipedia.org/wiki/%E8%B4%A8%E8%83%BD%E7%AD%89%E4%BB%B7) \(E = mc^2\) 是现代物理学的基石；而[欧拉恒等式](https://zh.wikipedia.org/wiki/%E6%AC%A7%E6%8B%89%E6%81%92%E7%AD%89%E5%BC%8F) \(e^{i\pi} + 1 = 0\) 则融合了五个最重要的数学常数。

## 块级公式

对于独立成段的复杂方程式，使用双美元符号 `$$` 包裹：

````markdown
$$
\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}
$$
````

[高斯积分](https://zh.wikipedia.org/wiki/%E9%AB%98%E6%96%AF%E7%A7%AF%E5%88%86)渲染效果：

$$
\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}
$$

### 多行对齐公式

支持使用 `aligned` 环境排版多行对齐的微分方程组（例如[洛伦兹吸引子](https://zh.wikipedia.org/wiki/%E6%B4%9B%E4%BC%A6%E8%8C%A8%E5%90%B8%E5%BC%95%E5%AD%90)）：

````markdown
$$
\begin{aligned}
\frac{dx}{dt} &= \sigma (y - x) \\[6pt]
\frac{dy}{dt} &= x (\rho - z) - y \\[6pt]
\frac{dz}{dt} &= xy - \beta z
\end{aligned}
$$
````

渲染效果：

$$
\begin{aligned}
\frac{dx}{dt} &= \sigma (y - x) \\[6pt]
\frac{dy}{dt} &= x (\rho - z) - y \\[6pt]
\frac{dz}{dt} &= xy - \beta z
\end{aligned}
$$

当 \(\sigma = 10\)、\(\rho = 28\)、\(\beta = 8/3\) 时，系统将在[相空间](https://zh.wikipedia.org/wiki/%E7%9B%B8%E7%A9%BA%E9%97%B4)中形成经典的蝴蝶形混沌吸引子轨迹。


