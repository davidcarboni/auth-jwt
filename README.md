# Experimental JWT auth solution

This prototype asks the question "what if there was no OAuth?"

## Rationale

The rationale is as follows:
 * OAuth is designed to allow a third-party service to access your resources on behalf of a user
 * The RoS use case is that users authenticate centrally (a single sign-on) and that this authentication (with associated authorisation information) is trusted by other RoS apps.
 * The other RoS apps need to be able to trust the identity and authorisations that are being asserted by a user.
 * The other RoS apps do not need to access resources owned by the central authentication.
 * Therefore a signed token (e.g. JWT) is both necessary and sufficient for trusted assertion.
 * Not using OAuth could significantly reduce complexity and potential for errors.

## Exceptions

There is one possible exception to be investigated: the Revenue Scotland Service. It is believed that this is making use of "third-party access to resources", which would be consistent with the intent of OAuth.

There is therefore a need to investigate this service and understand whether it is required (transaction volumes are believed to be extremely low) and whether, if it is required, a JWT solution might still meet the need.

## Implementation

The following is a summary of this implementation:

 * An auth component 
 * An example client app
 * The auth component takes in usernames and passwords and returns a JWT signed with a key-pair owned by the auth component
 * The auth component publishes the public key on a rest endpoint
 * Preferred interaction is a json username/password request, with a JWT response, where the client is expected to store the JWT
 * Fallback interaction is a form post, with the JWT stored server-side and a token returned to the client in a cookie on the response
 * The intent of having these two interactions is to be able to support non-javascript users and users of browsers that do not provide local storage
 * The client passes the JWT, or cookie, to the app it wishes to be served by. The app then exchanges the cookie for a JWT if necessary, requests the public key from the auth component, verifies the integrity of the JWT and then provides service according to the autorisations contained in the token (user and AD roles).

## Questions

 * Should we use a single key-pair, which may necessitate key-management infrastructure
 * Alternatively, should we go for ephemeral keys, which requires all instances over time to be able to access each others' public keys
 * What key-rotation strategy is appropriate?
 * Do we have a risk of replay attacks? If so:
   * How short or long lived should JWT tokens be?
   * How will clients refresh JWT tokens (if necessary)
 * Are there any use-cases that JWT does not provide for?

