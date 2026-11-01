# SPUTNIK — public actor role mapping

SPUTNIK now preserves the author field from RSS/Atom entries and can attach a
public actor category only when the operator explicitly configures it.

Set the GitHub Actions/Render environment variable `SPUTNIK_ACTOR_ROLE_MAP`
to a JSON object. Example:

```json
{
  "Public Name As Shown In Feed": "family",
  "Public Adviser Name": "adviser",
  "Public Cabinet Official": "cabinet",
  "Public Ally": "ally"
}
```

Allowed role values: `president`, `administration`, `cabinet`, `family`,
`adviser`, `advisor`, `ally`, `associate`, `friend`, `entourage`.

Names must match the public feed author field exactly after basic punctuation
and case normalization. Unknown names are not assigned a relationship.
Do not add private individuals or infer a relationship from proximity, rumor,
photographs, or unverified social posts.

The model still requires a dated, item-level public RSS/Atom entry with a
permalink and a concrete policy/event rule. Actor weighting affects only the
priority score; it does not establish truth, motive, insider activity, or a
trade direction by itself. SEC/OGE disclosures remain separate public-record
evidence. All outputs are EARLY_BIAS hypotheses, PAPER only, no orders.
