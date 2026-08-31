---
title: "I Thought I Found a Subdomain Takeover. I Had Not."
description: "A false-positive investigation showing why suspicious DNS and verification records did not establish a claimable third-party resource."
date: 2025-07-05
category: "research"
tags: ["subdomain-takeover", "dns", "web-security"]
readTime: "7 min read"
---

A company was reportedly taking services offline. Kaif Shah and I asked the obvious security question: had any forgotten subdomain been left pointing at abandoned infrastructure?

Within minutes, an automated scanner labelled one host as a possible Amazon S3 takeover. For a moment, the story seemed to write itself.

Then DNS ruined the story—in the useful way. The expected delegation was not there, the TXT response did not mean what we first thought it meant, and we could not establish an externally claimable resource. This was a false positive.

The original target and timestamps are redacted. No current lookup or provider claim was performed for this rewrite, and the historical authorization and reporting records are not retained. The commands below preserve the workflow with an inert domain; no target screenshot is included because the available captures expose unredacted operational details.

## Enumeration before takeover scanning

We started by enumerating subdomains, then probing the resulting hosts for HTTP state and DNS context:

```bash
sudo subfinder -d target.example -o subfinder.txt

sudo httpx-toolkit \
  -l subfinder.txt \
  -o httpx.txt \
  -cname \
  -ip \
  -title \
  -sc
```

`subfinder` supplied candidates. `httpx-toolkit` added status codes, titles, IPs, and CNAME values where available. None of those fields established takeover; they helped prioritize which host deserved manual DNS review.

The historical scanner invocation was:

```bash
subjack \
  -w subfinder.txt \
  -t 100 \
  -timeout 30 \
  -ssl \
  -c ~/Downloads/fingerprints.json \
  -v
```

The important flag was `-c`: it selected the fingerprint database used to classify provider error responses. The scanner associated one redacted host with an S3 bucket fingerprint. That was an automated label based on a response pattern, not proof of a CNAME, a deleted bucket, or the ability to claim anything.

![Automated scanner output flagging a host as a possible S3 bucket takeover candidate](/images/blog/subdomain-takeover/1_stBzv0SOC1jbQJFOrxpHqQ.webp)

*Scanner output associating a host with an S3 bucket takeover fingerprint. The tool labelled one host as `[S3 BUCKET]` based on a response pattern — a prioritization lead, not proof of DNS delegation, provider ownership, a missing resource, external claimability, or takeover.*

The high thread count made the first pass fast, but it did not make the conclusion reliable. A stale fingerprint, generic error page, transient response, or virtual-host mismatch can all produce a candidate worth checking and nothing more.

## What the scanner hypothesis required

For the S3 label to become a takeover finding, several links had to hold:

```text
TARGET HOSTNAME
    |
    +--> DNS routes to a specific S3 website/service endpoint
             |
             +--> the expected bucket or domain binding is absent
                      |
                      +--> another authorized account can claim it
                               |
                               +--> the provider will serve that account's
                                    content for the target hostname
```

The scanner only suggested the provider-fingerprint link. We still needed DNS delegation, missing-resource behavior, and provider-specific claimability.

## Manual CNAME and TXT checks

I queried the suspicious name directly and requested concise output first:

```bash
# Sanitized reconstruction
host='assets.target.example'

dig +noall +answer CNAME "$host"
dig +noall +answer TXT "$host"
```

The retained result state was:

```dns
; Sanitized reconstruction
; CNAME answer: empty

assets.target.example. 300 IN TXT "[redacted verification value]"
```

I then captured full answers for the surrounding record types instead of treating an empty CNAME answer as the finish line:

```bash
# Sanitized reconstruction
for type in A AAAA CNAME NS TXT; do
  dig "$type" "$host"
done
```

The historical notes preserve no CNAME answer and at least one TXT value. They do not preserve complete A/AAAA answers, TTL history, resolver identity, or provider-side configuration. So the narrow conclusion is that the manual check did not reveal the CNAME chain expected by the S3 hypothesis—not that every possible routing mechanism was absent.

![Manual dig output showing no CNAME answer and a TXT record for the investigated hostname](/images/blog/subdomain-takeover/1_076ZcP-S1SucdfUyhwY1-w.webp)

*Manual DNS lookup retained from the investigation. The CNAME answer was empty and at least one TXT value was present. This showed active-looking configuration at the hostname — but TXT data does not route HTTP traffic, identify an S3 bucket, prove a resource exists, or universally stop another account from binding a domain.*

## My TXT-record wrong turn

At the time, we described the TXT record as a defensive control that “prevented takeover.” That was too confident.

