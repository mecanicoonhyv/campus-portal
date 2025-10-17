# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: Django REST API. `config/` holds settings, `apps/` hosts domain modules (users, academics, assessments, attendance, library, services, facilities). Management commands live alongside `manage.py`.
- `frontend/`: Vue 3/Vite SPA. `src/views/` separated by role, `src/stores/` for Pinia stores, `src/services/api.js` configures Axios with JWT refresh.
- `data/`: CSV fixtures imported by `python manage.py import_data`. Update files here and rerun the command when seeding new data.

## Build, Test, and Development Commands
```bash
# Backend setup
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate && python manage.py import_data
python manage.py runserver  # http://localhost:8000

# Frontend setup
cd ../frontend
npm install
cp .env.example .env
npm run dev    # http://localhost:5173
npm run build && npm run preview
```
Run `backend/build.sh` during Render builds; comment the import step after the first deploy.

## Coding Style & Naming Conventions
- Follow PEP 8: 4-space indents, 79-character lines, descriptive docstrings for complex serializers/views.
- Use snake_case for Python functions and variables, PascalCase for Django models/serializers; group imports as stdlib, third-party, local.
- In Vue, keep component files PascalCase (`Dashboard.vue`), stores lowercase (`auth.js`), and favor composition API + script setup syntax already in `src/views`.

## Testing Guidelines
- Add Django tests beside each app in `backend/apps/<module>/tests/`; use `APITestCase` for API endpoints and seed data via factories instead of the CSV importer.
- Run `python manage.py test` before committing; integrate coverage measurement if suites grow.
- Frontend currently lacks automated tests—document manual verification in PRs and ensure `npm run build` succeeds.

## Commit & Pull Request Guidelines
- Repository history is not bundled, so adopt short imperative commits such as `backend: fix attendance serializer validation`. Reference affected app or view.
- PRs should include: summary of changes, linked issue or context, setup notes (migrations, data imports), and screenshots or cURL samples for UI/API updates.
- Ensure both servers run locally after the change and mention which commands you executed.

## Security & Configuration Tips
- Never commit `.env`; base new settings on the provided examples.
- Update `CORS_ALLOWED_ORIGINS` and `VITE_API_BASE_URL` when changing deployment URLs, and rotate `SECRET_KEY` before production launches.
