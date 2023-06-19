---
title: "JWT and CWT Status List"
category: info

docname: draft-looker-jwt-cwt-status-list-latest
submissiontype: independent  # also: "IETF", "IAB", or "IRTF"
number:
date:
v: 3
venue:
  github: "vcstuff/draft-looker-jwt-cwt-status-list"
  latest: "https://vcstuff.github.io/draft-looker-jwt-cwt-status-list/draft-looker-jwt-cwt-status-list.html"

author:
 -
    fullname: Tobias Looker
    organization: MATTR
    email: tobias.looker@mattr.global
 -
    fullname: Paul Bastian
    email: paul.bastian@posteo.de

normative:
  RFC7519: RFC7519
  RFC8392: RFC8392
  RFC3986: RFC3986
  RFC1952: RFC1952
  RFC7515: RFC7515
informative:

--- abstract

This specification defines a status list representation and processing rules for usage with JSON Web Tokens {{RFC7519}} and CBOR Web Tokens {{RFC8392}}.

--- middle

# Introduction

JSON Web Tokens (JWTs) {{RFC7519}} and CBOR Web Tokens (CWTs) {{RFC8392}} as secure token formats, have vast possible applications. Some of these applications can involve issuing a token whereby certain semantics about the token can change over time which are important to be able to communicate to relying parties in an interoperable manner, such as whether the token is considered invalidated or suspended by its issuer.

This document defines a Status List in JWT and CWT representations that describes the individual statuses of multiple Referenced Tokens. The statuses of all Referenced Tokens are conveyed via a bit array in the Status List. Each Referenced Token is allocated an index during issuance which represents a position within this bit array and the value of the bit(s) at this position correspond to the Referenced Token's status. The document also defines how an issuer of a Referenced Token in JWT or CWT representation references a Status List Token. Status Lists may be composed for expressing a range of Status Types, the document defines basic Status Types for the most common use cases as well as an extensibility mechanism for custom Status Types. The Status List Token may be used by an issuer in the Issuer-Holder-Verifier model, as described in (XXX) to express the status of verifiable credentials (Referenced Tokens) issued by an issuer.

The following diagram depicts the basic conceptual relationship.

~~~ ascii-art

+------------------+                    +-------------------+
|                  |      References    |                   |
|                  |------------------->|                   |
| Referenced Token |                    | Status List Token |
| (JWT/CWT Based)  |                    |  (JWT/CWT Based)  |
|                  |  Describes Status  |                   |
|                  |<-------------------|                   |
+------------------+                    +-------------------+
~~~

## Rationale

Revocation mechanisms are an essential part for most identity ecosystems. In the past, revocation of X.509 TLS certificates has been proven difficult as traditional certificate revocation lists (CRLs) have limited scalability and the Online Certificate Status Protocol (OCSP) has additional privacy risks as the client is leaking the requested website to a third party. OCSP stapling is addressing some of these problems at the cost of less up-to-date data. Modern approaches use accumulator-based revocation registries and Zero-Knowledge-Proofs to accommodate for this privacy gap but face scalability issues again.

The approach of this specification seeks to find a balance between scalability, security and privacy by minimizing the status information to mere bits and compressing the resulting binary data. Thereby a Status List may contain statuses of 100.000 or more Referenced Tokens, but still remain relatively small. Placing large amounts of Referenced Tokens into the same list also enables a herd privacy towards the Issuer.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Terminology

Status List
 A bit array that lists the statuses of many Referenced Tokens.

Status List Token
 A token in JWT or CWT representation that contains a Status List.

Referenced Token
 A token in JWT or CWT representation which contains a reference to a Status List Token. The information from the contained Status List may give a verifier additional information about up-to-date status of the Referenced Token.


# JSON Web Token Representation

## Referenced Token Format and Processing Requirements {#jwt-referenced-token}

The following rules apply to validating a Referenced Token in JWT representation which references a Status List Token. Application of additional restrictions and policy are at the discretion of the verifying party.

