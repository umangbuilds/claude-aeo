# Weekly AEO Report — {{domain}} — {{iso_week}}

## Citation rate
- This week: {{citation_rate_this}}% ({{cited_this}} / {{checked_this}} checked)
- Last week: {{citation_rate_last}}% ({{cited_last}} / {{checked_last}} checked)
- Delta: {{delta_pp}} pp

### Per LLM
| Provider | Cited | Not cited | Not checked |
|---|---|---|---|
| openai | {{openai_cited}} | {{openai_not_cited}} | {{openai_not_checked}} |
| anthropic | {{anthropic_cited}} | {{anthropic_not_cited}} | {{anthropic_not_checked}} |
| perplexity | {{perplexity_cited}} | {{perplexity_not_cited}} | {{perplexity_not_checked}} |
| gemini | {{gemini_cited}} | {{gemini_not_cited}} | {{gemini_not_checked}} |

---

## Ranking changes (GSC)
| Query | Last week pos | This week pos | Delta |
|---|---|---|---|
| {{query}} | {{last_pos}} | {{this_pos}} | {{delta}} |

*Skipped — GSC not connected.* (remove this line when GSC is wired)

---

## Critical audit findings
- {{finding}}

---

## Top 10 actions this week
| # | Type | Title | Impact | Effort (min) | Score | Draft |
|---|---|---|---|---|---|---|
| 1 | {{type}} | {{title}} | {{impact}} | {{effort}} | {{score}} | [draft]({{draft_path}}) |

---

## How to execute
- Run `/aeo-loop assist <action-id>` per action when you're ready to ship.
- After clicking Submit, run `/aeo-loop mark-done <action-id> --cited-on=<platform>`.
- For the full action list: `/aeo-loop list-actions {{domain}}`.
