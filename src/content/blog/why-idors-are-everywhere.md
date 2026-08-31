---
title: "The Invoice Number Changed. Did the Authorization Decision?"
description: "A historical invoice authorization concern recast as a controlled two-account method for testing and preventing broken object-level authorization."
date: 2025-06-15
category: "research"
tags: ["idor", "web-security", "bug-bounty"]
readTime: "6 min read"
---

The invoice route put a sequential number in front of me. I was authenticated to a test account, opened its invoice, changed only that number, and received a page whose invoice fields differed in the same session. The technical question was not whether the identifier was guessable. It was whether the server repeated the object-authorization decision after the identifier changed.

Amish Patel and Lay Patel at Hacker4Help provided guidance while this work was prepared as part of a cybersecurity learning initiative. The target was a redacted beta e-commerce platform. The historical record preserves the route shape, sequence, and distinct invoice pages, but not a controlled second account or an ownership export. That boundary matters when interpreting the comparison.

## Baseline: the test account's invoice

After a test purchase, the account dashboard linked to an invoice print route shaped like this:

```text
/myaccount/invoice/print/{invoiceId}?type=print
```

I first loaded the invoice linked directly from my authenticated account. That established the baseline session, route, and document structure.

**Sanitized reconstruction:**

```http
GET /myaccount/invoice/print/INV-016?type=print HTTP/1.1
Host: shop.example
Cookie: session=[session omitted]
Accept: text/html
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<main data-invoice-id="INV-016">
  <span class="invoice-number">INV-016</span>
  <span class="order-reference">ORDER-A</span>
  <span class="recipient">CUSTOMER-A</span>
  <span class="total">AMOUNT-A</span>
</main>
```

The values are inert representations of the visible fields, not a byte-for-byte response. The important baseline was that `INV-016`, `ORDER-A`, `CUSTOMER-A`, and `AMOUNT-A` belonged to one rendered invoice reached from the test account dashboard.

![Test account invoice print page showing the baseline invoice fields—the invoice the account was meant to access](/images/blog/why-idors-are-everywhere/1_QiG3-3uCdmdeR9J5xOAHNw.webp)

*The authenticated test account's own invoice print page. This is the baseline document: the account had a legitimate relationship to this invoice, and rendering it was the expected authorization outcome. Dummy test data is visible in the account and transaction fields.*

## Variant: change one object reference

I kept the same authenticated session, HTTP method, route, query string, and headers. I changed only the path identifier from `INV-016` to the adjacent `INV-017`.

```http
GET /myaccount/invoice/print/INV-017?type=print HTTP/1.1
Host: shop.example
Cookie: session=[session omitted]
Accept: text/html
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<main data-invoice-id="INV-017">
  <span class="invoice-number">INV-017</span>
  <span class="order-reference">ORDER-B</span>
  <span class="recipient">CUSTOMER-B</span>
  <span class="total">AMOUNT-B</span>
</main>
```

The page retained the same invoice template but returned a distinct set of values:

| Comparison field | Baseline response | One-ID variant | Observation |
|---|---|---|---|
| Requested path object | `INV-016` | `INV-017` | Only controlled request change |
| Rendered invoice number | `INV-016` | `INV-017` | Different object reference |
| Order reference | `ORDER-A` | `ORDER-B` | Different order value |
| Recipient marker | `CUSTOMER-A` | `CUSTOMER-B` | Different redacted recipient value |
| Total marker | `AMOUNT-A` | `AMOUNT-B` | Different rendered total |
| HTTP result | `200` invoice page | `200` invoice page | No denial on the variant |

I stopped after establishing that one changed identifier selected a distinct invoice-shaped object. I did not continue through a range, estimate scale, download a collection, or try update and deletion routes.

![Invoice print page returned after changing only the sequential identifier from INV-016 to INV-017 within the same authenticated session](/images/blog/why-idors-are-everywhere/1_6pz8TufSLIgbyl6L2znOtw.webp)

*A different invoice page was returned after changing one path parameter. The rendered invoice number, order reference, and recipient marker all differ from the baseline. The same session produced a 200 response with distinct data—the server did not deny the request. Whether this invoice belongs to another customer or is simply an unowned test entry is not proven by this capture alone.*

## What the historical comparison proves

The retained sequence supports these narrow observations:

1. an authenticated account could reach an invoice print route;
2. a sequential identifier selected the invoice object;
3. changing only that identifier in the same session returned another `200` invoice page; and
4. multiple redacted fields differed, so this was not merely the same document reflected under a new URL.

