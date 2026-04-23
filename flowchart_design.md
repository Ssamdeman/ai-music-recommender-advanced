# Step 4: Data Flow Visualization

## Mental Map (plain text)

```
INPUT                  PROCESS                          OUTPUT
─────────────────      ──────────────────────────────   ─────────────────
user_prefs dict   ──►  Load songs.csv into a list   
songs.csv         ──►  │                            
                        ▼                            
                        FOR each song in the list:   
                          score = 0                  
                          +2.0  if genre matches     
                          +1.0  if mood matches      
                          +0–3  energy proximity     
                          +0–2  valence proximity    
                          +0–1  acousticness fit     
                          store (song, score)        
                        END LOOP                     
                        │                            
                        ▼                            
                        Drop scores < threshold      
                        Sort descending by score     
                        Apply diversity rule         ──►  Top 5 recommendations
                                                          with explanations
```

---

## Mermaid.js Flowchart

```mermaid
flowchart TD
    A([🎵 START]) --> B

    subgraph INPUT["① INPUT"]
        B["user_prefs dict\n─────────────\ngenre: rock\nmood: intense\ntarget_energy: 0.88\ntarget_valence: 0.50\nlikes_acoustic: False"]
        C["songs.csv\n─────────────\n18 songs with\nenergy, valence,\nacousticness,\ngenre, mood…"]
    end

    B --> D
    C --> D

    subgraph PROCESS["② PROCESS — The Scoring Loop"]
        D["load_songs(csv_path)\n→ list of song dicts"] --> E

        E{{"FOR each song\nin the list"}}

        E --> F["score_song(user_prefs, song)\n─────────────────────────\n+2.0  genre match?\n+1.0  mood match?\n+0–3  energy proximity\n+0–2  valence proximity\n+0–1  acousticness fit\n─────────────────────────\nreturn (score, reasons)"]

        F --> G["Append\n(song, score, reasons)\nto results list"]

        G --> H{More songs?}
        H -- Yes --> E
        H -- No  --> I
    end

    subgraph RANKING["③ OUTPUT — Ranking"]
        I["Drop songs where\nscore < threshold (40)"]
        I --> J["Sort by score\ndescending"]
        J --> K{"Top 2 share\ngenre AND mood?"}
        K -- Yes --> L["Force 3rd slot =\nhighest scorer that\nbreaks genre OR mood"]
        K -- No  --> M
        L --> M["Return top K\n(default: 5)"]
    end

    M --> N([📋 Recommendations\nwith explanations])

    style INPUT    fill:#dbeafe,stroke:#3b82f6
    style PROCESS  fill:#dcfce7,stroke:#22c55e
    style RANKING  fill:#fef9c3,stroke:#eab308
```

---

## How a Single Song Moves Through the System

Using **"Storm Runner"** (rock · intense · energy=0.91 · valence=0.48 · acousticness=0.10)
against the user profile (rock · intense · target_energy=0.88 · target_valence=0.50 · likes_acoustic=False):

| Step | Action | Running Score |
|---|---|---|
| Load | Song read from songs.csv into a dict | — |
| Genre check | `"rock" == "rock"` → +2.0 | **2.0** |
| Mood check | `"intense" == "intense"` → +1.0 | **3.0** |
| Energy proximity | `(1 - \|0.91 - 0.88\|) × 3.0 = 0.97 × 3.0` → +2.91 | **5.91** |
| Valence proximity | `(1 - \|0.48 - 0.50\|) × 2.0 = 0.98 × 2.0` → +1.96 | **7.87** |
| Acousticness fit | `likes_acoustic=False`, song=0.10 (low) → +1.0 | **8.87** |
| Threshold check | 8.87 ≥ threshold → **keep** | ✅ |
| Sort | Placed in ranked list by score | — |
| Return | Appears in top 5 | **Recommended** |
