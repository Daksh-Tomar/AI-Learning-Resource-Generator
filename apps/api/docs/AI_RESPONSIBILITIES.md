# AI Responsibilities

In LearnLens, the role of LLMs (Gemini) is strictly scoped to natural language tasks to maintain system determinism and reliability.

## Allowed AI Operations
1. **Conversational Interview**: Adapting to user inputs to gently guide them towards defining a learning profile.
2. **Profile Extraction**: Using Structured Outputs to map natural language conversation history into a strict `LearnerProfileSchema`.
3. **Search Plan Generation**: Converting a learner profile into structured intent (search queries and keywords).
4. **Content Summarization**: (Future) Summarizing video transcripts or articles.

## Prohibited AI Operations
1. **Database Routing**: The LLM must not directly write SQL or decide which database tables to mutate.
2. **Scoring and Ranking**: The LLM will not assign final recommendation scores. This is handled deterministically via Python algorithms (e.g. `min_max_normalize`).
3. **External API Calls**: The LLM does not fetch data from YouTube or Coursera directly. It outputs search queries which the backend executes.
