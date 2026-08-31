---
title: "From Search Results to Two CERT-In Recognitions"
description: "A restrained account of using indexed government-domain pages as reconnaissance leads, preserving evidence, and separating two CERT-In recognitions from unsupported conclusions."
date: 2025-11-25
category: "research"
tags: ["bug-bounty", "CERT-IN", "recon"]
readTime: "5 min read"
cover: "/images/blog/from-dorks-to-defense/1_p0iY_bLGcryt7loqJ2s12Q.webp"
coverAlt: "Indexed government-domain pages surfaced through targeted search queries"
pinned: true
---

I started with a search box, not a scanner.

That sounds simple because it was. Search indexes had already mapped a useful slice of the public attack surface. My job was to turn those results into scoped leads, discard the noise, and test the remaining behavior with as little contact as possible.

A search result was never permission or proof. Before touching a result, I had to confirm the policy and reporting route for that specific system. The public record retained for this draft does not preserve that full authorization timeline, so the real hosts and reusable payloads remain redacted.

## Building query families instead of one magic dork

I grouped queries by the question they answered. These are sanitized shapes, not a claim that every matching page was sensitive or in scope.

```text
# Use only a host explicitly assigned for controlled review
site:[AUTHORIZED-HOST] [public crawler-map path shape]
site:[AUTHORIZED-HOST] [public client-script file shape]

# Documents and archives that require manual sensitivity review
site:[AUTHORIZED-HOST] [document-extension family]
site:[AUTHORIZED-HOST] [archive-or-backup-extension family]

# Dynamic pages where one parameter can be compared safely
site:[AUTHORIZED-HOST] [dynamic-page path] [single parameter shape]

# Configuration pages; a match is only a lead until opened and reviewed
site:[AUTHORIZED-HOST] [runtime-diagnostics page shape]
```

Broad file queries generated the most false positives. A PDF could be intentionally public; an archive-looking URL could be dead; an admin-looking path could enforce authentication correctly. I recorded the result, removed duplicates and stale pages, and kept only pages whose behavior could be checked without collecting data or changing state.

## Two endpoint shapes stood out

The useful leads were parameterized PHP pages. Their historical shapes were roughly:

```text
GET /testimonial.php?lang=2&lid=2464 HTTP/1.1
Host: portal-a.example

GET /search.php?page=14&fromdate=26-04-2024&todate=27-04-2024&state_name=35&circle=&division=&range=&block=&beat=&source= HTTP/1.1
Host: portal-b.example
```

These are **sanitized reconstructions**. The names `lang`, `lid`, `page`, date fields, `state_name`, and the empty geographic filters matter because they show where user-controlled values entered each request. They do not establish what the server did with those values.

My first wrong turn was treating “many parameters” as inherently exciting. Most were boring. Changing pagination changed the page. Changing a date changed the result set. Blank filters remained blank. That baseline work was useful precisely because it separated normal application behavior from one unusual branch.

## Baseline first, one variation second

For each candidate parameter, I captured the ordinary response before changing anything. Then I varied one value while keeping method, path, headers, and all other parameters stable.

```http
# Sanitized reconstruction — baseline
GET /testimonial.php?lang=2&lid=2464 HTTP/1.1
Host: portal-a.example
Accept: text/html

# Sanitized reconstruction — one syntax-relevant variation
GET /testimonial.php?lang=2%27&lid=2464 HTTP/1.1
Host: portal-a.example
Accept: text/html
```

The same discipline applied to the larger search request:

```http
# Sanitized reconstruction — baseline
GET /search.php?page=14&fromdate=26-04-2024&todate=27-04-2024&state_name=35&circle=&division=&range=&block=&beat=&source= HTTP/1.1
Host: portal-b.example
Accept: text/html

# Sanitized reconstruction — only state_name varies
GET /search.php?page=14&fromdate=26-04-2024&todate=27-04-2024&state_name=35%27&circle=&division=&range=&block=&beat=&source= HTTP/1.1
Host: portal-b.example
Accept: text/html
```

The retained notes describe changed errors and broken rendering after the syntax-relevant variations. That is useful input-handling evidence, but it is not enough to claim database extraction, authentication bypass, or a particular severity. A generic application exception can resemble an injection signal. The next safe question is whether the baseline and variation produce a stable, input-dependent difference—not how much data can be pulled out.

I stopped at the smallest reproducible distinction suitable for a report. I did not enumerate tables, records, users, or neighboring objects.

## Keeping the SQL and reflected-output branches separate

The historical article compressed several observations into “SQL injection and XSS.” That made the chronology sound cleaner than the evidence.

For the SQL branch, the reportable logic was:

1. capture a normal request and response fingerprint;
2. change only `lang` or `state_name`;
3. observe a repeatable diagnostic or rendering difference;
4. return to the baseline to confirm normal behavior; and
5. stop before data access or state change.

For the reflected-output branch, the question was different: did a harmless marker return in the response, and in what HTML context?

```http
# Sanitized reconstruction — inert reflection marker
GET /testimonial.php?lang=MARKER-7F3&lid=2464 HTTP/1.1
Host: portal-a.example
Accept: text/html
```

```html
<!-- Sanitized reconstruction of the relevant response fragment -->
<span class="language">MARKER-7F3</span>
```

That response shape would prove reflection in an HTML text context. It would not prove script execution, persistence, delivery to another user, or impact. Those require their own context-specific evidence. I kept this branch distinct instead of using it to strengthen the SQL claim.

