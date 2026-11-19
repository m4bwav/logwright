# Privacy method

Default for every game: opt-in, local file only, no network code, no persistent device or advertising ID.

## Children (under 13)

COPPA applies when a service directed to children, or one that knows a user is under 13, collects personal information online. Persistent identifiers used to recognise a user over time count as personal information. A local file that never leaves the machine is not online collection. Any upload, account, online crash report or third-party analytics SDK changes that and needs a privacy notice and verifiable parental consent first. So for a child's game: local only, no `iid`, no SDK. `lgw.py privacy <repo> --child` fails on any network send or device ID.

## Before any upload (the owner's decision)

- GDPR: name the lawful basis (consent for analytics), say what is kept and for how long, allow deletion.
- Steam: a game that collects personal data needs a privacy policy linked on its store page.
- Roblox AnalyticsService and Unity Analytics send data to the platform; they are the owner's call under the platform's own consent rules.
- Self-hosted crash triage: GlitchTip accepts the Sentry SDK; the owner creates the instance and DSN.

The agent never creates an account, DSN or endpoint.
