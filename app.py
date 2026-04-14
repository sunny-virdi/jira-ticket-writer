# V1 SCOPE: Summary, Description, Acceptance Criteria, Priority
# INTENTIONALLY EXCLUDED: Story Points (team-dependent)
# OUT OF SCOPE: Epic, Labels, Sprint, Reporter, Custom fields

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

raw_notes = """
Met with design team today. Need to update the dashboard filters.
Currently users can only filter by date. They want to filter by assignee and 
status too. Sarah said this is blocking her team's weekly review. 
Should be straightforward, maybe 2-3 days work. Needs to work on mobile too.
"""

prompt = f"""You are a JIRA ticket writer for product teams. 
Convert the following raw notes into a structured JIRA ticket.

Raw notes:
{raw_notes}

Return the ticket in exactly this format:

**Summary:** [One line, action-oriented, under 10 words]

**Description:**
[2-3 sentences of context. What is this and why does it matter?]

**Acceptance Criteria:**
- [ ] [Testable condition 1]
- [ ] [Testable condition 2]
- [ ] [Testable condition 3]

**Priority:** [Critical / High / Medium / Low]
"""

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(message.content[0].text)