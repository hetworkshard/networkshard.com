---
title: "One APK, 91 Gyms' Keys, and a Backend That Never Asked Who I Was"
description: "I downloaded one gym app and walked away holding 90 other gyms' backend keys. Then the server behind it started handing out admin sessions and member records to anyone who knew a number. A story about white-label apps going brrr."
date: 2026-08-31
category: "research"
tags: ["apk-analysis", "mobile-security", "white-label", "multi-tenancy", "broken-authorization", "pii-exposure", "firebase", "responsible-disclosure"]
readTime: "9 min read"
---

I downloaded one gym's Android app. By the time I finished reading its asset folder, I was sitting on the config for ninety *other* gyms — every one a separate business, a separate paying customer of the same platform, all crammed into the same 68 MB binary. 🫠

That was surprise number one. Number two was worse and it lived on the server: the backend would hand you an admin session, or a named member's record, if you asked nicely. And "asking nicely" meant a URL with a number in it.

Everything identifying here is redacted — the platform, the domain, the gyms, the package names, the keys, and one very real member. The reasoning survives that. The identifiers don't need to.

## one app, ninety-one landlords

The target was a white-label fitness app. You know the genre: one vendor builds an app once, re-skins it per client, and ships a hundred near-identical copies. Branding is the gym's. Plumbing is the vendor's.

Boring Flutter-over-Kotlin, nothing to see — until I opened the assets folder and it wasn't *a* config. It was a directory of them. **91 tenant config files**, one per gym on the platform, sitting in plaintext JSON.

```text
assets/flutter_assets/assets/
├── [redacted-gym-01].json
├── [redacted-gym-02].json
│   … 88 more …
└── [redacted-gym-91].json
```

Every file was a *different* business — its name, its backend API key, its Firebase project. The app I installed needed exactly one of these. It carried all ninety-one.

There's no world where a customer of Gym A needs Gym B's backend key living on their phone. The second I saw file number two, this stopped being an app bug and became an architecture confession: every tenant's app was a photocopy of every tenant's secrets.

## the keys, and which ones actually mean anything

Time to be annoyingly precise, because these are not all worth the same and I'm not going to fear-monger a key count at you.

Here's one file, gutted and redacted:

```json
{
  "app_name": "[REDACTED]",
  "androidPackageName": "com.app.[redacted]",
  "apiKey": "[REDACTED — opaque base64 backend key]",
  "androidFirebaseOptions": {
    "apiKey": "AIza…[REDACTED]",
    "projectId": "[redacted]-xxxxx",
    "storageBucket": "[redacted]-xxxxx.firebasestorage.app"
  }
}
```

The Firebase `AIza…` key? **Not the finding.** People screw this up constantly. A Firebase Web/Android key is an *identifier*, not a secret — Google literally means for it to ship in your app. On its own it unlocks nothing. What decides whether it's dangerous is the project's **Security Rules**. Rules locked down → the key is a dead fish. Rules wide open → that same key reads and writes the whole database. I didn't test the rules, because testing them means reading tenant data that isn't mine. So I'm not going to stand here and claim Firestore was popped. That door was *visible*. I didn't kick it.

The backend `apiKey` is the spicy one. It's an opaque per-tenant token the app uses to talk to the platform's own API. Ninety-one of them, in the clear, in one download. If that's the token the backend trusts to act *as* a tenant, then owning all of them is basically owning the platform — but again, I didn't prove that, so I won't sell it to you as proven. What I *will* say: no client-side token should ever be a cross-tenant master key, and here every gym was gift-wrapping every other gym's token for anyone with the APK.

So: one confirmed structural faceplant (mass cross-tenant secret sharing, by design) and two *maybe* risks I flagged but left alone. That line — proven vs. plausible — matters way more than "303 keys!!!" in a headline.

## the server rats itself out

The app told me who to call. The backend told me everything else, because it was running in debug mode. In production. In 2026.

Poke a route that doesn't exist → the framework spits back its full debug error page → and on this stack, that page prints the **entire URL map**. Every route the app knows, in order. It was a long-dead major version of the framework on an equally dead language runtime, so this behavior was both expected and never getting patched.

No fuzzing. No wordlists. No string-scraping the APK. The server just handed me its routing table like a menu. Most of it was normal, session-gated stuff. A few entries were… not.

## endpoints that never asked for ID

I'm describing these by what they *do*, not by their literal paths. The exact route strings are identifying, and printing them just helps someone rediscover a live target while teaching nobody anything. The lesson is the mistake, not the URL.

Three routes stood out because they took an identifier in the URL and coughed up sensitive data with **zero auth**:

```text
GET  /<redacted-admin-login>/<fitness_center_id>/
     → 302 → an authenticated staff dashboard for that gym

GET  /<redacted-phone-lookup>/?PhoneNo=<number>
     → a customer record: name, phone, email, gym, internal ID

GET  /<redacted-member-info>/<customer_id>/
     → full membership card: plan, category, expiry
```

