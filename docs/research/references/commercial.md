# References — Commercial and Consumer Products

---

## Machine translation

| Product | Tigrinya support | Notes |
| --- | --- | --- |
| **Google Translate** | Yes | `[reported]` outperformed NLLB on accuracy and fluency in a comparative study. **The translation quality bar to beat.** |
| **Microsoft Translator** | Yes | Evaluated in the AfricaNLP error analysis |
| **Lesan.ai** | Yes | Ethiopian-language MT specialist |

**Common failure modes** `[reported]` under MQM-DQF: **mistranslation** and
**omission** dominate across all three.

**Strategic note:** Google Translate is a **baseline to measure against**, not a
dependency (see R-005). This is why translation is excluded from the minimum
viable platform (DEC-006).

## Input methods and consumer tools

| Product | Platforms | Features |
| --- | --- | --- |
| **GeezIME** | iOS, macOS, Android, Windows, Web | Ge'ez keyboard with **word suggestions** for Tigrinya, Tigre, Blin, Amharic. User-extensible dictionary. The most established. |
| **GeezKTB** | Web | Free Ge'ez keyboard; advertises AI chatbot dictionary, voice input, translation hub, **grammar check** |
| **Mesmer Tigrinya Geez Keyboard** | Mac, Windows, iOS, Android | Native Ge'ez typing |
| **GeezWord** | Windows | Ge'ez script in MS Office, Adobe Illustrator/Photoshop/InDesign |
| **Lexilogos Tigrinya Keyboard** | Web | Online Ge'ez typing utility |

---

## Why this matters for our scope

**1. The input problem is solved.** Multiple mature keyboard products exist.
This supports **N-2** — we must not build consumer input tools.

**2. These products are our most likely first users.** Each has independently
re-solved word suggestion and dictionary lookup. Several advertise features
(grammar check, dictionary, translation) that a shared infrastructure layer
would serve better than each doing it alone. **This duplication is the clearest
demand signal found for DEC-002.**

**3. GeezKTB's "grammar check" claim needs assessment.** If a usable Tigrinya
grammar checker already exists commercially, that changes our priority for the
grammar service. **Not yet evaluated** — flagged for `01_ecosystem` follow-up.

**4. Nobody offers an API.** None of these products expose Tigrinya language
capability as developer infrastructure. That remains the gap.
