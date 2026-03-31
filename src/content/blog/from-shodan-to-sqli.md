---
title: "From Shodan to SQLi: Hacking an Exposed Company Dashboard"
description: "From Shodan to SQLi: Hacking an Exposed Company Dashboard"
date: 2025-08-28
tags: ["sql-injection", "shodan", "pentesting"]
readTime: "6 min read"
---

![](https://cdn-images-1.medium.com/max/800/1*6WU29m2SWDro9AcCZ-RUCw.png)

Uncovering vulnerabilities and exploiting them: a deep dive into the journey from reconnaissance to a successful SQL injection.

This is a real-world case study detailing how an exposed company dashboard was identified and exploited, starting from a simple search on Shodan. It serves as a powerful reminder of how critical security hygiene is from network configuration to secure coding practices.

📌 **Special thanks to** [**Shah kaif**](https://medium.com/u/10f677056bcd?source=post_page---user_mention--d82e6591a63a---------------------------------------) **—** my dedicated learning partner — for collaborating on this research and finding.

* * *

### The Reconnaissance Phase: Shodan’s Power

![](https://cdn-images-1.medium.com/max/800/0*3d7ozKMAO-vAzWUI.gif)

While exploring Shodan one evening, I came across an exposed server running an outdated version of Apache. What started as simple reconnaissance quickly escalated into a full SQL injection that let me bypass login and access a company’s internal dashboard.

This write-up highlights how **basic misconfigurations + outdated software + lack of input validation** can lead to severe compromises.

![](https://cdn-images-1.medium.com/max/800/1*LZ02PKRCZHqgRjI1dlmu5Q.png)

Where I saw this !!!

![](https://cdn-images-1.medium.com/max/800/1*Cl2IrfAiJoOR9jfZf-maWA.png)

* * *

### Discovering the Login Page

![](https://cdn-images-1.medium.com/max/800/1*VWcHFyy6JiBbMCnefzWX5w.png)

When I visited the IP, I noticed that directory listing was enabled, which exposed several data files.

![](https://cdn-images-1.medium.com/max/800/1*j5SQexw4h8RuJ4kqRYhvjw.png)

When I visited the IP, I noticed that directory listing was enabled, which exposed several data files. I visited almost every data folder, but they eventually redirected me to a login screen. I tried a few password combinations, which obviously failed.

![](https://cdn-images-1.medium.com/max/800/0*gHknThx6B8fZOVdG.gif)

* * *

### Testing for SQL Injection

The first step was simple: I entered a single quote (`'`) into the username field. The application responded with a SQL syntax error. Jackpot.

![](https://cdn-images-1.medium.com/max/800/1*AUm2rqX_fxkcEf8bpALKpA.png)

![](https://cdn-images-1.medium.com/max/800/0*Z26o7cVgzPs2KY9R.gif)

```
A Database Error OccurredError Number: 1064You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'admin' LIMIT 1' at line 3SELECT * FROM (`user_login_details`) WHERE `user_name` ='admin'' and user_password='admin' LIMIT 1Filename: C:\xampp\htdocs\DEMO\system\database\DB_driver.phpLine Number: 331
```

From there, I crafted a basic payload to extract more details. Error messages revealed database structure and confirmed the backend was vulnerable.

* * *

### Accessing the Dashboard

Well, Using a simple payload:

```
admin' AND 1=1#
```

Dashboard:

![](https://cdn-images-1.medium.com/max/1200/1*lwKIbkv_c5dRnE3HtLsBlw.png)

![](https://cdn-images-1.medium.com/max/800/0*UoabAfPECZkb6AJo.gif)

I was able to bypass authentication and gain direct access to the company’s internal dashboard.

The dashboard revealed whole internal system and at this point, I reported the issue to the company before digging any further. **Ethical hacking isn’t about exploiting data;** **it’s about securing it.**

* * *

### Conclusion

This story underscores the power of Shodan when combined with simple testing techniques like SQL injection. The best defense? Assume attackers are running these scans every day because they are.

For companies: never expose sensitive dashboards to the internet, always sanitize inputs, and ensure proper monitoring is in place.

For ethical hackers: sometimes all it takes is curiosity and persistence to uncover significant vulnerabilities.

* * *

### About Me

**Het Patel** — VAPT Intern | Cybersecurity Researcher | Bug Hunter | Top 3% THM | Coffee Addict ☕

> Me and Shah Kaif are building our platform to display our personal Medium blogs and a lot more to come, on our own platform — **VulnInsights**

> [https://www.vulninsights.codes/](https://www.vulninsights.codes/)