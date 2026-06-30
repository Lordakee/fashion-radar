# Stage 242 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

1. **JSON wrapper key tolerance incomplete** — Plan mentions handling list vs `{"tweets": [...]}`, but Xiaohongshu checks multiple wrapper keys ("data", "notes", "items", "feeds", "results"). Twitter CLI may use "data", "results", or "statuses" (classic Twitter API term). Recommend checking `("tweets", "data", "results", "statuses", "items")` to match the tolerant pattern established by xiaohongshu:220-225.

2. **Auth error keywords could be broader** — Plan specifies "login/cookie/auth/401" but Instagram also checks "forbidden" and "private". Twitter may return "403", "unauthorized", "suspended", or "rate limit". Recommend keyword list: `("login", "cookie", "auth", "401", "403", "unauthorized", "forbidden", "rate limit")` for more robust classification.

3. **twitter_cli_path precedence unclear** — Plan says "shutil.which('twitter') or TwitterSourceSettings.twitter_cli_path" but doesn't specify order. Instagram has `instaloader_path` setting that's never used in code (source.py:70 vs instagram.py). Ensure implementation checks `twitter_cli_path` first (if set), then falls back to `shutil.which("twitter")` — explicit path should override discovery.

## Nits

1. **Timeout value unspecified** — "bounded timeout" mentioned but no value given. Xiaohongshu uses `source.http.timeout_seconds` (line 156). Clarify whether Twitter subprocess should use same, or a different value (subprocess calls may need longer timeout than HTTP).

2. **URL format ambiguous** — "url from tweet id+user" doesn't specify format. Should be explicit: `https://x.com/{username}/status/{tweet_id}` (or twitter.com — clarify current domain preference given the twitter.com→x.com transition).

3. **Empty text fallback missing** — Instagram has `f"Instagram post {shortcode}"` title fallback (line 124). Specify Twitter's fallback when text is empty/missing: `f"Tweet {tweet_id}"` or similar.

4. **Shell escaping safety** — Command shows `twitter search "<query>"`. Recommend using subprocess argument list (not shell=True) to avoid injection risk with queries containing quotes/backticks/semicolons. Pattern: `["twitter", "search", query, "-n", str(max_tweets), "--json"]`.

5. **User field nested extraction** — Plan mentions user might be "str or `{"screen_name": ...}`" but doesn't specify nested extraction logic. Clarify pattern: check if dict → extract key, else use as-is (similar to Xiaohongshu's nested field handling).

## Summary

Solid plan following established collector patterns (fail-closed, bounded, injectable runner for tests, delegated auth). Subprocess design is sound for offline testing. Main gaps are JSON wrapper key tolerance (should check more wrapper names beyond "tweets") and auth error keyword coverage (should match Instagram's breadth). The twitter_cli_path override must actually be used in code (Instagram's instaloader_path isn't, which is a latent inconsistency). Nits are mostly documentation clarity — explicit timeout value, URL format, and shell escaping approach.
