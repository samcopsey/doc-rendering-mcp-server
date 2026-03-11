---
title: "{{ title }}"
project: "{{ project_name }}"
version: "1.0"
date: "{{ date | default('') }}"
author: "Cast (AI-generated)"
status: "Draft"
---

# Use Case: {{ title }}

## Overview

{{ overview }}

## Actors

| Actor | Description |
|-------|-------------|
{% if actors is string %}{{ actors }}{% else %}{% for actor in actors %}| {{ actor.name }} | {{ actor.description }} |
{% endfor %}{% endif %}

## Preconditions

{{ preconditions | default('None specified') }}

## Main Flow

{% if main_flow is string %}{{ main_flow }}{% else %}{% for step in main_flow %}{{ loop.index }}. {{ step }}
{% endfor %}{% endif %}

## Alternative Flows

{{ alternative_flows | default('None specified') }}

## Postconditions

{{ postconditions | default('None specified') }}

## Notes

{{ notes | default('') }}