It does **not** preserve the ownership mapping needed to prove that `INV-017` belonged to a non-owner account. The old prose described it as another customer's invoice, but there is no retained Account B fixture, account-to-invoice export, or reciprocal request. The sequence is strong evidence of a distinct-object authorization concern; historical cross-account ownership remains unproved.

It also does not support claims of thousands of invoices, full database access, payment-card exposure, unauthenticated access, account takeover, record modification, deletion, present-day exposure, remediation, or retest.

## The authorization decision that should have happened

Authentication answers “who sent this request?” Object-level authorization answers “may this subject read this invoice?” The policy should be evaluated after resolving the route and before rendering the object:

```text
subject = authenticated account from server-verified session
object  = invoice selected by invoiceId
action  = read_print_view
allow   = object.owner_id == subject.id
          OR explicit role policy permits this action
```

The unsafe lookup shape is:

```text
invoice = invoices.find(request.params.invoiceId)
return render(invoice)
```

The safe shape scopes retrieval and still makes the action explicit:

```text
subject = authenticated_subject(session)
invoice = policy_scope(subject, invoices)
            .find(request.params.invoiceId)
require_allowed(subject, "read_print_view", invoice)
return render(invoice)
```

A UUID would make guessing harder, but it would not repair this decision. Object references leak through links, logs, browser history, exports, and related APIs. Authorization has to hold even when the caller knows a valid identifier.

## Controlled owner/non-owner validation matrix

The clean way to resolve the historical ambiguity—and to keep the fix from regressing—is to create two synthetic accounts and two synthetic invoices in an authorized test environment:

```text
Account A owns INVOICE-A
Account B owns INVOICE-B
Role S is an approved support role, if the product defines one
```

Then record the complete matrix rather than relying on an adjacent number:

| Authenticated subject | Requested object | Route/action | Expected policy result | State to verify |
|---|---|---|---|---|
| Account A | `INVOICE-A` | HTML print view | Allow | Baseline A fields returned |
| Account A | `INVOICE-B` | HTML print view | Deny | No B fields returned |
| Account B | `INVOICE-B` | HTML print view | Allow | Baseline B fields returned |
| Account B | `INVOICE-A` | HTML print view | Deny | No A fields returned |
| Unauthenticated | `INVOICE-A` | HTML print view | Deny | No invoice body returned |
| Account A | `INVOICE-A` | Download/PDF | Allow | Own synthetic file returned |
| Account A | `INVOICE-B` | Download/PDF | Deny | No non-owner file returned |
| Account A | `INVOICE-B` | Preview/API | Deny | No non-owner fields returned |
| Account A | `INVOICE-B` | Update | Deny | B object unchanged on fresh read |
| Account A | `INVOICE-B` | Delete | Deny | B object still exists for owner |
| Approved Role S | `INVOICE-A` | Documented support read | Allow only if policy says so | Decision logged with purpose |
| Unapproved role | `INVOICE-A` | Any invoice read | Deny | No invoice fields returned |
| Account A | unknown ID | Any read route | Safe denial | Response does not disclose existence |

For each case, capture the sanitized request, authenticated subject, object-owner fixture, action, status, response fingerprint, and a fresh owner-side state read for mutations. Reciprocal A-to-B and B-to-A denials prove that the rule follows ownership rather than a special-case identifier.

## Route-by-route fix and tests

The same policy must guard every route that resolves an invoice: HTML view, print view, PDF/download, preview, API, email/share workflow, update, and deletion. A centralized policy scope reduces drift, but each action still needs a test because legitimate role rules may differ.

Useful regression assertions are concrete:

```text
owner read       → 200 + own object fingerprint
non-owner read   → safe denial + no object fields
unknown object   → same safe denial class
non-owner update → denial + unchanged owner-side fingerprint
non-owner delete → denial + object still available to owner
approved support → allowed only for documented role/action/purpose
```

The server should derive identity from the verified session, deny by default when ownership or role is unresolved, avoid trusting a client-supplied account ID, and log the policy decision without copying invoice contents into logs. Consistent denials can avoid turning status or body differences into an object-existence oracle.

## The practical lesson

A sequential number is a lead, not a vulnerability. The useful evidence is the controlled comparison: baseline object, one changed reference, distinct response, ownership fixture, reciprocal policy checks, and a stop condition.

In the historical test, the first three pieces survive and the ownership fixture does not. Keeping that gap visible is more accurate than erasing the technical sequence or overstating it. The regression matrix shows exactly what would turn the concern into a proved owner/non-owner authorization result—and exactly what the application must continue to enforce.
