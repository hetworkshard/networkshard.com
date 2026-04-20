---
title: "Why IDORs Are Everywhere — And How to Find Them — Part I"
description: "Why IDORs Are Everywhere — And How to Find Them — Part I"
date: 2025-06-15
tags: ["idor", "web-security", "bug-bounty"]
readTime: "5 min read"
---

## **“Why IDORs Are Everywhere — And How to Find Them” — Part I**

![](/images/blog/why-idors-are-everywhere/1_46Qd3SNa4tKkcA5ORbSUJQ.png)

_This write-up has been prepared under the guidance of_ [_Amish Patel_](https://medium.com/@cyberexpertamish)_,_ [_Lay Patel_](https://medium.com/@cynex) _at_ [_Hacker4Help_](https://medium.com/@hacker4help) _as part of our learning initiative on cybersecurity awareness._

Insecure Direct Object Reference (IDOR) is a common yet critical vulnerability in web applications that has consistently remained in the **OWASP Top 10** for over a decade. Often overlooked during development, it allows attackers to access unauthorized resources simply by manipulating input parameters. Despite its apparent simplicity, IDOR has led to major data breaches affecting millions of users, making it one of the most exploited vulnerabilities in modern web applications.

The beauty (and danger) of IDOR lies in its simplicity — no complex exploit chains, no advanced tools required. Just basic parameter manipulation that any curious user could stumble upon.

![](/images/blog/why-idors-are-everywhere/1_pOShe-Y9KU8UoQ8xt60WYA.gif)

## What is IDOR?

IDOR occurs when an application exposes internal object references (like database keys, file names, or user IDs) in a way that allows attackers to manipulate them and gain unauthorized access to resources they shouldn’t be able to view or modify.

**Simple Example:**

```
Normal request: https://banking-app.com/account/12345Malicious request: https://banking-app.com/account/12346
```

If the application doesn’t verify that the logged-in user owns account `12346`, the attacker gains access to someone else's banking information.

![](/images/blog/why-idors-are-everywhere/1_AFWKVkO4kf3f0ClM_0SNOA.gif)

## Types of IDOR Vulnerabilities

**1\. Horizontal IDOR** — Access data at the same privilege level

-   User A accessing User B’s profile
-   Customer viewing another customer’s orders

**2\. Vertical IDOR** — Privilege escalation to higher access levels

-   Regular user accessing admin functionalities
-   Customer accessing employee-only resources

**3\. Blind IDOR** — No direct data exposure but actions can be performed

-   Deleting other users’ files without seeing them
-   Modifying records without viewing the content

## My Real-World Finding: Exposing Invoices via IDOR

![](/images/blog/why-idors-are-everywhere/0_jBnQxyUv6c20fb6i.gif)

### The Discovery Process

While conducting a security assessment on a beta e-commerce platform, I discovered a critical IDOR vulnerability that exposed thousands of customer invoices. Here’s how it unfolded:

**Initial Observation:** After making a purchase and navigating to my account dashboard, I noticed the invoice URL:

```
https://redacted-shop.in/myaccount/invoice/print/16?type=print
```

The sequential number `16` immediately caught my attention. In my experience, predictable identifiers are often vulnerable to IDOR attacks.

![](/images/blog/why-idors-are-everywhere/1_QiG3-3uCdmdeR9J5xOAHNw.png)

_Address and Mobile number — both are dummy — lol._

Once i clicked on Invoice:

![](/images/blog/why-idors-are-everywhere/1_6pz8TufSLIgbyl6L2znOtw.png)

**Testing Methodology:**

1.  **Baseline Test**: Confirmed I could access my own invoice.
2.  **Parameter Manipulation**: Changed the ID to `17`, `18`, `19`, etc.
3.  **Access Verification**: Successfully accessed other users’ invoices
4.  **Impact Assessment**: Tested both directions (lower and higher IDs

**What I Found:**

-   **Complete invoice access** for other customers
-   **Personal information exposure**: Names, addresses, phone numbers
-   **Purchase history**: Products bought, quantities, prices
-   **Payment details**: Last 4 digits of credit cards, payment methods
-   **Order patterns**: Shipping preferences, delivery addresses

All I needed was to be logged into **my own account**. If not logged in, the endpoint

**What This Means** 🧪**:** The server was exposing internal object references (invoice IDs) without verifying if the current user had permission to view them. Anyone with a valid session could access other users’ sensitive data just by manipulating the URL.

**Security Issue** 🔐**:** This is a textbook example of IDOR. The application should have enforced access controls to ensure that only the **logged-in user** could access their own invoices.

**Impact** 🎯**:**

-   Unauthorized access to user data
-   Potential privacy violations
-   Risk of legal and regulatory non-compliance

## How IDOR Happens

-   Lack of access control checks
-   Exposing predictable object IDs
-   Poor session management

## Impact of IDOR Vulnerabilities

-   Data leakage
-   Account takeover
-   Unauthorized actions (modifying or deleting records)
-   Full privilege escalation

## Final Thoughts

IDOR is a prime example of how simple mistakes can lead to serious consequences. It reinforces the importance of secure coding practices, regular testing, and awareness among developers and testers alike.

So next time you see a URL with a numeric ID, test it — you might just stumble upon your next big find.