The first one made me read it three times. Feed it a gym's number and it **302s you straight into that gym's staff dashboard**. No login. No session. No token. A number in a path *was* the login. And the gym IDs were sequential across several thousand centers, so "which gyms" wasn't exactly a puzzle.

The other two are the classic broken-object-authorization move — the one I keep writing about because it never dies. The server happily re-runs the *lookup* when the ID changes, but never re-runs the *authorization check*. Swap the phone number, get a different human. Swap the customer ID, get a different card. Guessable IDs were never the point. The point is nobody ever asked "wait, is this caller allowed to see this?"

## one record, then hands off

A debug page and some suggestive route names aren't a finding — they're a vibe. To turn a vibe into a finding I needed exactly one confirmed pull, and then I needed to stop.

So: one phone number → the lookup route → a live customer record. Real name, real phone, the gym they belong to, their internal ID. Fed that ID into the membership route → their card: plan tier, training category, an expiry way out in the future.

One real member, reconstructed end to end — who they are, where they train, what they pay for — from two unauthenticated GETs and nothing but a phone number to start.

I'm not printing that record. Name, number, gym, dates — all redacted, because that's a real person who didn't sign up to be my PoC screenshot. One confirmed record proved the endpoints return live production data. A second would've proven nothing new and burned somebody else. So I stopped at one.

## what I didn't do (and I want this on the record)

This part matters as much as the findings, so no jokes here.

I did **not** enumerate the member base. The lookup would've answered for arbitrary numbers and the admin route would've opened arbitrary gyms — I confirmed the behavior on a single record, on a single path, and stopped. I didn't measure how many people were affected, because measuring it means harvesting them.

I did **not** log into a dashboard that wasn't mine, pivot a staff session into admin functions, touch a single record, read anyone's Firestore or Storage, or test whether those bundled backend keys work across tenants. All of it was *visible* from where I stood. None of it was mine to walk through.

I did **not** decode or publish key material. Firebase keys, backend tokens, payment analytics IDs — real, redacted, not reproduced.

The job was to show the doors exist and that they open. Not to inventory the building. "I could have" is not a measurement, and I'm not going to cosplay one as impact.

## why this keeps happening

Two root causes, and they rhyme.

**Client-side secrets don't scale.** That white-label build was almost certainly churned out by a pipeline: take the vendor app, inject the tenant config, ship. Somewhere in there, "inject the tenant's config" quietly became "inject *everyone's* config" — and because the app worked flawlessly for its one intended gym, nobody clocked the ninety stowaways. The app never *used* the extras, so the extras were invisible in testing. On a multi-tenant platform the client binary is a public document. Per-tenant secrets are things it's never allowed to hold — least of all a neighbor's.

**Authentication ≠ authorization, and an ID is neither.** These routes didn't break because the IDs were sequential. Make them UUIDs and nothing changes. They broke because the server answered "what object is this?" and never once asked "is this caller allowed to have it?" A number in a URL is a lead. It is not a credential.

Neither of these is exotic. Both survive to prod precisely *because* the app works. Happy path's clean, tests are green, and the extra configs and missing auth checks only show up if you go looking for what shouldn't be reachable. Which, y'know. That's the job. 🧠

## the fixes that would've held

For the vendor, in order:

1. **Stop shipping tenant config in the binary.** The app fetches *its own* tenant's config after it authenticates, and nothing else. No app should be able to *name* another tenant's keys, let alone read them.
2. **Rotate everything that shipped, and treat it as burned.** Every backend key and Firebase project that rode in the shared binary is public now. A key that's been in an APK download is not a secret. It's a fun fact.
3. **Put a real authorization check behind every object route.** Every endpoint that takes an ID re-verifies the caller owns the thing — on read *and* every write. The admin-by-ID route shouldn't exist in its current shape at all.
4. **Turn off debug mode in prod.** The URL map, the stack traces, the server paths — all handed out for free. One config flag, huge blast radius.
5. **Bury the end-of-life stack.** A framework and runtime that stopped getting security patches years ago can't be the floor under this many businesses' member data.

None of this is research. It's hygiene. The findings were only interesting because the hygiene was missing at the *seams between tenants* — exactly where a single-tenant test never looks.

---

The download only needed one gym. It carried ninety-one, and the server behind it never asked who was calling. Neither of those is a clever exploit. Both are just what happens when you build a platform one tenant at a time and never audit it as the ninety-one-tenant beast it actually became.

Don't ship the whole keyring in every app. And ask people for ID at the door. 🫰

*Everything identifying — the platform, the domain, the tenant businesses, package names, key material, and the member record I used to confirm this — is withheld while these issues are still live. Run this platform and want the specifics? That's a coordinated-disclosure conversation, not a search box.*
