Project setup

- Create venv: `python3 -m venv .venv`
- Activate (bash/zsh): `source .venv/bin/activate`
- Activate (fish): `source .venv/bin/activate.fish`
- Activate (Windows PowerShell): `.venv\\Scripts\\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

Quick check

Run: `python -c "import dynamiq; print(dynamiq.__version__)"`

Environment

- Create `.env` at project root with: `OPENAI_KEY=your-key-here`
- `.env` is gitignored.
- The app loads `.env` in `app/main.py` and uses `OPENAI_KEY`.
