# T.R.A.C. Interaction Diagram

## Схема взаимодействия компонентов

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TERAG Cognitive Stack                             │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   User Query     │
│   "What caused   │
│   delays?"       │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  T.R.A.C. Layer (Traceable Reasoning Architecture Core)          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Trace Begin │ ──▶ │  Extract    │ ──▶ │  Reasoning │         │
│  │ (trac_trace)│    │  Triplets   │    │  Chain      │         │
│  └──────┬──────┘    │  from KAG   │    │  (CoR)      │         │
│         │           └──────┬───────┘    └─────┬───────┘         │
│         │                  │                  │                 │
│         │                  ▼                  ▼                 │
│         │           ┌─────────────────┐ ┌──────────────┐        │
│         │           │ Get SPO         │ │  Hypothesis  │        │
│         │           │ Triplets        │ │  Formation   │        │
│         │           └─────────────────┘ └──────┬───────┘        │
│         │                                      │                 │
│         │                  ┌───────────────────┘                 │
│         │                  │                                     │
│         ▼                  ▼                                     │
│  ┌─────────────┐    ┌─────────────┐                            │
│  │  Evidence   │ ──▶ │  Generate   │                            │
│  │  Gathering  │    │  Structured │                            │
│  └──────┬──────┘    │  Prompt     │                            │
│         │           └──────┬───────┘                            │
└─────────┼──────────────────┼─────────────────────────────────┘
          │                  │
          │                  ▼
          │           ┌─────────────────┐
          │           │   LLM Layer      │
          │           │  (Ollama Local)   │
          │           └──────┬───────────┘
          │                  │
          │                  ▼
          │           ┌─────────────────┐
          │           │  Generated       │
          │           │  Response        │
          │           └──────┬───────────┘
          │                  │
          │                  ▼
          │           ┌─────────────────┐
          │           │  Validation      │
          │           │  & Enrichment    │
          │           └──────┬───────────┘
          │                  │
          ▼                  │
┌──────────────────────────────────────────────────────────────────┐
│  AI-REPS Layer (Cognitive Resonance Metrics)                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Update RSS │    │  Update COS │    │  Update     │         │
│  │  (Reasoning │    │  (Cognitive │    │  FAITH      │         │
│  │   Stability)│    │   Optimize) │    │  (Feedback) │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                     │
│                            ▼                                     │
│                   ┌──────────────┐                               │
│                   │   Resonance   │                               │
│                   │  Calculation │                               │
│                   └──────┬───────┘                               │
│                          │                                       │
│                          ▼                                       │
│                   ┌──────────────┐                               │
│                   │  Cognitive   │                               │
│                   │  State Update│                               │
│                   └──────┬───────┘                               │
│                          │                                       │
│                          ▼                                       │
│                   ┌──────────────┐                               │
│                   │   Feedback    │                               │
│                   │   to T.R.A.C. │                               │
│                   └───────────────┘                               │
└───────────────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌───────────────────────────────────────────────────────────────────┐
│  Memory Bank (Persistent Storage)                                 │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────┐                │
│  │  Save Complete Trace                         │                │
│  │  {                                           │                │
│  │    trace_id, query, reasoning_steps,        │                │
│  │    final_answer, confidence,                 │                │
│  │    ai_reps_metrics, audit_trail             │                │
│  │  }                                           │                │
│  └──────────────────────────────────────────────┘                │
│                                                                   │
│  ┌──────────────────────────────────────────────┐                │
│  │  Pattern Analysis (Background)              │                │
│  │  - Identify successful chains              │                │
│  │  - Detect error patterns                   │                │
│  │  - Update reasoning rules                   │                │
│  └──────────────────────────────────────────────┘                │
└───────────────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌──────────────────┐
│  Final Response  │
│  + Full Trace    │
│  + Metrics       │
└──────────────────┘
```

---

## Детальный поток данных

### 1. Входной запрос

```
User: "What caused payment delays in 2020?"
       ↓
T.R.A.C. Trace Begin
  - timestamp: 2025-10-26T12:30:45
  - trace_id: trac_abc123
```

### 2. Извлечение контекста (Graph-RAG / KAG)

```
T.R.A.C. → KAG: "Get relevant triplets for payment delays"
       ↓
KAG → ChromaDB: Semantic search "payment delays"
       ↓
ChromaDB → KAG: Returns 12 relevant triplets
       ↓
KAG → OpenSPG Graph: Fetch full triplets with context
       ↓
OpenSPG → T.R.A.C.: 
  - (Payment_Delay, caused_by, COVID_Pandemic)
  - (Payment_Delay, occurred_in, 2020)
  - (Financial_Impact, affected, Payment_Flow)
```

### 3. Reasoning Chain Formation

```
Step 1: Hypothesis Formation
  Input: Query + Retrieved triplets
  Output: "Payment delays related to macro factors in 2020"
  Confidence: 0.85
  
