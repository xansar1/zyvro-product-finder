# ZYVRO AI — Product Research Studio V2

A **transparent** product discovery / unit economics **research demo**, made with Streamlit, Python, and Pandas.

**Public demo mode:** 70 deterministically generated **fictional** items. No real Amazon prices, rankings, reviews, demand, availability, or links are implied. These are placeholders for user interface testing.

**Optional provider mode:** server-side Rainforest API key can fetch actual Amazon *search-result records at request time*. Returned product metadata is not verified inventory, sales or future demand, and may be incomplete or sponsored.

The **Opportunity score (0–100) is a handcrafted heuristic, NOT trained AI, forecast, guaranteed profit or an Amazon sales prediction**. Details and weights are shown in the dashboard. Review-count density is only a proxy for listing evidence, not a measure of actual competition. All unit economics use user-entered hypothetical assumptions and ignore taxes and uncertain returns unless included by the user.

## Features
- Four working sections: Discovery, Compare, Unit Economics, Methodology.
- Candidate search, filter, sort, evidence disclosure, reusable real-data adapter and defensively parsed provider URLs.
- Interactive tables and charts, simple breakdown of every ranking component.
- Scenario-based gross/unit margin calculations (NOT predicted sales).
- CSV export with source label.
- Completely offline-capable fictional demo mode.

## Run locally

```bash
bash scripts/start_mac.sh
```

Or install `requirements.txt` then run `streamlit run app.py`. Tests: `pip install -r requirements-dev.txt && pytest -q`.

## Optional live provider mode

1. Get a Rainforest API account and **new key**. If your earlier key was committed to public GitHub, **revoke/rotate it** at the provider before reusing the integration. Removing `.env` from a branch does NOT erase it from Git history.
2. Set `RAINFOREST_API_KEY` in Streamlit Community Cloud → App settings → Secrets (never in code, logs, `.env` tracked files, or URL). For local use `export RAINFOREST_API_KEY='...'` in the shell or create local `.streamlit/secrets.toml` from the example (ignored in Git).
3. In sidebar choose *Rainforest API results*. API calls may use your paid quota. Provider credentials are never sent to the browser directly.

## Streamlit Community Cloud

Deploy the `main` or `zyvro-v2-safe-demo` branch using `app.py` as the main file. The public demo works **without keys**. When the branch is reviewed and merged, the live app may redeploy automatically if connected to the same repository/branch.

## Security

**Legacy source warning**: the old repository exposed `.env` and used fabricated listing metrics and fake CTR/ROAS estimates. This V2 has no embedded key and no fabricated live claims. Make sure to remove all real credentials and revoke old keys before publishing. A separate Git history rewrite is required if you want the historical secret removed from the original repository's commit history.
