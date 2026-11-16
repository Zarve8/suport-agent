# Support-Ticket Co-pilot: Business Case

## Decision

At approximately **10,000 tickets per month**, the support-ticket co-pilot is worth running if it reduces handling time by around four minutes on at least 60% of repetitive tickets.

The recommended configuration is a **draft-only co-pilot** with grounded retrieval, deterministic safety rules, and mandatory human review for sensitive or unsupported cases.

## Assumptions

| Metric | Assumption |
|---|---:|
| Monthly tickets | 10,000 |
| Average current handling time | 8 minutes |
| Support labor cost | $20/hour |
| Tickets suitable for automation | 60% |
| Handling-time reduction | 4 minutes per suitable ticket |
| Average LLM cost | $0.01 per ticket |
| Infrastructure and monitoring | $800/month |

These are planning assumptions for the take-home case. They should be replaced with production measurements during a pilot.

## Monthly value

Suitable tickets:

```text
10,000 × 60% = 6,000 tickets
```

Time saved:

```text
6,000 × 4 minutes = 24,000 minutes = 400 hours
```

Labor value saved:

```text
400 hours × $20/hour = $8,000/month
```

## Monthly cost

```text
LLM usage:                    10,000 × $0.01 =   $100
Infrastructure, monitoring:                    $800
Total estimated cost:                         $900
```

## Expected return

```text
Gross monthly benefit:       $8,000
Estimated monthly cost:        $900
Estimated net benefit:       $7,100
```

```text
ROI = $7,100 / $900 = 7.9×
```

Estimated break-even volume:

```text
$900 / ($20 × 4/60 × 60%) ≈ 1,125 tickets/month
```

The current volume of 10,000 tickets per month is substantially above this illustrative break-even point.

## Configuration decision

| Configuration | Expected benefit | Risk | Decision |
|---|---|---|---|
| Human-only support | Baseline | Lowest AI risk | Comparison baseline |
| Draft-only co-pilot | High for repetitive tickets | Human approves reply | **Recommended for Phase 1** |
| Auto-send supported answers | Potentially higher | Greater grounding and compliance risk | Phase 2 after measurement |
| Large model for every ticket | Higher possible quality | Higher cost | Avoid by default |
| Small model plus rules and retrieval | Low cost and predictable routing | Requires good evaluation | **Recommended at scale** |

## Recommended operating model

- Use BM25 retrieval over the approved knowledge base.
- Use a cost-efficient model for classification and grounded drafting.
- Keep deterministic rules for trading advice, complaints, KYC/AML, unsupported requests, and escalation.
- Require citations for every knowledge-base answer.
- Route complaints, KYC/AML cases, account-specific actions, and low-coverage answers to a human.
- Start with agent-approved drafts; do not auto-send in Phase 1.

## Pilot success criteria

Before expanding to auto-send, measure:

- Average handling-time reduction.
- Percentage of tickets receiving an accepted draft.
- Citation and grounding accuracy.
- Escalation precision and recall.
- Unsupported-answer and hallucination rate.
- Agent edit rate.
- Customer satisfaction and complaint rate.

## Conclusion

The co-pilot is economically attractive at 10,000 tickets per month under reasonable assumptions. The safest business decision is to launch a draft-only Phase 1, measure real handling-time savings and answer quality, and scale only the well-grounded deposit, account-opening, and verification workflows. Auto-send should require demonstrated safety and citation accuracy rather than being enabled at launch.
