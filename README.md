# Experimental JWT auth solution

## Purpose

This prototype asks the question "what if there was no OAuth?"

## Rationale

The rationale is as follows:
 * OAuth is designed to allow a third-party service to access your resources on behalf of a user
 * The RoS use case is that users authenticate centrally (a single sign-on) and that this authentication token 
   (carrying authorisation information) is trusted by other RoS apps.
 * The other RoS apps need to be able to trust the identity and authorisations that are being asserted by a user.
 * The other RoS apps do not need to access resources owned by the central authentication.
 * Therefore a digitally signed token (e.g. JWT) is both necessary and sufficient for trusted assertion.
 * Not using OAuth could significantly reduce complexity and potential for errors.

## Features and benefits

 * *Public-private key signatures*: this avoids the need for a shared secret between auth and clients, simplifying deployment.
 * *Elliptic curve digital signatures*: part of the JWT standard, ECDSA uses shorter keys and produces smaller signature blocks with significantly faster performance than RSA.
 * *Ephemeral keys*: the design of this prototype avoids the need for private key storage and transmission on startup. It ensures a group of stateless instances can sign JWTs and support verification of signatures created by any instance (running or exited).
 * *API design*: the format for the `/keys` endpoint is designed to follow the same API pattern as Github, e.g.: https://api.github.com/users/davidcarboni/keys

## Exceptions

There is one possible exception to be investigated: the Revenue Scotland Service. It is believed that this is making use of "third-party access to resources", which would be consistent with the intent of OAuth.

There is therefore a need to investigate this service and understand whether it is required (transaction volumes are believed to be extremely low) and whether, if it is required, a JWT solution might still meet the need.

## Implementation

The following is a summary of this implementation:

 * An auth component 
 * An example client app
 * The auth component takes in a `user_id` and `password` and returns a JWT signed with the private key owned by the auth instance
 * Auth instances publish the public keys of all instances (identified by a key ID represented as `kid` in the JWT header) on an endpoint
 * Preferred interaction is a json `username`/`password` request, with a JWT response, where the client is expected to store the JWT
 * Fallback interaction is a form post, with the JWT stored server-side and a `session_id` returned to the client in the response cookie
 * The intent of having a fallback interaction mode is to be able to support non-javascript users 
   and users of browsers that do not provide local storage
 * Once the client has a JWT or `session_id` cookie, this is passed to the app the client wishes to be served by.
 * If necessary, the app contacts auth to exchange the `session_id` for a JWT
 * The app requests public keys from auth in order to verify the integrity of the JWT and, if the signature is valid, 
   provides service according to the autorisations contained in the token (user and AD roles).

## Questions

 * Should we use a single key-pair, rather than an ephemeral design, which may necessitate key-management infrastructure?
 * Alternatively, should we use ephemeral keys, which requires all instances over time to be able to access each others' public keys
 * What key-rotation strategy is appropriate?
 * Do we have a risk of replay attacks? If so:
   * How short or long lived should JWT tokens be?
   * How will clients refresh JWT tokens (if necessary)
 * Are there any use-cases that JWT does not provide for?

NB: in the case of Securities and Discharges, the appropriate level of protection is likely to be lower, 
because the sensitive part of the transaction is protected by the physical smart-card. 
The risk we are protecting against is "creation of an application" - 
it should not be possible to even submit the application for processing without a signed deed. 