Step 2: Evidence Gathering
  Input: Hypothesis
  Output: 
    - Documents: [financial_report_2020.pdf]
    - Extracts: ["Due to pandemic, cash flow disruptions..."]
    - Triplet IDs: [t_123, t_456]
  Confidence: 0.92
  
Step 3: Logical Inference
  Input: Evidence
  Output: "Delays caused by: pandemic (45%), cash gap (30%), banking (25%)"
  Confidence: 0.88
```

### 4. LLM Generation

```
T.R.A.C. → LLM: Structured Prompt
  {
    "context": "Evidence from 3 documents, 12 triplets",
    "reasoning_steps": [step1, step2, step3],
    "evidence": triplets,
    "query": "What caused payment delays?"
  }
       ↓
LLM → T.R.A.C.: Generated Answer
  "Based on the financial documents for 2020, payment delays 
   were primarily caused by three factors: (1) the COVID-19 
   pandemic leading to economic disruptions (45%), (2) cash 
   flow gaps in operations (30%), and (3) banking system 
   delays (25%)."
```

### 5. Validation & Enrichment

```
T.R.A.C. Validation:
  - Check logic consistency: ✅ Pass
  - Verify sources: ✅ All cited
  - Calculate confidence: 0.88
  
T.R.A.C. Enrichment:
  - Add triplet references
  - Add document citations
  - Add reasoning trace
```

### 6. AI-REPS Update

```
T.R.A.C. → AI-REPS: Reasoning Quality Metrics
  {
    "rss": 0.92,        // Reasoning Stability Score
    "cos": 0.89,        // Cognitive Optimization
    "faith": 0.91,      // Feedback Integration
    "resonance": 0.87   // Phase Resonance
  }
       ↓
AI-REPS → T.R.A.C.: Updated Cognitive State
  {
    "target_rss": 0.90,    // Adjust for consistency
    "target_cos": 0.91,    // Optimize cognitive load
    "phase": 0.75          // Current phase alignment
  }
```

### 7. Memory Bank Storage

```
T.R.A.C. → Memory Bank: Save Complete Trace
  {
    "trace_id": "trac_abc123",
    "query": "What caused payment delays in 2020?",
    "reasoning_steps": [step1, step2, step3],
    "final_answer": "Based on...",
    "confidence_score": 0.88,
    "ai_reps_metrics": {
      "rss": 0.92,
      "cos": 0.89,
      "faith": 0.91
    },
    "audit_trail": {
      "source_documents": ["doc1.pdf"],
      "triplet_ids": ["t_123", "t_456"],
      "validation_checks": ["logic: pass", "sources: pass"]
    }
  }
```

### 8. Return to User

```
T.R.A.C. → User: Final Response
  {
    "answer": "Based on...",
    "confidence": 0.88,
    "sources": 3 documents,
    "reasoning_time": 3.2 seconds,
    "trace_available": true
  }
```

---

## Learning Loop (Background Process)

```
Memory Bank → Pattern Analysis
  - Identify successful reasoning chains
  - Detect common error patterns
  - Update reasoning rules
       ↓
AI-REPS → Update Target Metrics
  - Adjust RSS based on success rate
  - Optimize COS for better performance
  - Update Resonance targets
       ↓
T.R.A.C. → Adapt Reasoning Strategy
  - Use successful patterns
  - Avoid error patterns
  - Improve confidence calibration
       ↓
Next Query → Better Reasoning
  - Higher RSS
  - Better COS
  - More consistent answers
```

---

## Визуализация для PowerPoint

### Тип 1: Простая блок-схема

```
[User Query] 
    ↓
[T.R.A.C. Reason]
    ├→ [Extract Triplets] → [Graph-RAG]
    ├→ [Build Chain] → [Hypothesis → Evidence → Inference]
    ├→ [Validate] → [Logic Check]
    └→ [Generate] → [LLM]
          ↓
[AI-REPS Metrics]
    ├→ [Update RSS]
    ├→ [Update COS]
    └→ [Update Resonance]
          ↓
[Return Answer + Trace]
```

### Тип 2: Интерактивная диаграмма

```
┌──────────┐
│  Query   │──┐
└──────────┘  │
              ▼
       ┌──────────────┐
       │   T.R.A.C.  │
       │   Reason    │──┬──▶ [Graph-RAG]
       └──────────────┘  │───▶ [LLM]
              │          │───▶ [Validate]
              ▼          └───▶ [AI-REPS]
       ┌──────────────┐
       │  Answer +    │
       │   Trace      │
       └──────────────┘
```

---

**Для использования в презентации:**
1. Блок-схема для общего понимания
2. Детальный поток для технической аудитории
3. Интерактивная диаграмма для демонстрации

























