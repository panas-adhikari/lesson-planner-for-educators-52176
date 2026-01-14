# Supabase (optional) integration scaffolding

This project lists Supabase as a potential 3rd-party service, but the Lesson Planner app is fully functional without Supabase credentials.

## If you want to add Supabase later

You can use Supabase for:
- Hosted Postgres (instead of SQLite)
- Auth (instead of Django sessions)
- File storage (lesson attachments)

## Suggested variables (do not add secrets to git)

Backend:
- SUPABASE_URL=
- SUPABASE_ANON_KEY=

Frontend:
- REACT_APP_SUPABASE_URL=
- REACT_APP_SUPABASE_ANON_KEY=

No code currently depends on these values.
