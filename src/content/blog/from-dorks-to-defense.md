---
title: "From Dorks to Defense: How I Secured Two CERT-In Hall of Fames"
description: "From Dorks to Defense: How I Secured Two CERT-In Hall of Fames"
date: 2025-11-25
tags: ["bug-bounty", "CERT-IN", "recon"]
readTime: "5 min read"
pinned: true
---

![](/images/blog/from-dorks-to-defense/1_FET9FfzNnFiAum2nLDPMJA.jpeg)

### Introduction:

Getting recognized by CERT-In (Indian Computer Emergency Response Team) is a milestone for many bug bounty hunters and security researchers in India.

I recently achieved this milestone **twice**.

What’s funny is that it didn’t require zero-days or deep exploit development. It all began with the simplest tool in a researcher’s kit: **a search engine**.

**Phase 1: The Reconnaissance (Google Dorking on Steroids)**

Every good hunt starts with reconnaissance. When you’re looking at a huge scope like `*.gov.in`, brute-forcing or mass scanning is the worst approach. You need a clear attack surface first.

Hence, I used Google dorking, the art of using advanced search operators to find information that isn’t readily visible to the average user.

![](/images/blog/from-dorks-to-defense/0_ESd0A9iQE-bqBmcM.gif)

I crafted a specific list of dorks aimed at uncovering sensitive files, configuration errors, and admin panels within the government domain.

**Broad Scope & Infrastructure:**

```
site:*gov.insite:*gov.in/robots.txtsite:*gov.in/sitemap.xmlsite:*gov.in/*.js
```

**Juicy File Extensions (Information Disclosure):**

```
site:*gov.in filetype:pdfsite:*gov.in filetype:xlsx OR filetype:xlssite:*gov.in (filetype:zip OR filetype:tar OR filetype:gz OR filetype:sql)
```

> **Pro Tip:** Keeping track of these dorks can be tedious. I keep all my best dorks and checklists organized over at [**recon.vulninsights.codes**](https://recon.vulninsights.codes/). Feel free to use it to build your own bug bounty checklist.

* * *

**Phase 2: Striking Gold**

After running through these dorks, I started sifting through the results. It involves a lot of scrolling past irrelevant data, but eventually, something catches your eye.

I was looking for URLs with parameters , those little `?id=123` bits at the end of a link. Parameters are often where user input meets the backend database, making them prime targets for injection attacks.

Two sites caught my eye:

```
https://[redacted].gov.in/testimonial.php?lang=2&lid=2464https://[redacted].gov.in/search.php?page=14&fromdate=26-04-2024&todate=27-04-2024&state_name=35%20OR%201=1%20&circle=&division=&range=&block=&beat=&source=
```

![](/images/blog/from-dorks-to-defense/0_-55DUeeo85zZX55S.gif)

Multiple parameters in a government site? Yes, that’s basically a “please test me” invitation.

**Phase 3: The Exploitation**

I started with the basics: checking for client-side issues. And boom, reflected XSS popped up almost instantly.

But then it got more interesting.

While poking the _lang_ and _state\_name_ parameter, the responses began acting weird. Errors changed. Pages broke.

A few crafted payloads later, it was confirmed:

**_The endpoint was vulnerable to SQL Injection._**

### CERT-In Hall of fame:

My reports were validated, patched, and acknowledged.

**September 2025:**

![](/images/blog/from-dorks-to-defense/1_3vdr2a9sNeUeRmFGYdS9bw.jpeg)

**October 2025:**

![](/images/blog/from-dorks-to-defense/1_oT6i9Y-R4OfGCkdW_3e4Sw.jpeg)

**Some of findings:**

![](/images/blog/from-dorks-to-defense/0_GWjt6PwnSHNGIJUk.gif)

**2 SQL Injection:**

![](/images/blog/from-dorks-to-defense/1_p0iY_bLGcryt7loqJ2s12Q.png)

![](/images/blog/from-dorks-to-defense/1_5d4F_vbMcVmiJidEqPK91Q.jpeg)

**Several PHPInfo (Information disclosure):**

![](/images/blog/from-dorks-to-defense/1_GbClUe79xPv9M3own-G4jQ.png)

![](/images/blog/from-dorks-to-defense/1_CwwUwpGMYV0yHRDyBAVjvQ.png)

* * *

### Final Thoughts

![](/images/blog/from-dorks-to-defense/1_XW_R9WWXDpwzbEZCRBikdw.png)

This journey was never about exploiting anything. It was about safeguarding systems people rely on every day.

If you’re just starting out:

-   Build a strong recon workflow.
-   Learn to use Google dorks properly.
-   Pay attention to weird behavior.

Your next discovery might be much bigger than you think.

* * *

### About Me

**Het Patel** - VAPT Intern | CRTA | Cybersecurity Researcher | Bug Hunter | Top 2% THM | Coffee Addict ☕

![](/images/blog/from-dorks-to-defense/1_EsnzyEdgvPnrvyq6Jl_mDA.jpeg)

> Me and Shah Kaif are building our platform to display our personal Medium blogs and a lot more to come, on our own platform — **VulnInsights**

> [https://www.vulninsights.codes/](https://www.vulninsights.codes/)

> Connect with us:  
> Linkedln: \[‘[https://www.linkedin.com/in/hetpatel9/](https://www.linkedin.com/in/hetpatel9/)’, ‘[https://www.linkedin.com/in/skaif009](https://www.linkedin.com/in/skaif009)’\]