# Build Plan

## Chapter 1: Conversational Input Layer
- [x] Task 1: Set up app.py as the Streamlit entry point
- [x] Task 2: Find and embed a music Lottie animation (vinyl or equalizer)
- [x] Task 3: Add text input with placeholder and submit button
- [x] Task 4: Store submitted input in session state and echo it back

## Chapter 2: LLM Agent — Interpret Input
- [x] Task 1: Connect OpenRouter API
- [x] Task 2: Send user input to LLM, extract genre/mood/energy as structured output
- [x] Task 3: Display extracted attributes back to user

## Chapter 3: MusicBrainz Retriever
- [x] Task 1: Query MusicBrainz using extracted attributes
- [x] Task 2: Return a list of candidate songs
- [x] Task 3: Handle rate limiting and empty results

## Chapter 4: Scoring Engine
- [x] Task 1: Adapt Module 3 scoring logic to work with MusicBrainz data
- [x] Task 2: Rank and filter candidate songs

## Chapter 5: Response Generator
- [x] Task 1: Send ranked songs to LLM for plain English explanation
- [x] Task 2: Display recommendations + explanations in UI
- [x] Task 3: Add follow-up input for refinement loop

## Chapter 6: Logger + Guardrails
- [x] Task 1: Add logging throughout the pipeline
- [x] Task 2: Add input validation and error handling

## Chapter 7: Visual Polish
- [x] Task 1: Replace "Reading your vibe..." spinner with full-width HTML Canvas orbital animation (stars, gold sphere, 4 tilted rings, glowing trailing dots, breath pulse, fade text)

---

## What We Built — Chapter Recap

**Chapter 1: Conversational Input Layer**
The front door of the app. Instead of dropdowns or sliders, the user gets a single open text field — describe how you're feeling in plain English, hit submit, and the app echoes it back so you know it was heard. This chapter establishes the entire visual identity: dark background, gold accents, Playfair Display headings, and a CSS equalizer animation that plays while the system works. Every design decision made here carries through all six chapters.

**Chapter 2: LLM Agent — Interpret Input**
This is where the intelligence starts. The user's plain English description is sent to a language model via OpenRouter, which extracts structured musical intent: genre, mood, energy level, valence, tempo, acoustic preference, and search keywords. The result is shown back to the user in a "What I Heard" card so the system is transparent about what it understood — not a black box.

**Chapter 3: MusicBrainz Retriever**
Instead of a hardcoded song list, this chapter reaches out to MusicBrainz — a real, open music catalog with millions of recordings. The extracted mood profile becomes a search query (tags like `jazz`, `melancholic`, `late night`) and the system retrieves up to 25 real candidate songs. Rate limiting and error handling are built in so the app never crashes on a slow or failed network request.

**Chapter 4: Scoring Engine**
Twenty-five candidates is too many to show a user — this chapter narrows it to the best five. It adapts the scoring logic from Module 3: each song earns points for catalog relevance, genre match, mood match, and keyword overlap. Two diversity rules prevent boring results: the Module 3 genre+mood rule, and a new artist deduplication pass that ensures no artist appears twice in the top five.

**Chapter 5: Response Generator**
The system's voice. Once the top five are ranked, a second LLM call writes a short, warm paragraph explaining why these specific songs fit what the user described — mentioning each song by name and connecting it to the user's actual words. Below the explanation, a refinement input lets the user push back, narrow down, or shift the mood entirely, restarting the full pipeline with their new description.

**Chapter 6: Logger + Guardrails**
The layer that makes the system trustworthy. Every pipeline run writes a structured log to `logs/app.log`: what the user said, what the LLM extracted, how many songs were retrieved, the final top five with scores, and any errors. Input guardrails run before the LLM is ever called — rejecting empty inputs, gibberish, or keyboard mashing with a friendly message instead of a crash. API failures from OpenRouter or MusicBrainz are caught and surfaced as readable UI messages, never as Python tracebacks.

---

## Future Improvements

- **Artist diversity:** Extend the deduplication rule to catch partial name matches — e.g. `"Axela"` vs `"Axela & JAX"` currently count as different artists and both slip through.
- **Audio features:** Integrate a source that provides per-song energy and valence scores (Spotify API is the obvious candidate) to replace the tag-overlap approximation, which rarely fires because MusicBrainz tags are genre-focused, not mood-focused.
- **Playlist export:** Let users save their top 5 as a shareable or downloadable list — a simple text export or a link they can send to a friend.
- **User history:** Remember past searches within a session so the refinement loop can reference earlier queries and make progressively better suggestions rather than starting from scratch each time.
- **Expanded catalog:** Increase MusicBrainz retrieval beyond 25 candidates — niche genres and lesser-known artists are underrepresented at 25 results; 50–100 would meaningfully improve coverage.
- **Model Card update:** Document the new agentic system — its two LLM calls, the RAG layer, what it can and can't do, where it might fail, and responsible use guidance, replacing the Module 3 model card with one that reflects the current architecture.
