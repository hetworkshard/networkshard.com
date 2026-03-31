---
title: "Mastering Nmap: The Ultimate Guide to Port Scanning"
description: "Mastering Nmap: The Ultimate Guide to Port Scanning"
date: 2025-06-23
tags: ["nmap", "recon", "tools"]
readTime: "8 min read"
---

_This write-up has been prepared under the guidance of_ [_Amish Patel_](https://medium.com/@cyberexpertamish)_,_ [_Lay Patel_](https://medium.com/@cynex) _at_ [_Hacker4Help_](https://medium.com/@hacker4help) _as part of our learning initiative on cybersecurity awareness._

![](https://cdn-images-1.medium.com/max/800/0*ArZ_MYtOn9xGhS0L)

* * *

### Introduction

> _“When it comes to hacking, knowledge is power.”_

Before any exploitation attempt, proper **enumeration** is vital. The more information you gather about a target, the more precise and successful your actions will be. One of the first steps in this process is **port scanning** — a way to understand what services a machine is running and where.

Imagine you’re handed a set of IP addresses and asked to perform a **security audit**. The first task is to map the digital landscape: Is it running a webserver? Is there an Active Directory controller? All these answers begin with scanning **ports** — the doorways to network services.

* * *

### What Are Ports? 🌐

Ports are essential for distinguishing services on a computer. They act like communication endpoints. For example:

-   **HTTP (Web)**: Port 80
-   **HTTPS (Secure Web)**: Port 443
-   **SMB/NetBIOS**: Ports 139 and 445

There are **65,535 ports** per device, but many services use standardized ones. In CTFs or hardened environments, services may be hosted on non-standard ports. That’s why port scanning is critical.

* * *

### Why Use Nmap? 🔍

![](https://cdn-images-1.medium.com/max/800/0*cVYt14UIUwe8IDqU.gif)

**Nmap (Network Mapper)** is the industry standard for network discovery and auditing. Why it’s a go-to:

-   Scans open, closed, or filtered ports
-   Detects service versions and OS
-   Integrates a powerful scripting engine (NSE)
-   Great for ethical hacking, audits, and CTFs

```
nmap -h       # Help menu  man nmap      # Manual page
```

* * *

### Core Scan Types

### 1\. TCP Connect Scan (-sT)

Performs a full **three-way handshake** with the target:

1.  SYN →
2.  SYN/ACK ←
3.  ACK → (connection established)

-   **Open** port: SYN/ACK → ACK
-   **Closed** port: RST
-   **Filtered** port: No response

Best for environments where root privileges are not available.

![](https://cdn-images-1.medium.com/max/800/0*6V_IOJuKGS7kGxet.gif)

### 2\. SYN Scan (-sS)

Also known as a **half-open** or **stealth** scan:

1.  SYN →
2.  SYN/ACK ←
3.  RST → (terminate before completing handshake)

Advantages:

-   Stealthier (bypasses basic IDS).
-   Not logged by many services.
-   Faster than -sT.

Disadvantages:

-   Requires root/sudo access.
-   Might crash unstable services.

![](https://cdn-images-1.medium.com/max/800/0*mLiWN1dCapio4i5H.gif)

### 3\. UDP Scan (-sU)

UDP is stateless and scanning is tricky:

-   **No response** → Open|Filtered
-   **ICMP Port Unreachable** → Closed
-   **Valid UDP response** → Open

Slow but useful. Mitigate with:

```
nmap -sU --top-ports 20 <target>
```

![](https://cdn-images-1.medium.com/max/800/0*NhLt1x4DJHcmYWof.gif)

* * *

### Advanced & Stealth Scans

### TCP Null Scan (-sN)

-   Sends a packet with **no flags**
-   Closed port → RST
-   Open|Filtered → No response

### TCP FIN Scan (-sF)

-   Sends a packet with the **FIN** flag
-   Closed port → RST

### TCP Xmas Scan (-sX)

-   Flags: FIN, PSH, URG (like a blinking Christmas tree 🎄)
-   Closed port → RST

These scans are stealthier and useful against **firewalls** blocking SYN packets. However, they are less reliable on Windows hosts.

* * *

### Discovering Live Hosts

![](https://cdn-images-1.medium.com/max/800/0*Yc6iGJv-HpKMEi1C.gif)

On first connection to a target network in a black box assignment, we need to identify active hosts. This is done using a **ping sweep** with the `-sn` flag:

```
nmap -sn 192.168.0.1-254nmap -sn 192.168.0.0/24
```

-   `-sn`: disables port scanning, uses ICMP, TCP SYN to port 443, and TCP ACK/SYN to port 80.
-   Requires `sudo` for ARP requests on local networks.

* * *

### Bypassing Firewalls

![](https://cdn-images-1.medium.com/max/800/0*cvksTnE8dbENhvCU.gif)

Some hosts may block ICMP packets, causing them to appear offline. Use `-Pn` to treat all hosts as alive:

```
nmap -Pn <target>
```

Other evasion options:

-   `-f`: Fragment packets
-   `--mtu <num>`: Set custom MTU (must be multiple of 8)
-   `--scan-delay <time>ms`: Adds delay between packets
-   `--badsum`: Send packets with bad checksums

* * *

### Nmap Scripting Engine (NSE)

NSE scripts extend Nmap’s capabilities significantly. Scripts are written in Lua and categorized by type:

-   `safe`: Harmless, passive scans
-   `intrusive`: Might affect the target
-   `vuln`: Check for vulnerabilities
-   `exploit`: Try to exploit vulnerabilities
-   `auth`: Test authentication methods
-   `brute`: Perform bruteforce attacks
-   `discovery`: Gather more network information

### Using Scripts

Run all scripts from a category:

```
nmap --script=vuln <target>
```

Run specific scripts:

```
nmap --script=http-fileupload-exploiter <target>nmap --script=smb-enum-users,smb-enum-shares <target>
```

Scripts with arguments:

```
nmap -p 80 --script http-put \  --script-args http-put.url='/dav/shell.php',http-put.file='./shell.php'
```

Help for any script:

```
nmap --script-help <script-name>
```

### Finding Scripts

![](https://cdn-images-1.medium.com/max/800/0*btwJoawApYDvFVHI.gif)

-   Online: [Nmap Script Index](https://nmap.org/nsedoc/)
-   Locally: `/usr/share/nmap/scripts`
-   Search with:

```
grep "ftp" /usr/share/nmap/scripts/script.dbls -l /usr/share/nmap/scripts/*ftp*
```

Install missing scripts manually:

```
sudo wget -O /usr/share/nmap/scripts/<script>.nse \  https://svn.nmap.org/nmap/scripts/<script>.nsenmap --script-updatedb
```

* * *

![](https://cdn-images-1.medium.com/max/800/1*760LZh2IHCNGgFM9ZDIexQ.png)

* * *

### Final Thoughts

Port scanning is the **foundation of enumeration**. Without it, you’re blindly poking at a system. Whether it’s a stealthy SYN scan, a protocol-specific UDP ping, or a targeted NSE script, **Nmap arms you with the visibility** needed to act smartly and ethically.

> _“A hacker without enumeration is like a sniper shooting blindfolded.”_

* * *

### Pro Tip 💡

Use `-oA scan_results` to save results in all formats (normal, XML, grepable):

```
nmap -sS -sV -A -T4 -oA scan_results <target>
```

* * *

### Recommended Lab

Further Nmap: [https://tryhackme.com/room/furthernmap](https://tryhackme.com/room/furthernmap)

Nmap Live Host Discovery: [https://tryhackme.com/room/nmap01](https://tryhackme.com/room/nmap01)

* * *

### About Me 👤

![](https://cdn-images-1.medium.com/max/800/0*SRqMpy-WEMp8pFJD.gif)

Hi! I’m **Het Patel**, a passionate cybersecurity enthusiast and a B.Tech student majoring in IT at Birla Vishvakarma Mahavidyalaya (BVM), Anand.

Follow my journey and insights:

-   Medium : [hettt.medium.com](http://hettt.medium.com)
-   TryHackMe: [https://tryhackme.com/p/hett.patell](https://tryhackme.com/p/hett.patell)
-   GitHub: [https://github.com/patelhettt](https://github.com/patelhettt)

Let’s explore the digital frontier together! 🚀