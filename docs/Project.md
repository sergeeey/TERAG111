# Project Overview

## Mission
Provide an immersive 3D and voice-enabled interface to inspect and interact with TERAG reasoning, exposing metrics and graphs with graceful degradation.

## Architecture
- React + Vite SPA with provider pattern
- 3D via React Three Fiber and Drei
- API integration in `src/services/terag-api.ts`
- Optional local RAG/Neo4j tooling (Python) for code intelligence

## Traceability
- Minimal client-side trace utility in `src/utils/trace.ts`
- Recommend backend audit-trail with hashes and source lineage

## Testing
- Vitest configured; unit tests for `src/services/terag-api.ts`







