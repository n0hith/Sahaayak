# Sahaayak

Sahaayak (“helper”) is a mobile-first hackathon prototype for benefit discovery and application readiness. It is deliberately independent: it uses only fictional local data and does not represent, connect to, or submit anything to a government service.

## Run locally

```bash
npm install
npm run dev
```

For a production build check:

```bash
npm run build
```

## Demo journey

1. Choose **Check what may fit me** from the welcome screen.
2. Select **Use demo profile** for a repeatable path, or answer the five brief profile steps.
3. Review strong, possible, and explore-more fictional scheme results. Each makes uncertainty clear.
4. Open a scheme, compare options, and create a preparation plan.
5. Complete local checklist items, use the deterministic explainer, and print if useful.
6. Choose a fictional support route and create a synthetic `SHY-2026-xxxxx` readiness reference. No application is sent.

The demo profile is a 20-year-old town resident in undergraduate education who is also seeking training, has household income of ₹1.5–3 lakh/year, and has identity/education records but not an income certificate. It intentionally produces both strong and incomplete/possible matches.

## Mock data and privacy policy

- Every scheme is fictional, visibly labelled “Demo scheme”, and stored in [`src/data/schemes.ts`](src/data/schemes.ts).
- The app uses no government logos, emblems, official branding, APIs, scraping, uploads, sign-in, or network calls for its flow.
- It asks only broad matching questions. It never asks for names, phone numbers, precise addresses, Aadhaar, bank details, passwords, OTPs, or document uploads.
- Browser `localStorage` keeps the selected profile, plan completion, low-data preference, and synthetic reference on that device only. Clear browser storage to reset it.

## AI role and deterministic demo mode

[`src/lib/explanations.ts`](src/lib/explanations.ts) is the assistant’s deterministic template layer. It converts selected profile information and structured fictional rules into a top-three plain-language summary, personal fit explanation, contextual checklist, and short answers to common preparation questions. It never inspects documents or calls a provider.

This provides a dependable no-key demo. In a production version, a reviewed privacy-preserving AI service could be optional and consented; the structured rule engine should remain the source of truth.

## Code structure

```text
src/
  data/schemes.ts       six fictional schemes and structured eligibility rules
  lib/eligibility.ts    deterministic matching, labels, demo profile
  lib/explanations.ts   deterministic explanations and checklist generation
  components/           screen and shared UI components
  App.tsx               navigation and localStorage state
  styles.css            mobile-first visual system and print styling
```

## Assumptions, limitations, and scale

- Conditions, values, availability, time estimates, processes, and document lists are examples—not current rules or legal guidance.
- A “strong match” means selected answers meet all mock rules and example documents are marked available. It is never approval or a guarantee.
- A “possible match” means a document is not marked available. “More information needed” means an eligibility answer is unknown. Conflicting schemes remain under “Explore more”.
- English and Hindi cover core navigation and demo actions; longer explanatory content is primarily English. The layout is designed to support longer Hindi labels.
- Low-data mode removes decorative effects and animations. There are no images or data-heavy feeds.

For a real deployment, retain the separation of reviewed, versioned scheme data; a transparent rule engine with recorded match reasons; consented encrypted storage; language/accessibility review; and independently verified official-channel links. Current official information must be maintained by accountable human reviewers.
