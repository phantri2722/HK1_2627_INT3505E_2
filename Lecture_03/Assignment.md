# Review of Spotify Web API — Criteria 1 & 2

## Criteria 1: Resources should be nouns
Spotify strictly follows this criteria. Every resources (you can find it in Spotify API References) are nouns.

For example: /players, /artists, /me, /albums, ....

## Criteria 2: Naming should be consistent (Lowercase, kebab-case path; snake_case query; plurals for collection)
Here is one example API:
https://api.spotify.com/v1/me/shows?offset=0&limit=20 that shows Spotify compliants the lowercase, snake_case query and plurals for collection rules. You can see a reasonable exception /me which is singular (not plural), it represents one current actor rather than a collection.

Another example is: 
https://api.spotify.com/v1/me/player/currently-playing that shows that Spotify compliants the kebab rule.
