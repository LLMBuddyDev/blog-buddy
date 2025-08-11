# BlogBuddy Cloud

Streamlit app that generates long- and short-form blogs with helpful linking to technical resources.

## Quickstart

1) Install deps

```
pip install -r requirements.txt
```

2) Provide API keys (either method works)

- Environment variables

```
export OPENAI_API_KEY="..."
export GOOGLE_API_KEY="..."
export GOOGLE_CX="..."
```

- Streamlit secrets (local dev)

```
mkdir -p .streamlit
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# edit .streamlit/secrets.toml with your keys
```

3) Run

```
streamlit run app.py
```

On first run, you'll be asked for a Workspace Key. Use any memorable string; it keys and isolates your saved company contexts under `user_contexts/`.

## Deploy to Streamlit Community Cloud (recommended)

1. Push this repo to GitHub
2. Create an app in Streamlit Cloud and point it at this repo
3. In the app settings, add secrets:

```toml
[openai]
api_key = "your_openai_api_key"

[google]
api_key = "your_google_api_key"
cx = "your_google_cx"
```

## Deploy to Heroku

1) Create app and set config vars

```
heroku create your-blogbuddy-app
heroku config:set OPENAI_API_KEY=... GOOGLE_API_KEY=... GOOGLE_CX=...
```

2) Deploy

```
git push heroku main
```

Procfile is included and will run Streamlit on the assigned port.

## Notes

- Secrets are loaded from env vars or Streamlit secrets via `company_config.py`
- Keep `blog_prompt_template.txt` and `technical_links.json` in the repo root for the app to find them
- Company contexts are stored per workspace key in `user_contexts/` (ignored by Git)

