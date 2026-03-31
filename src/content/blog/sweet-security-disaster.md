---
title: "Sweet Security Disaster: How I Could Verify Any Account on a Dessert Website 🍦"
description: "Sweet Security Disaster: How I Could Verify Any Account on a Dessert Website 🍦"
date: 2025-05-09
tags: ["bug-bounty", "account-takeover"]
readTime: "4 min read"
---

_This write-up has been prepared under the guidance of_ [_Amish Patel_](https://medium.com/@cyberexpertamish)_,_ [_Lay Patel_](https://medium.com/@cynex) _at_ [_Hacker4Help_](https://medium.com/@hacker4help) _as part of our learning initiative on cybersecurity awareness._

* * *

_Me, enjoying sweets while finding security holes…_

### The Setup: Just Browsing Some Desserts…

What started as casual browsing on a traditional sweets website turned into an unexpected security adventure. Recently, I was looking through a popular dessert website (which shall remain unnamed for security reasons) and decided to create an account just to explore their offerings. Like most of us, I was just satisfying my curiosity about their sweet selection, not looking for security vulnerabilities.

![](https://cdn-images-1.medium.com/max/1200/1*i_Kv29qtBl3NbD3GvzIG-Q.png)

### The Discovery: Wait, What’s This URL?

After filling out the standard sign-up form with my email and password, I received a verification email as expected. Nothing unusual so far.

![](https://cdn-images-1.medium.com/max/800/1*yUgDvcYkl6m8XjUxKyZFmw.png)

Used an Temp mail to create an account and received an email contained a friendly welcome message and a verification link that looked something like this:

![](https://cdn-images-1.medium.com/max/800/1*rDzSpa3p-zTw5QtneMnjBQ.png)

I have blurred the logo and removed the details as the bug is still not reported.

```
https://example-sweets.com//activeaccount.php?e=aGVzaXQ3MjM2N0BtYWdwaXQuY29t
```

![](https://cdn-images-1.medium.com/max/800/1*HyAWOI2ijMRnpuMZAiEhKg.gif)

Being naturally curious (or nosy, depending on who you ask), I noticed something interesting about that link. The parameter _e=aGVzaXQ3MjM2N0BtYWdwaXQuY29t_ caught my attention.

### The Experiment: Let’s Decode This…

That string after the `e=` parameter looked familiar. With my limited but enthusiastic knowledge of web security, I recognized it as Base64 encoding. So I decided to decode it:

```
aGVzaXQ3MjM2N0BtYWdwaXQuY29t → hesit72367@magpit.com
```

Well, well, well! That’s just my temp email address encoded in Base64. Now things were getting interesting.

![](https://cdn-images-1.medium.com/max/800/1*0jdXtb5fvq4LfYjr-p1S-Q.gif)

### The Vulnerability: Security More Flaky Than Their Sweets

Here’s where it gets concerning. If the verification system only checks for a Base64-encoded email in the URL, what’s stopping anyone from:

1.  Creating an account with ANY email address
2.  Intercepting the verification link
3.  Changing the Base64-encoded email to activate ANY account

This means I could potentially:

-   Create accounts for emails I don’t own
-   Take over accounts that haven’t been verified yet
-   Generally cause sweet, sweet chaos

### The Impact: Not Just About Sweets Anymore

While this might seem like a small issue on a dessert website, the implications can be serious:

-   Identity verification is completely bypassed
-   Users could impersonate others
-   Account security is compromised
-   Customer data could potentially be at risk

### Conclusion: Security Is Like a Good Recipe

This simple case demonstrates that security, like baking, requires attention to detail. A small mistake in the recipe can lead to the whole batch being compromised.

For developers, especially those handling user accounts, remember that Base64 is NOT encryption — it’s just encoding that anyone can easily reverse. Never use it for security purposes!

For users, this is a reminder that even the sweetest websites might have bitter security issues.

_Security should be baked in, not added as frosting_