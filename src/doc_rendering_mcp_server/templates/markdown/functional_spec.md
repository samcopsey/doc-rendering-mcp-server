---
title: "{{ title }}"
project: "{{ project_name }}"
version: "{{ version | default('1.0') }}"
author: "{{ author | default('Cast (AI-generated)') }}"
date: "{{ date | default('') }}"
status: "{{ status | default('Draft') }}"
---

# {{ title }}

**Project:** {{ project_name }}
{% if status %}**Status:** {{ status }}{% endif %}
{% if priority %}**Priority:** {{ priority }}{% endif %}
{% if effort_estimate %}**Effort Estimate:** {{ effort_estimate }}{% endif %}
{% if ado_link %}**ADO Link:** [{{ ado_link }}]({{ ado_link }}){% endif %}

---

## 1. Overview

{{ overview }}

{% if stakeholders or business_value_score or priority or effort_estimate or target_completion %}
| Detail | Value |
|--------|-------|
{% if stakeholders %}| Stakeholders | {{ stakeholders if stakeholders is string else stakeholders | join(", ") }} |
{% endif %}{% if business_value_score %}| Business Value Score | {{ business_value_score }} |
{% endif %}{% if priority %}| Priority | {{ priority }} |
{% endif %}{% if effort_estimate %}| Effort Estimate | {{ effort_estimate }} |
{% endif %}{% if target_completion %}| Target Completion | {{ target_completion }} |
{% endif %}
{% endif %}
{% if scope %}
### Scope

{% if scope is string %}{{ scope }}{% else %}{% for item in scope %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if out_of_scope %}
### Out of Scope

{% if out_of_scope is string %}{{ out_of_scope }}{% else %}{% for item in out_of_scope %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if assumptions %}
### Assumptions

{% if assumptions is string %}{{ assumptions }}{% else %}{% for item in assumptions %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if constraints %}
### Constraints

{% if constraints is string %}{{ constraints }}{% else %}{% for item in constraints %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if roi_azure_estimate or roi_questions or growth_strategy_alignment %}
## 2. ROI Statement & Strategic Value

{% if roi_azure_estimate %}
### Azure Cost Estimate

{{ roi_azure_estimate }}

{% endif %}
{% if growth_strategy_alignment %}
### Growth Strategy 3.0 Alignment

{{ growth_strategy_alignment }}

{% endif %}
{% if roi_questions %}
### ROI Questions for Requestor

> **These questions must be answered by the business — figures must never be fabricated.**

{% for q in roi_questions %}{{ loop.index }}. {{ q }}
{% endfor %}

{% endif %}
{% endif %}
## 3. Problem Statement

{{ problem_statement }}

{% if problem_who_impacted %}
### Who Is Impacted

{% if problem_who_impacted is string %}{{ problem_who_impacted }}{% else %}{% for item in problem_who_impacted %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if problem_current_state %}
### Current State

{% if problem_current_state is string %}{{ problem_current_state }}{% else %}{% for item in problem_current_state %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if problem_desired_state %}
### Desired State

{% if problem_desired_state is string %}{{ problem_desired_state }}{% else %}{% for item in problem_desired_state %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if key_features %}
## 4. Key Features

{% for feature in key_features %}
### {{ feature.name }}

{% if feature.capabilities is string %}{{ feature.capabilities }}{% else %}{% for cap in feature.capabilities %}- {{ cap }}
{% endfor %}{% endif %}
{% if feature.user_benefits %}
> **User Benefit:** {{ feature.user_benefits }}
{% endif %}

{% endfor %}
{% endif %}
{% if architecture_overview or architecture_components or architecture_data_flows %}
## 5. Functional Architecture

{% if architecture_overview %}
{{ architecture_overview }}

{% endif %}
{% if architecture_components %}
### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
{% for comp in architecture_components %}| {{ comp.component if comp is mapping else comp }} | {{ comp.technology | default("—") if comp is mapping else "—" }} | {{ comp.purpose | default("—") if comp is mapping else "—" }} |
{% endfor %}

{% endif %}
{% if architecture_data_flows %}
### Data & User Flows

{% if architecture_data_flows is string %}{{ architecture_data_flows }}{% else %}{% for flow in architecture_data_flows %}{{ loop.index }}. {{ flow }}
{% endfor %}{% endif %}

{% endif %}
{% endif %}
## 6. Detailed Requirements

### Functional Requirements

{% if requirements is string %}
{{ requirements }}
{% else %}
| ID | Category | Requirement | Priority |
|----|----------|-------------|----------|
{% for req in requirements %}| {{ req.id | default("FR-%03d" | format(loop.index)) if req is mapping else loop.index }} | {{ req.category | default("—") if req is mapping else "—" }} | {{ req.description if req is mapping else req }} | {{ req.priority | default("Must Have") if req is mapping else "Must Have" }} |
{% endfor %}
{% endif %}