A TXT value is data attached to a DNS name. It may be used for domain verification, email policy, certificate validation, or something unrelated. Its presence does not route HTTP traffic, identify an S3 bucket, prove a resource exists, or universally stop another account from binding a domain.

The TXT answer was still relevant because it showed active-looking configuration at the hostname. But only the exact provider product and its current ownership rules could tell us whether that value participated in custom-domain verification. We did not have that evidence.

## Why “no CNAME” weakened rather than proved the case

A classic dangling-service pattern looks like this:

```dns
assets.target.example. 300 IN CNAME abandoned-bucket.s3-website-region.amazonaws.com.
```

That answer would establish routing to a provider endpoint. It still would not prove that the backing bucket was missing or claimable.

Our lookup did not return that chain. This removed the simplest explanation for the scanner's S3 label. It did not prove safety: an A/AAAA record, CDN mapping, DNS-provider alias, historical record, or provider-side custom-domain mapping might require separate review. None was retained here, so inventing one would merely replace the scanner's unsupported assumption with mine.

## Dangling DNS is not the same as claimability

I now separate six questions:

1. **Delegation:** Does DNS or HTTP routing reproducibly reach a specific third-party product?
2. **Resource state:** Does provider-specific evidence show the expected resource or binding is missing?
3. **Fingerprint quality:** Is the error response unique enough to that missing-resource state?
4. **External claimability:** Could a different authorized account create the exact resource or bind the hostname?
5. **Ownership controls:** Does the provider require DNS, file, account, or certificate validation unavailable to that account?
6. **Minimal proof:** If explicitly permitted, can harmless content be served through the target hostname and removed safely?

A scanner can help with question three. `dig` can help with question one and reveal ownership-control clues for question five. Neither answers the whole chain.

We never attempted to create a bucket, bind the hostname, alter DNS, upload content, or serve a proof page. Provider-side claiming changes state and can create cost, collision, and ownership problems; it requires explicit authorization and a cleanup plan. Because delegation was already unproven, there was no technical reason to approach that boundary.

## The decision tree I use now

```text
Scanner flags a hostname
|
+-- Save timestamped DNS and HTTP evidence
|
+-- Is there a repeatable route to one third-party product?
|   |
|   +-- No --> classify as scanner mismatch / false positive; stop
|   |
|   +-- Yes --> identify the exact product and resource-name rule
|
+-- Does product-specific evidence show a missing binding?
|   |
|   +-- No --> not dangling; document and stop
|   |
|   +-- Unclear --> report a potential stale mapping without claiming takeover
|   |
|   +-- Yes --> assess ownership verification and namespace rules
|
+-- Can external claimability be established without creating a resource?
|   |
|   +-- No or unclear --> do not claim; give owner the evidence
|   |
|   +-- Yes --> check explicit authorization for state-changing validation
|
+-- Is a harmless provider-side proof specifically authorized?
    |
    +-- No --> stop and report the suspected condition
    |
    +-- Yes --> use the minimum proof, capture it, remove it, and retest
```

Our case exited at the first decision: no reproducible provider route was established from the retained DNS evidence. The correct label was **false positive**, not “protected takeover” and not “almost compromised.”

## Reporting the result without overselling it

A useful report could say:

> An automated fingerprint associated the redacted hostname with an Amazon S3 takeover pattern. Manual DNS inspection did not return the expected CNAME delegation and did return a TXT value of unresolved purpose. I could not establish routing to S3, a missing resource, or external claimability. Please review current and historical DNS records plus any custom-domain binding for this hostname.

That gives the owner three concrete things to verify without pretending we controlled the name. The retained material does not confirm that this report was delivered, acknowledged, remediated, or retested.

## Remediation and defensive testing

For asset owners, prevention is mostly lifecycle discipline:

- inventory DNS names with service owner, provider product, resource identifier, and expiry date;
- remove or change DNS before deleting a third-party resource;
- use provider ownership verification where available, but document exactly what it protects;
- alert on CNAME destinations, HTTP fingerprints, and certificate changes;
- review A, AAAA, CNAME, NS, TXT, and provider-side aliases rather than relying on one record type; and
- verify decommissioning from multiple resolvers after TTL expiry.

A safe retest should confirm that DNS no longer routes to an abandoned service and that the provider no longer returns a missing-resource fingerprint. If provider claimability must be evaluated, the owner should do it in a controlled account or explicitly authorize a minimal test with cleanup steps. A TXT record alone is not a passing test.

The best result from this investigation was not a takeover. It was catching our own reasoning before a scanner label became a vulnerability claim.