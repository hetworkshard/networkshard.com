---
title: "Business Logic: Broken. Wallet: Hacked. OTP: Bypassed."
description: "Business Logic: Broken. Wallet: Hacked. OTP: Bypassed."
date: 2025-07-19
tags: ["business-logic", "otp-bypass", "xss"]
readTime: "7 min read"
---

![](/images/blog/business-logic-broken/0_DAMc1WOXdab7ezbW.png)

📌 **Special thanks to** [**Shah kaif**](https://medium.com/u/10f677056bcd) **—** my dedicated learning partner — for collaborating on this research and finding.

![](/images/blog/business-logic-broken/0__FpircngVZdK8KMz.gif)

During a recent security assessment of **redacted.ai**, a virtual assistance platform that connects clients with remote talent including engineers, mentors, and co-founders, I uncovered several critical vulnerabilities that could compromise user accounts, financial data, and platform integrity.

> ⚠️ This post is for **educational purposes only**. I follow responsible disclosure. The name `redacted.ai` replaces the real domain for confidentiality.

* * *

## 🧠 What’s redacted.ai?

`redacted.ai` is an AI-based job-matching platform that:

-   Lets users sign up using email, Verify their account using Digilocker services for KYC,
-   Rewards actions with wallet coins,
-   Provided Virtual assistance and Job matching,
-   Helped with Mock interviews,

Also they were hiring for Remote Cybersecurity Specialist, and that was the main reason I had visited the site. Everything seemed to be perfect.

![](/images/blog/business-logic-broken/0_NwbSBhyPs6xseqbT.gif)

Simple idea. Good UX.  
 — But one weekend, I got curious and poked around.

Let’s just say… **things fell apart fast.**

* * *

## Vulnerabilities at a Glance

![](/images/blog/business-logic-broken/1_YhZwgmUnpdLlPNeJ2uuFMw.png)

* * *

## 1️⃣ OTP? Nah, Who Needs That!

![](/images/blog/business-logic-broken/0_8subjYEY-df33Brv.gif)

redacted.ai used **4-digit OTPs** for login and forgot-password flows — with **no rate limiting**, no CAPTCHA, and **no timeouts**.

I could easily bruteforce OTPs as they were only of 4 digits and Rate limits were not enforced.

### **Screenshot of The Attack:**

![](/images/blog/business-logic-broken/1_ISlZNs5U8yhWUcYqQ53hJA.png)

**This confirmed Pre-Account Takeover + Account Takeover of any user using forgot-otp feature.**

📉 **Impact**:

-   Any user account can be hijacked.
-   OTP system is meaningless.
-   Attacker doesn’t need the password, just the email address.

* * *

## 2️⃣ Business Logic Flaw — Wallet Be Like “Make It Rain 💸”

![](/images/blog/business-logic-broken/0_WI5l_f-2ztbS98FH.gif)

After creating a new account, I explored the “Wallet” feature. A popup appeared allowing me to request an amount — in **dollars** — despite my wallet balance being exactly **$0**. 🫠

![](/images/blog/business-logic-broken/1_X1WTxTOoDBUhR-gQQ3KS4Q.png)

I sent request of some dollars and naturally, I intercepted the request using **Burp Suite**. When I sent a payment request for some random amount, the response was:

![](/images/blog/business-logic-broken/1_-jCinslcxVfUcUe5HnmM3w.png)

```
{  "error':"Insufficient wallet balance for this request."}
```

Here, I changed the 400 Bad Request to 200 OK and removed the body of request and forwarded the request. To my surprise, The frontend accepted this and sent:

![](/images/blog/business-logic-broken/1__5KiJYxi6IGomC71-Xi8SA.png)

```
{  "userId':"6872b......",  "amount":1000000,  "type":"debited"}
```

Here, All I had to do is changed the “type” → “debited” to “credited”.

So, Here’s what I did,

```
{  "userId':"6872b......",  "amount":10000000000......,  "type":"credited"}
```

And this is what I got:

![](/images/blog/business-logic-broken/1_3xHhbSWjzCG7U4h__Ft6iw.png)

And the frontend:

![](/images/blog/business-logic-broken/1_NY0xBDOplm6UryRAO7dwFA.png)

### 💡 Why This Is Critical:

-   **No server-side validation** for wallet transactions.
-   **Trusting frontend logic** for financial operations is a **massive red flag**.
-   I was able to **manipulate the wallet balance** to any amount without any authentication or verification.

### 🛡️ Impact:

-   Unauthorized wallet crediting
-   Leads to potential purchase abuse, gift card fraud, or platform exploitation
-   Possible **financial loss** to the platform

* * *

## **3️⃣ Stored XSS in Resume Upload (PDF) and SVG Upload**

![](/images/blog/business-logic-broken/0_1aB4TW-qyCRlUQox.gif)

The platform allowed users to upload their **resumes as PDFs** and **profile pictures as SVGs** — both of which were vulnerable to **Stored Cross-Site Scripting (XSS)**.

### **PDF Upload: Stored XSS 🪓**

I crafted a malicious PDF file containing JavaScript payloads and uploaded it via the resume upload section. When any admin or HR opened this document **in-browser**, the JavaScript executed silently in their context.

This led to **persistent XSS**, as the PDF was stored and retrievable via a direct link — no sanitization or validation of file contents!

### **SVG Upload: Stored XSS Again!** 🧠

All I had to do is update :

```
filename="example2.jpg" --> "example2.svg"Content-Type: image/jpeg --> image/svg+xmlRemove the jpeg content and replace it by js script.
```

![](/images/blog/business-logic-broken/1_J-RfkqTIfbZVjgCw4kyaEw.png)

SVG images are actually **XML files** — and JavaScript can be embedded directly in them. I uploaded an SVG with the following payload:

```
<svg xmlns="http://www.w3.org/2000/svg">  <script>alert('Hello from SVG script');</script></svg>
```

**Boom!** ⚠️ Whenever someone visited the profile or page rendering this SVG, the script fired.

![](/images/blog/business-logic-broken/1_Op1wySX9A6LJ526vt5tzUQ.png)

* * *

## 5️⃣ Mobile Number Verification Bypass

![](/images/blog/business-logic-broken/0_gH7NS9HFoB2De_XL.gif)

While updating the profile, the platform sends an OTP to verify the mobile number. However, this mechanism was flawed due to **poor frontend-side validation and lack of backend enforcement**.

I entered invalid mobile number and requested for OTP.

![](/images/blog/business-logic-broken/1_nsKwQTnOBSCpAzGjznbOdw.png)

And also did provided false OTP. As expected the response was:

![](/images/blog/business-logic-broken/1_kL9iuOuwK-2WNXx130-Giw.png)

**SAME!!!** Again I tried changing bad request to → 200 OK and changed the body content to:

```
{  "success":true,  "error":"Invalid...."}
```

And this fired an another POST request at an /api/update-user-data:

![](/images/blog/business-logic-broken/1_pzllGmbVBjXo5OLoO7nx_A.png)

![](/images/blog/business-logic-broken/1_d2PqU5MjQMfPVS3k2VbvFA.png)

And that returned with:

![](/images/blog/business-logic-broken/1_R0In7t2awqNoIebmU9uRuA.png)

* * *

## About the Authors:

![](/images/blog/business-logic-broken/0_RucizFrRvuSfZDBr.gif)

-   [**Het Patel**](https://www.linkedin.com/in/hetpatel9) — VAPT Intern| Cybersecurity Researcher | Bug Hunter | Top 5% THM | Coffee Addict ☕
-   [**Kaif Shah**](https://www.linkedin.com/in/skaif009/) — Security Researcher | CEHv11 | CRTA | Top 4% THM | Bug Hunter

_Happy Hacking! (Ethically, of course)_ 😉🔒