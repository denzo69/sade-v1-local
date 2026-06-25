# Authentication Policy

Local AI Workspace protects the browser UI and API routes with local authentication.

## Principles

- The first user is created locally from the command line.
- Password hashes are stored locally and are not committed to Git.
- Sessions are stored server-side.
- Logout invalidates the active session.
- CSRF protection is required for state-changing browser requests.

## Deployment note

Authentication does not replace transport security. Remote access should use a trusted tunnel or HTTPS. The app should not be exposed directly to the public internet.