{% if nonfunctional_requirements %}
### Non-Functional Requirements

{% if nonfunctional_requirements is mapping %}{% for category, detail in nonfunctional_requirements.items() %}
#### {{ category }}

{% if detail is string %}{{ detail }}{% else %}{% for item in detail %}- {{ item }}
{% endfor %}{% endif %}

{% endfor %}{% elif nonfunctional_requirements is string %}{{ nonfunctional_requirements }}{% endif %}
{% endif %}
{% if acceptance_criteria %}
### Acceptance Criteria

{% if acceptance_criteria is string %}{{ acceptance_criteria }}{% else %}{% for criterion in acceptance_criteria %}{{ loop.index }}. {{ criterion }}
{% endfor %}{% endif %}

{% endif %}
{% if security_auth or security_permissions or security_secrets or security_data_residency or security_gdpr or security_network or security_audit %}
## 7. Security & Compliance

{% if security_auth %}
### Authentication

{{ security_auth }}

{% endif %}
{% if security_permissions %}
### Permissions & Authorisation

{% if security_permissions is string %}{{ security_permissions }}{% else %}{% for item in security_permissions %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if security_secrets %}
### Secrets Management

{{ security_secrets }}

{% endif %}
{% if security_data_residency %}
### Data Residency

{{ security_data_residency }}

{% endif %}
{% if security_gdpr %}
### GDPR & Data Protection

{{ security_gdpr }}

{% endif %}
{% if security_network %}
### Network Security

{{ security_network }}

{% endif %}
{% if security_audit %}
### Audit & Logging

{{ security_audit }}

{% endif %}
{% endif %}
{% if systems_customer_requirements or systems_infrastructure or systems_integrations %}
## 8. Systems & Environments

{% if systems_customer_requirements %}
### Customer Requirements

{% if systems_customer_requirements is string %}{{ systems_customer_requirements }}{% else %}{% for item in systems_customer_requirements %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if systems_infrastructure %}
### Infrastructure

| Service | Environment | Configuration |
|---------|-------------|---------------|
{% for entry in systems_infrastructure %}| {{ entry.service if entry is mapping else entry }} | {{ entry.environment | default("—") if entry is mapping else "—" }} | {{ entry.configuration | default("—") if entry is mapping else "—" }} |
{% endfor %}

{% endif %}
{% if systems_integrations %}
### Integration Points

{% if systems_integrations is string %}{{ systems_integrations }}{% else %}{% for item in systems_integrations %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% endif %}
{% if dependencies_technical or dependencies_team or dependencies_external or blockers %}
## 9. Dependencies & Prerequisites

{% if dependencies_technical %}
### Technical Dependencies

{% if dependencies_technical is string %}{{ dependencies_technical }}{% else %}{% for item in dependencies_technical %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if dependencies_team %}
### Team Dependencies

{% if dependencies_team is string %}{{ dependencies_team }}{% else %}{% for item in dependencies_team %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if dependencies_external %}
### External Dependencies

{% if dependencies_external is string %}{{ dependencies_external }}{% else %}{% for item in dependencies_external %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% if blockers %}
### Blockers

{% if blockers is string %}{{ blockers }}{% else %}{% for item in blockers %}- {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% endif %}
{% if implementation_estimate or implementation_phases or target_go_live or critical_path %}
## 10. Implementation Approach

{% if implementation_estimate %}**Effort Estimate:** {{ implementation_estimate }}

{% endif %}
{% if implementation_phases %}
### Phases

{% for phase in implementation_phases %}{{ loop.index }}. {{ phase }}
{% endfor %}

{% endif %}
{% if target_go_live %}**Target Go-Live:** {{ target_go_live }}

{% endif %}
{% if critical_path %}
### Critical Path

{% if critical_path is string %}{{ critical_path }}{% else %}{% for item in critical_path %}{{ loop.index }}. {{ item }}
{% endfor %}{% endif %}

{% endif %}
{% endif %}
{% if risks %}
## Risks

{% if risks is string %}{{ risks }}{% else %}
| Risk | Impact | Mitigation |
|------|--------|------------|
{% for risk in risks %}| {{ risk.description if risk is mapping else risk }} | {{ risk.impact | default("Medium") if risk is mapping else "—" }} | {{ risk.mitigation | default("—") if risk is mapping else "—" }} |
{% endfor %}
{% endif %}

{% endif %}
{% if pre_delivery_checklist %}
## Pre-Delivery Checklist

{% for item in pre_delivery_checklist %}- [ ] {{ item }}
{% endfor %}
{% endif %}
---
*Generated by Cast on {{ date | default('') }}*