![Terminal and request validation evidence capturing the tested SQL-shaped parameter response against a redacted government endpoint](/images/blog/from-dorks-to-defense/1_p0iY_bLGcryt7loqJ2s12Q.webp)

*Technical testing evidence retained from the investigation. The capture records visible response behavior against a redacted parameterized endpoint. It documents what was observed during authorized testing, not severity or CERT-In acceptance.*

![Response evidence showing SQL diagnostic output captured during parameter testing](/images/blog/from-dorks-to-defense/1_5d4F_vbMcVmiJidEqPK91Q.webp)

*A second diagnostic response associated with parameter-level testing. The old article labelled this "2 SQL Injection," but the evidence shows a response with diagnostic behavior. Whether this represents an independently distinct vulnerability depends on the exact input, endpoint, and root cause—not on a label.*

## A separate PHPInfo exposure branch

The configuration exposure was found through a different query family and had a different cause. A publicly rendered `phpinfo()` page can disclose runtime version, loaded modules, filesystem paths, environment names, and configuration flags.

The validation was deliberately passive:

```http
# Sanitized reconstruction
GET /diagnostics/phpinfo.php HTTP/1.1
Host: portal-c.example
Accept: text/html
```

```text
HTTP/1.1 200 OK
Content-Type: text/html

PHP Version [redacted]
System [redacted]
Loaded Configuration File [path redacted]
```

I recorded only enough fields to show that a real PHP configuration page was publicly rendered. I did not publish paths, environment values, hostnames, or secrets. This was information exposure, not code execution, and the record does not show that any disclosed value was operationally useful.

The historical notes mention several PHPInfo pages. Without safe per-host artifacts, I will not turn that into a precise affected-host count or imply that each page became an independently accepted report.

![Publicly rendered PHP configuration page discovered through passive search-index review](/images/blog/from-dorks-to-defense/1_GbClUe79xPv9M3own-G4jQ.webp)

*A publicly accessible `phpinfo()` page found through a different search-query family. The capture shows runtime version, loaded modules, and configuration flags. This was information exposure, not code execution—no secret was tested for operational usefulness.*

![Second captured PHP configuration page associated with a distinct endpoint](/images/blog/from-dorks-to-defense/1_CwwUwpGMYV0yHRDyBAVjvQ.webp)

*A second captured configuration page. The old article mentions several; this artifact supports that more than one diagnostic page was observed. Whether each became an independently accepted report is not established by this capture alone.*

## What I preserved for reporting

A useful evidence packet contained:

- the indexed URL and timestamp, retained privately;
- the policy or scope consulted at the time;
- a baseline request and response fingerprint;
- one changed parameter and the resulting difference;
- a repeat of the baseline where appropriate;
- the finding branch—SQL signal, reflected output, or PHP configuration exposure;
- an explicit stop point; and
- a sanitized copy with hosts, paths, session values, and personal data removed.

The technical branches stayed separate in the report. One endpoint's diagnostic behavior did not prove the second endpoint was vulnerable, and neither SQL-shaped errors nor PHPInfo output established sensitive-data access.

## CERT-In recognition — September 2025

CERT-In's September 2025 Hall of Fame page lists **Het Patel and Kaif Shah** with “SQL Injection.” That is the narrow documentary link retained for this month; it does not identify the exact endpoint, establish authorization for every test, assign severity, or confirm remediation or retesting.

![CERT-In September 2025 Hall of Fame table with the Het Patel and Kaif Shah entry outlined](/images/blog/from-dorks-to-defense/1_3vdr2a9sNeUeRmFGYdS9bw.webp)

*Recognition record: the September 2025 CERT-In page lists Het Patel and Kaif Shah. It documents the entry shown, not every technical claim or a patch status.*

## CERT-In recognition — October 2025

CERT-In's October 2025 Hall of Fame page lists **Shah Kaif and Het Patel** with “SQL Injection.” The ordering differs, but the proof boundary does not: the page documents recognition in October, not which historical request earned it or whether every item in the earlier article was accepted.

![CERT-In October 2025 Hall of Fame table with the Shah Kaif and Het Patel entry outlined](/images/blog/from-dorks-to-defense/1_oT6i9Y-R4OfGCkdW_3e4Sw.webp)

*Recognition record: the October 2025 CERT-In page lists Shah Kaif and Het Patel. It does not confirm remediation, retesting, or acceptance of unrelated findings.*

## Defensive fixes and retesting

The fixes depend on the branch:

- **SQL-shaped input handling:** use parameterized queries, validate values by type and allowed range, avoid concatenating request parameters into SQL, and keep database diagnostics out of client responses.
- **Reflected output:** encode for the actual output context, reject invalid language identifiers, and add response tests containing reserved HTML characters.
- **PHPInfo exposure:** remove diagnostic scripts from public document roots, restrict operational diagnostics to authenticated administrators, and rotate any secret that was actually exposed rather than assuming removal alone is enough.
- **Search-index residue:** return an appropriate terminal status for removed pages, remove sensitive documents at the origin, and use de-indexing only after fixing the source exposure.

A proper retest would replay the original sanitized baseline and variation against the exact endpoint, confirm generic errors and unchanged behavior, verify inert markers are encoded, and confirm configuration pages are unavailable without authorization. I do not have retained retest evidence for these historical endpoints, so I am not claiming those checks passed.

The recognitions matter to me. The stronger lesson, though, was methodological: search gave me leads; parameter-level comparisons gave me evidence; separating each branch kept that evidence honest.