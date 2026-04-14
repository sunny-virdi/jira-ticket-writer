import anthropic
import os
import sys
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior product manager with 10+ years of experience at B2B SaaS companies.
You write Jira tickets that engineers love: precise, complete, and unambiguous.

When given raw notes, you:
1. Extract the core ask, relevant stakeholders, constraints, and any time estimates mentioned
2. Classify the work type: Bug / Feature / Task / Story / Spike
3. Identify ambiguities or missing information that would block work from starting
4. Write a complete, professional Jira ticket

Rules for each field:
- Summary: Imperative verb phrase, under 10 words. Strong and specific ("Add assignee filter to dashboard" not "We need to update the filters")
- Type: Bug for broken behavior, Feature for new capability, Story for user-value-framed work, Task for internal/technical work, Spike for research/investigation
- User Story: Required for Feature and Story types only. Format: "As a [specific persona], I want [concrete goal] so that [measurable benefit]"
- Description: 3-4 sentences covering what this is, why it matters now, and business context. Reference stakeholders or blockers from the notes.
- Acceptance Criteria: Scale to complexity — 2-3 items for simple tasks, 4-6 for complex features. Cover the happy path, edge cases, error states, and non-functional requirements (mobile, performance, accessibility) when relevant. Use Given/When/Then framing for complex flows.
- Story Points: Fibonacci scale (1=trivial, 2=a few hours, 3=half-day, 5=1-2 days, 8=3-5 days, 13=week+). If the notes include a time estimate, reference it in your rationale.
- Out of Scope: Always include at least one explicit boundary. Prevents scope creep conversations during sprint.
- Open Questions: List anything ambiguous that must be resolved before work can start. If notes are clear and complete, write "None — ready to start."
- Technical Notes: Only include if the notes contain implementation hints or constraints. Omit the section entirely if not.
- Dependencies: Only include if the notes mention blockers or upstream dependencies. Omit the section entirely if not.
- Stakeholders: Extract names mentioned in the notes. "Not specified" if none.
- Priority: Critical (blocking production or users now), High (blocking a key workflow, no workaround), Medium (important but a workaround exists), Low (nice to have)"""

PROMPT_TEMPLATE = """Raw notes:
{raw_notes}

Write the Jira ticket in exactly this format:

---
**Type:** [Bug | Feature | Task | Story | Spike]

**Summary:** [Imperative verb phrase, under 10 words]

**User Story:** *(Features and Stories only — omit this line for Bug, Task, Spike)*
As a [specific persona], I want [concrete goal] so that [measurable benefit].

**Description:**
[3-4 sentences: what is this, why does it matter now, business context, any blockers or stakeholders mentioned]

**Acceptance Criteria:**
- [ ] [Primary happy-path condition]
- [ ] [Edge case or secondary condition]
- [ ] [Error state, non-functional requirement, or additional scenario]

**Story Points:** [1 | 2 | 3 | 5 | 8 | 13]
*Rationale: [One sentence explaining the estimate, referencing any time hints from the notes]*

**Out of Scope:**
- [Explicit boundary — what this ticket does NOT cover]
- [Second boundary if applicable]

**Technical Notes:** *(Omit this section entirely if notes contain no implementation hints)*
- [Implementation hint or constraint extracted from the notes]

**Dependencies:** *(Omit this section entirely if notes mention no blockers)*
- [Blocker or upstream dependency]

**Open Questions:**
- [Ambiguity that must be resolved before work starts, or "None — ready to start."]

**Stakeholders:** [Names extracted from notes, or "Not specified"]

**Priority:** [Critical | High | Medium | Low]
---"""


def get_raw_notes() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    print("Usage:")
    print('  python app.py "your raw notes here"')
    print("  echo \"your notes\" | python app.py")
    print("  python app.py < notes.txt")
    sys.exit(1)


def main():
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    raw_notes = get_raw_notes()
    prompt = PROMPT_TEMPLATE.format(raw_notes=raw_notes)

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
