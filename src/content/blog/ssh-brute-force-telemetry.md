---
title: "SSH Under Siege: 30 Days of Brute-Force Telemetry on an Exposed VM 🌐"
description: "1,595 brute-force attempts. 64 IPs. 20+ countries. A month of SSH login fails against my Oracle Cloud VM, with a globe to make it look impressive."
date: 2026-04-25
category: "operations"
tags: ["ssh", "brute-force", "fail2ban", "oracle-cloud", "telemetry"]
readTime: "6 min read"
---

I provisioned an Oracle Cloud ARM VM a few months ago. It runs Jellyfin, holds my recon tooling, and otherwise sits there breathing quietly into the void. Today, on a whim, I ran `sudo journalctl -u ssh -S "30 days ago"` and grepped for failed logins.

**1,595 brute-force attempts. 64 unique source IPs. ~20 countries.**

I knew this was a thing. Every public IPv4 with port 22 open gets scanned within minutes of going up; this is well-documented. But knowing it and watching 1,500 strangers personally try to log in as `admin` are two very different feelings, and I was emotionally unprepared for the second one.

* * *

## Who's knocking?

Top source IPs over 30 days, sorted by sheer determination:

```
   582  190.123.65.197    Betim, Brazil           Gerencia Telecom
   186  193.32.162.151    Amsterdam, NL           Techoff SRV (bulletproof)
   118  217.160.162.192   Berlin, DE              IONOS Cloud
    98  2.57.121.112      Rushden, UK             Unmanaged LTD
    96  2.57.121.25       Rushden, UK             Unmanaged LTD
    90  213.209.159.159   Augsburg, DE            Feo Prest SRL
    77  193.32.162.145    Amsterdam, NL           Techoff SRV
    46  111.52.249.29     Shanxi, CN              China Mobile
```

There is a single bot in Betim, Brazil that has tried 582 times this month. No backoff, no IP rotation, just one machine somewhere outside Belo Horizonte dialing my SSH like a stalker ex who hasn't gotten the message. I almost respect it.

Then there's the cluster on "Unmanaged LTD" in Rushden, England. They have a real website. They describe themselves as "providing reliable hosting solutions". I am sure they are very reliable. The 3,000+ failed login attempts I have received from their network speak for themselves.

The rest of the list is the usual buffet: abused cloud hosting (IONOS, Azure, GCP, Tencent, UCloud all show up further down), residential ISPs in BR/CN/VN/NG, and a couple of mobile carriers whose customers are presumably running malware they bought as a phone game.

* * *

## The username wishlist

`sshd` only logs the username, never the password. But the username list itself tells you what bots are scanning for. Top hits in the last 24 hours:

```
   193  user
    49  debian
    49  admin
    17  tempusr
    17  postgres
    16  sol
    15  oracle
    15  controll
    14  jacob
    14  ansible
```

A few of these deserve a closer look.

**`user`**. 193 attempts. The most generic possible username, and by far the most popular. There is genuinely a small but non-zero chance that some sysadmin somewhere created a Linux user literally named `user`, with the password `user`, and forgot about it. The bots are betting on that chance, every five minutes, forever.

**`controll`**. 15 attempts. They misspelled "control" in the wordlist. I think this typo has been propagating through botnet codebases for the better part of a decade. Some kid copy-pasted it once in 2014 and now it is part of internet history. Future archaeologists will find `controll` in our digital sediment.

**`jacob`**. 14 attempts. There is a Jacob, somewhere out there, who set up a server, used his own first name as the SSH login, picked a password like `jacob123`, and got pwned. The botnet remembers. Jacob's mistake will outlive him. I think about Jacob a lot.

**`solana`, `sol`, `solv`, `jito`, `validator`, `raydium`, `shredstream`**. Combined ~109 hits this month. Bots have figured out that hobbyists are running Solana validators on commodity VMs with painfully predictable usernames. If you have a validator running and your SSH user is literally `sol`, please know that at this exact moment the entire internet is taking turns trying to crack your account. Make better choices.

The rest is just the regular DevOps list: `ansible`, `jenkins`, `nexus`, `moodle`, `n8n`, `odoo`, `azureuser`, `splunk`, `minioadmin`, `sonar`. Bots have noticed that self-hosted DevOps stacks tend to sprout dedicated Linux users with weak SSH passwords, and now those usernames are in everybody's wordlist. Sorry to whoever first set up `jenkins:jenkins` on a public box. You ruined it for the rest of us.

* * *

## How nothing got in

Five lines of `/etc/ssh/sshd_config`:

```
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no
```

That is the entire defense.

With password auth disabled, every one of those 1,595 attempts terminates at "Connection closed by invalid user [...] [preauth]". The bot never even gets to the password prompt. fail2ban catches the loud ones and IP-bans them for ten minutes; over the month it has banned 132 distinct addresses. They come back. fail2ban bans them again. The cycle continues. It is the digital equivalent of slowly closing a door on a Jehovah's Witness who refuses to leave.

Brute-force traffic is not a threat to a properly configured box. It is just background radiation. Like cosmic rays, except angrier and from Brazil.

* * *

## I built a thing

Once I had the data, I had to look at it on a globe. I asked Claude to put together a dashboard with a spinning Earth, glowing dots at every attacker location, animated arcs from each IP back to my box in Mumbai, and live-feed widgets on the side. The texture is NASA's Black Marble (the city-lights one), the rendering is `globe.gl` on Three.js, and the JSON is regenerated by a Python script that parses `journalctl` and pings `ip-api.com` for geo data.

[**→ Live dashboard**](/ssh-attacks/)

![SSH attack telemetry dashboard — globe with attacker locations, side widgets showing top countries and live feed](/images/ssh-attacks-dashboard.png)

What you are looking at:

- Red dots: attacker IPs, sized by hit count
- Animated arcs: attempts arriving at the box
- Pulsing green dot in Mumbai: the box itself
- Side widgets: top countries, top source IPs, top usernames tried, scrolling live feed

Is this objectively overkill for what amounts to a really fancy `tail -f`? Yes. But every time I open it I think *oh, hello Lagos. Hello Shanghai. Hello São Paulo. Hello whatever bot is having a bad day in Vietnam right now*, and it makes me feel something close to fondness for the people trying to break into my server. Not a healthy fondness. But still.

* * *

## What you should do if you have a VM

Three boring rules. They will spare you 99% of the noise.

1. **Disable password auth.** Set `PasswordAuthentication no`, restart sshd, sleep better. Pubkey-only auth is so much stronger than even a great password that there is no contest.
2. **Don't trust default usernames.** `admin`, `oracle`, `postgres`, `solana`, `jenkins`, `jacob` (sorry Jacob) — bots are checking for all of them. Either don't create them, or give them `/usr/sbin/nologin` as a shell.
3. **Read your logs once in a while.** Not because you'll find an actual breach. Because watching 1,500 people fail to break in is genuinely entertaining over morning coffee, and a good reminder that "exposed to the internet" means *exposed to the actual internet*, not the friendly one that lives in your browser tabs.

The internet is a loud neighbourhood. Lock the door, install a peephole, and enjoy the show.
