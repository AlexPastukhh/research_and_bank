# ChatGPT ↔ user ↔ application interaction scenarios (draft)

> **Статус с 2026-10-10: историческая справка.** Прежние ценности и evidence сохранены; новое развитие отделено от runtime. Актуальный документ: [AI_WORKFLOW.md](../docs/AI_WORKFLOW.md). Нижний текст сохраняет прежний контекст, не задаёт текущую очередь или закрытый enum типов.

These scenarios are product-level journeys, not canonical UC definitions. They are intended to expose who does what and which reusable capabilities are missing.

## Responsibility split

### User
Provides goals, preferences, examples, corrections, selections, confirmations and domain judgment.

### ChatGPT / research agent
Interprets intent, retrieves context, proposes lenses/recipes, performs semantic reasoning, selects appropriate registered capabilities, explains results, asks for confirmation at meaningful boundaries, and records interpretations separately from raw facts.

### Application
Owns persistent state, deterministic commands, authorization, scheduling, bank/search UI, tables/charts, history, collections, evidence views, source/tool management, query projections and background execution.

### External tools/sources
Acquire/process data under explicit source/tool contracts. They do not become canonical truth by themselves.

---

## S01 — Save anything

**User:** shares an image, URL, game, app, file, article or note and says “save this”.

**ChatGPT:** infers/asks only necessary metadata; suggests entity links or tags without forcing research.

**Application:** persists Asset/Entity/Annotation/BankItem, provenance and saved time; computes allowed derived representations asynchronously or explicitly.

**Result:** item exists independently of any project and can later participate in search/research/watch.

---

## S02 — Find visually/semantically similar images

**User:** “Find things similar to this saved image.”

**ChatGPT:** clarifies/infers similarity intent: near-duplicate, visual composition, style, semantic content, etc.

**Application:** retrieves representation(s), searches bank first, optionally executes external image/web discovery, ranks/explains matches.

**Result:** user can save selected candidates, build a collection, or start research from them.

---

## S03 — Find games similar by mechanics

**User:** “We analyzed this game; find modern games similar by mechanics, not necessarily art style.”

**ChatGPT:** uses the saved game/entity and mechanics representation; constructs a mechanics-focused lens.

**Application:** hybrid search over bank + approved sources, filters by release date/other constraints, stores new observations and identity links.

**UI:** shows multi-aspect similarity and “why similar” features rather than one opaque score.

---

## S04 — Collection as a search seed

**User:** creates “games with interesting inventory systems” from games, screenshots, videos and notes; asks for more like this collection.

**Application:** creates mixed collection and collection representation/profile.

**ChatGPT:** derives shared traits, distinguishes positive/negative examples, runs internal/external discovery.

**Result:** bank expands based on accumulated taste/knowledge.

---

## S05 — Daily market/opportunity research

**User:** saves a lens: “work/tasks matching my interests and skills”.

**Run:** repeated daily.

**System:** discovers paid-work/opportunity entities, normalizes, resolves identity, records pay/demand/requirements/lifecycle observations, compares with prior runs.

**UI:** current state, new/changed/disappeared/reopened, payout distributions, trends, coverage, personal-fit projection.

**ChatGPT:** answers “what changed today?”, “what is worth attention?”, “why?”, without treating vacancies as the universal product model.

---

## S06 — News/topic watch

**User:** “Track AI agent regulation using my trusted sources plus broader discovery.”

**System:** repeatedly gathers stories/events, clusters duplicate coverage into underlying story/event entities, tracks source diversity and chronology.

**ChatGPT:** distinguishes new event vs more coverage of known event, explains source disagreement and limitations.

---

## S07 — Watch a saved entity

**User:** “Watch this game.”

**Application:** creates a Watch for price, player count, reviews, release/update events and selected sources/cadence.

**UI:** timeline, changes, alerts and trend views.

**ChatGPT:** can answer “what changed since I saved it?” with linked evidence.

---

## S08 — Watch a query or similarity neighborhood

**User:** “Tell me when something new appears that is similar to these three games.”

**System:** stores the query/lens + representation profile as the monitored subject and periodically reruns discovery.

