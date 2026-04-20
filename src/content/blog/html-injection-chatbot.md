---
title: "How We Discovered a Stored HTML Injection in a Chatbot System 🕷️"
description: "How We Discovered a Stored HTML Injection in a Chatbot System 🕷️"
date: 2025-06-06
tags: ["html-injection", "chatbot", "web-security"]
readTime: "4 min read"
---

![](/images/blog/html-injection-chatbot/1_I5gZg5zHGbCAm6pFutc-og.png)

_This write-up has been prepared under the guidance of_ [_Amish Patel_](https://medium.com/@cyberexpertamish)_,_ [_Lay Patel_](https://medium.com/@cynex) _at_ [_Hacker4Help_](https://medium.com/@hacker4help) _as part of our learning initiative on cybersecurity awareness._

* * *

## 🔍 Introduction

As budding cybersecurity enthusiasts, we’re always on the lookout for vulnerable systems that can help us learn and sharpen our skills. One casual evening of testing led us — **Het Patel** and [**Kaif Shah**](https://medium.com/@SKaif009) — to discover a **Stored HTML Injection vulnerability** in the chatbot feature of redacted[.co.in](https://pyng.co.in), an AI-driven platform that connects users with verified professional experts across various categories.

![](/images/blog/html-injection-chatbot/1_O-VS6Px7tMZsiEi0ppwFPg.gif)

So Let’s get started **😎**

* * *

## What is Stored HTML Injection? 💥

Before we dive into the juicy details, let’s break down what **Stored HTML Injection** actually is (because not everyone speaks fluent hacker 🤓):

![](/images/blog/html-injection-chatbot/1_5ZxnGMhwcyDhQA1jg8MFWg.gif)

**Think of it like this:** Imagine you’re at a restaurant and the waiter takes your order without questioning it. You ask for “spaghetti with a side of _surprise ingredients_” and the kitchen just… makes it. No questions asked. That’s essentially what happens with stored HTML injection! 🍝

Hence, **Stored HTML Injection** occurs when user-supplied HTML content is not properly sanitized and is saved in the application’s database. When this data is later rendered on a page, the HTML is executed directly, which could lead to defacements or further security issues such as phishing or XSS (if scripts are allowed).

This can lead to:

-   🎭 Page defacements (making websites look funky)
-   🎣 Phishing attacks (tricking users)
-   ⚡ XSS vulnerabilities (if scripts sneak through)

* * *

## The Setup: Where We Found It 🧪

While exploring the **AI chatbot feature** of pyng.co.in, we noticed an input field where users could send messages. At first, it seemed harmless — but our curiosity nudged us to test how it handled raw HTML.

## Payload and Execution

We entered the following simple HTML tag as our message:

```
<h1>Hello from Het & Kaif</h1>
```

To our surprise, when the chat history was loaded on page refresh or revisit, the message was rendered exactly as HTML — **not escaped**, not sanitized.  
This confirmed a **stored HTML injection** — the HTML was being stored server-side and rendered client-side without any filtering.

We also tried several other payloads to confirm the injection:

```
<b style="color:red">XSS</b><i onclick="alert('XSS')">Click me</i><div style="background:red;padding:10px">Injected DIV</div><b style="color:red">XSS</b>
```

However, since JavaScript execution was fully disabled, despite attempting multiple payloads and bypass techniques, we were unable to achieve any successful execution.

* * *

## Screenshot of Payload Execution

![](/images/blog/html-injection-chatbot/1_hhnaAsei0pc_D0CEi2zBpg.png)

* * *

## 📬 Responsible Disclosure

We followed responsible disclosure practices:

-   Reported the bug to the redacted.co.in team.
-   Shared steps to reproduce and suggestions to mitigate.

* * *

We did got the reply from support team:

![](/images/blog/html-injection-chatbot/1__uzraE2NuE6Vl8XD_EwWog.png)

They were already aware of the vulnerability so they marked our report as “Duplicate Submission” 😭

* * *

## **About the Authors:**

![](/images/blog/html-injection-chatbot/1_NRR6i_VIh-HmfrQhX8yfFg.gif)

-   [**Het Patel**](https://www.linkedin.com/in/hetpatel9) — Cybersecurity Enthusiast | Bug Hunter | Coffee Addict ☕
-   [**Kaif Shah**](https://www.linkedin.com/in/skaif009/) — Security Researcher | CEHv11 | CRTA | Top 4% THM | Bug Hunter

_Happy Hacking! (Ethically, of course)_ 😉🔒