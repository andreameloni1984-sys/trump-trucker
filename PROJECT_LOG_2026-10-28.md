# Project log — 2026-10-28

## Change: constrain operational asset keyword classification

- SPUTNIK's item-level public-feed domain filter now classifies operational energy headlines around oil, crude, WTI, Brent and supply/refinery catalysts; metals are gold, silver and copper; agriculture is corn, wheat and soybean.
- General macro/political catalyst domains (trade policy, rates, defense, technology and others) remain available for discovery. This change does not remove sources or turn headlines into confirmed trade signals.
- Added regression tests for included/excluded asset terms and retained macro catalyst labels.
- Not deployed or merged. Full test suite still needs to run in CI.