1. The JWT MUST contain an "iss" (issuer) claim that contains a unique string based identifier for the entity that issued the JWT. In the absence of an application profile specifying otherwise, compliant applications MUST compare issuer values using the Simple String Comparison method defined in Section 6.2.1 of {{RFC3986}}. The value MUST be equal to that of the "iss" claim contained within the referenced Status List Token.

2. The JWT MUST contain an "status" (status) claim conforming to the rules outlined in [](#jwt-referenced-token-status)

The following example is the decoded header and payload of a JWT meeting the processing rules as defined above.

~~~ ascii-art

{
  "alg": "ES256",
  "kid": "11"
}
.
{
  "iss": "https://example.com",
  "status": {
    "bits": 1,
    "idx": 0,
    "uri": "https://example.com/statuslists/1"
  }
}
~~~

### Status Claim Format {#jwt-referenced-token-status}

The following rules apply to validating the "status" (status) claim

1. The claim value MUST be a valid JSON object.

2. The claim value object MUST contain an "idx" (index) attribute with a numeric based value that represents the index to check for status information in the Status List for the current JWT. The value of this attribute MUST be a non-negative number, containing a value of zero or greater. Refer to xx for details on the validation procedure.

3. The claim value object MUST contain a "uri" attribute with a string based value that identifies the Status List containing the status information for the JWT. The value of this attribute MUST be a uri conforming to {{RFC3986}}

## Status List JWT Format and Processing Requirements {#jwt-status-list-format-and-processing}

The following rules apply to validating a JWT based Status List Token. Application of additional restrictions and policy are at the discretion of the verifying party.

1. The JWT MUST contain an "iss" (issuer) claim that contains a unique string based identifier for the entity that issued the JWT. In the absence of an application profile specifying otherwise, compliant applications MUST compare issuer values using the Simple String Comparison method defined in Section 6.2.1 of {{RFC3986}}. The value MUST be equal to that of the "iss" claim contained within the Referenced Token.

2. The JWT MUST contain a "sub" (subject) claim that contains an unique string based identifier for that Referenced Token. The value MUST be equal to that of the "uri" claim contained in the "status" claim of the Referenced Token.

3. The JWT MUST contain an "iat" (issued at) claim that identifies the time at which it was issued.

4. The JWT MUST contain an "status_list" (status list) claim conforming to the rules outlined in [](#jwt-status-list-claim-format).

5. The JWT MAY contain an "exp" (expiration time) claim that convey's when it is considered expired by its issuer.

6. The JWT MAY contain other claims.

7. The JWT MUST be digitally signed using an asymmetric cryptographic algorithm. Relying parties MUST reject the JWT if it is using a Message Authentication Code (MAC) based algorithm. Relying parties MUST reject JWTs with an invalid signature.

8. Relying parties MUST reject a JWT that is not valid in all other respects per "JSON Web Token (JWT)" {{RFC7519}}.

~~~ ascii-art

{
  "typ": "statuslist+jwt",
  "alg": "ES256",
  "kid": "11"
}
.
{
  "iss": "https://example.com",
  "sub": "https://example.com/statuslists/1",
  "iat": 1683560915,
  "exp": 1686232115,
  "status_list": {
    "bits": 1,
    "lst": "H4sIAMo_jGQC_zvp..MAZLRLMQMAAAA"
  }
}
~~~

### Status List Claim Format {#jwt-status-list-claim-format}

The following rules apply to validating the "status_list" (status list) claim

1. The claim value MUST be a valid JSON object.

2. The claim value object MUST contain a "bits" (bit size) attribute with an numeric based value that represents the number of bits per Referenced Token in the Status List ("lst") of the Status List JWT. The allowed values for "bits" are 1,2,4 and 8.

3. The claim value object MUST contain a "lst" (list) attribute with a string based value that represents the status values for all the tokens it conveys statuses for. The value MUST be computed using the algorithm described in [](#jwt-status-list-claim-encoding).

### Status List Encoding {#jwt-status-list-claim-encoding}

Each status of a Referenced Token MUST be represented with a bit size of 1,2,4, or 8. Therefore up to 2,4,16, or 256 statuses for a Referenced Token, depending on the bit-size, are possible. This limitation is intended to limit bit manipulation necessary to a single byte for every operation and thus keeping implementations simpler and less error prone.

1. The overall Status List is encoded as a byte array. Depending on the "bit-size" each byte corresponds to 8/(#bit-size) statuses (8,4,2, or 1). The status of each Referenced Token is identified using the "index" that maps to one or more specific bits within the byte array. The index starts counting at 0 and ends with "size" - 1(being the last valid entry). The bits within an array are counted from least significant bit "0" to the most significant bit ("7"). All bits of the byte array at a particular index are set to a status value.

2. The complete byte array is compressed using gZIP {{RFC1952}}.

3. The result of the gZIP compression is then encoded as URL-safe base64 encoding without padding encoding as defined in Section 2 of {{RFC7515}} and stored as a string.


Example of a Status List representing the statuses of 16 Referenced Tokens (1-bit status type) with indices 0 to 15 (2 bytes):

~~~ ascii-art

status[0] = 1
status[1] = 0
status[2] = 0
status[3] = 1
status[4] = 1
status[5] = 1
status[6] = 0
status[7] = 1
status[8] = 1
status[9] = 1
status[10] = 0
status[11] = 0
status[12] = 0
status[13] = 1
status[14] = 0
status[15] = 1
~~~

These bits are concatenated:

~~~ ascii-art

byte             0                  1               2
bit       7 6 5 4 3 2 1 0    7 6 5 4 3 2 1 0    7
         +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+...
values   |1|0|1|1|1|0|0|1|  |1|0|1|0|0|0|1|1|  |0|...
         +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+...
index     7 6 5 4 3 2 1 0   15   ...  10 9 8   23
         \_______________/  \_______________/
                0xB9               0xA3

~~~

Resulting in the byte array:

~~~ ascii-art

byte_array = [0xB9, 0xA3]
~~~

After compression and Base64URL encoding the generated Status List is:

~~~ ascii-art

"status_list": {
   "bits": 1,
   "lst": "H4sIAMo_jGQC_9u5GABc9QE7AgAAAA"
}
~~~

Example of a more complex status list of length 12 using 2 bit statuses (3 bytes):

~~~ ascii-art

status[0] = 1
status[1] = 2
status[2] = 0
status[3] = 3
status[4] = 0
status[5] = 1
status[6] = 0
status[7] = 1
status[8] = 1
status[9] = 2
status[10] = 3
status[11] = 3
~~~

These bits are concatenated:

~~~ ascii-art

byte             0                  1                  2
bit       7 6 5 4 3 2 1 0    7 6 5 4 3 2 1 0    7 6 5 4 3 2 1 0
         +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+
values   |1|1|0|0|1|0|0|1|  |0|1|0|0|0|1|0|0|  |1|1|1|1|1|0|0|1|
         +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+
          \ / \ / \ / \ /    \ / \ / \ / \ /    \ / \ / \ / \ /
status     3   0   2   1      1   0   1   0      3   3   2   1
index      3   2   1   0      7   6   5   4      11  10  9   8
           \___________/      \___________/      \___________/
                0xC9               0x44               0xF9

~~~

Resulting in the byte array:

~~~ ascii-art

byte_array = [0xC9, 0x44, 0xF9]
~~~

After compression and Base64URL encoding the generated Status List is:

~~~ ascii-art

"status_list": {
   "bits": 2,
   "lst": "H4sIAMo_jGQC_zvp8hMAZLRLMQMAAAA"
}
~~~

# Status Types {#status-types}

This document defines the possible statuses of Referenced Tokens as Status Type values. If the Status List contains more than one bit per token (as defined by "bits" in the Status List) then the whole value of bits MUST describe one value. A Status List can not encompass multiple statuses per individual bits for a Reference Token.

The registry in this document describes the basic Status Type values required for the most common use cases. The registry may be extended as describes in XXX.

## Status Types Values

A status describes the state, mode, condition or stage of an entity that is described by the status list. Status Types MUST be numeric based values between 0 and 255.
Status types described by this specification comprise:
0x00 - "VALID" - The status of the Token is valid, correct or legal.
0x01 - "INVALID" - The status of the Token is revoked, annulled, taken back, recalled or cancelled. This state is irreversible.
0x02 - "SUSPENDED" - The status of the Token is temporarily invalid, hanging, debarred from privilege. This state is reversible.

The issuer of the Status List Token MUST choose an adequate "bits" (bit size) to be able to describe the required Status Types.ST be used for the "typ" attribute within the "status_list".

### Examples
In the first example the Status List shall be used as a revocation list. It only requires the Status Types "VALID" and "INVALID", therefore a "bits" of 1 is sufficient.

In the second example the Status List shall additionally include the Status Type "SUSPENDED. As the Status Type value for "SUSPENDED" is 0x02 and doe snot fit into 1 bit, the "bits" is required to be 2.

## Extended Status List Types


# Security Considerations

## Correct decoding and parsing of the encoded status list
TODO elaborate on risks of incorrect parsing/decoding leading to erroneous status data

## Cached and Stale status lists
TODO consumers/Verifiers of the status list should be aware if they fetch the up-to-date data

## Authorized access to the Status List
If the status list token is provided without any kind of access restriction (allowing everyone to resolve and process the status list), there are some privacy considerations that need to be taken into account (discussed in detail in [](#privacy-considerations)):

- Verifiers are able to re-check the validity of previously provided tokens without consent of the holder.
- Third parties are able to do profiling by periodically checking the contents of the status list.

While this might be wanted behavior depending on the use-case, this should be taken into the consideration when using the status list. Access to the status list can be restricted. There are three general approaches for status list regarding authorization:

- no authentication: the status list can be retrieved and by all involved parties without any kind of restriction.

- verifier authentication: the status list is retrieved by the verifier after successful authentication - this expects some form of verifier authentication to exist. This especially makes sense if verifier authentication is part of holder/verifier interactions and should be strongly considered in that case. This does not prevent re-checks from the verifier but at least excludes untrusted third parties from profiling.

- holder authentication: instead of the status list getting retrieved by the verifier, the holder retrieves the status list (possibly re-using the authorization mechanism that was used for the token issuance) and provides it additionally to the token during a presentation. The verifier could still pool status list presentations from different holders and extract additional information but has no direct access to the status list.

Restricted access to the status list token can be achieved using well-known authorization mechanisms like OAuth 2.0 and should be considered.

## History
TODO elaborate on status list only providing the up-to date/latest status, no historical data, may be provided by the underlying hosting architecture

# Privacy Considerations {#privacy-considerations}

## Herd Privacy
TODO elaborate on herd privacy, size of the status list

## Profiling
TODO elaborate on Verifiers regularly fetching the status list to create a profile, possible countermeasures with authorized access to the status list

## Correlation Risks and Tracking
TODO elaborate on Issuer-Verifier correlation and Verifier-Verifier correlation as the status list introduces unique,trackable data
TODO elaborate on issuers avoiding sequential usage of indices and status lists
TODO elaborate that a status list only gives information about the maximum number of possible statuses that a list conveys, issuers are recommended to pre-allocate lists, use dead entries that are never assigned or other obfuscation mechanisms

## Malicious Issuers
TODO elaborate on issuers generating unique status lists per Referenced Token that do not offer herd privacy

## Hosting Service (what's a better name here?)
TODO elaborate on increased privacy if the status list is hosted by a third party instead of the issuer reducing tracking possiblities
TODO evaluate deifnition of Status List Provider?
 An entity that hosts the Status List as a resource for potential verifiers. The Status List Provider may be the issuer of the Status List but may also be outsourced to a trusted third party.

# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
