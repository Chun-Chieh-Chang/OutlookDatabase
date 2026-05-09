---
title: "{{name}}"
aliases: {{aliases}}
type: {{category}}
dimensions: [{{category}}]
lifecycle: {{lifecycle}}
improvement: {{improvement}}
urgency: {{urgency}}
tags: {{tags}}
domain: "{{domain}}"
created: {{created}}
updated: {{updated}}
---

# {{name}}

## Description
{{description}}

## Relationships
{% for rel in relationships %}
- **{{rel.type}}**: [[{{rel.target}}]]
{% endfor %}

## Status & Synthesis
(AI synthesized context goes here)

## Records
- Initial extraction from {{source_email}}