**Result:** alerts distinguish genuinely new items from known/reobserved ones.

---

## S09 — Source reuse

**User:** “Save this subreddit and these sites as my indie-game sources.”

**Application:** registers Sources and reusable SourceRoutes with roles/priorities/access methods.

Later **User:** “Search my sources first.”

**ChatGPT:** selects saved source group; application executes registered routes/tools and preserves route/tool lineage.

---

## S10 — Research recipe reuse

**User:** “Every week rerun the same app-market research.”

**System:** saves Lens + ResearchRecipe and creates a Watch that owns the weekly cadence; each execution compiles an immutable RunSpec with resolved source/tool/method versions. Runs accumulate into the same bank instead of isolated reports.

**UI:** current state + historical comparison + method/comparability warnings.

---

## S11 — Historical question without refresh

**User:** “What did we know about this market two months ago?”

**Application:** queries historical projections/observations only.

**ChatGPT:** explains known-at-the-time evidence; does not silently run fresh research. If the requested historical projection is unavailable, returns that limitation explicitly.

---

## S12 — Backfill discovers an older fact

Today the system finds a source stating that an event happened last week.

**System:** records event/valid time separately from capture/system time.

**UI/ChatGPT:** can distinguish “event happened then” from “we learned it today”.

---

## S13 — Entity identity correction

**System:** suggests two records are the same game/company/person.

**User:** confirms merge or rejects/splits.

**Application:** preserves merge/split history and reindexes derived representations/results without destroying source observations.

---

## S14 — Research from saved bank items

**User:** selects 10 saved games: “research what these have in common and find patterns I may have missed.”

**ChatGPT:** creates a lens, selects domain analysis methods, forms hypotheses/clusters.

**Application:** reads bank objects, computes/version-controls derived features, stores analysis/result products linked back to original items.

---

## S15 — Personal counterfactual

**User:** “If I learn Blender, what new kinds of paid work become realistic for me?”

**Application:** reprojects existing opportunity bank against a modified user profile without changing raw observations.

**ChatGPT:** explains opportunity expansion, assumptions and missing evidence.

---

## S16 — Why / provenance drill-down

**User:** clicks/asks “Why do you say this game is growing?”

**UI:** shows claim/result → metrics → observations → source captures → source routes/tools/run/method versions.

**ChatGPT:** summarizes the evidence and points out coverage/source disagreement.

---

---

## S17 — Reproduce an old search result exactly

**User:** “What exactly did the 5 October mechanics-similarity run return, and why was Game A first?”

**Application:** loads the immutable RunSpec + ResultSet/ResultOccurrences from that run rather than recomputing with current representations.

**ChatGPT/UI:** show historical membership/rank, similarity dimensions/reasons, model/profile versions and provenance; optionally compare with today’s rerun as a separate result set.

**Result:** historical research output remains inspectable even after rankers/embeddings evolve.

---

## S18 — Watch compiles without ambiguous ownership

**User:** saves a games Lens, chooses a SourcePolicy, selects a Recipe, then schedules a Watch.

**Application:** compiles an immutable RunSpec. Lens owns semantic filters/ranking intent, SourcePolicy/Routes own source boundary/access, Recipe owns methods/tools, Watch owns cadence/alerts.

If two components attempt to own a non-overrideable field, compilation fails before external acquisition and the UI explains the conflict.

**Result:** repeated research is reproducible and configuration drift is visible.

---

## S19 — AI note is not automatically independent evidence

**User:** previously saved an AI-generated summary, then later researches the same claim.

**Application:** retrieves the note as useful context but preserves its epistemic class and `derived_from` lineage.

**Research/ChatGPT:** may cite the original independent sources behind the summary, but does not count rediscovering the summary itself as a second independent confirmation.

**Result:** arbitrary Bank reuse does not create self-confirming evidence loops.

---

## UI surface draft

Possible primary navigation:

```text
Bank
Discover
Research
Watch
Current State
Changes
Trends
Collections
Sources
Tools
History
Research Health
```

Chat remains an orchestration/explanation surface, not the only way to inspect persistent state.
