# AI Threat Hunting Hypothesis Generator


A local AI-powered Threat Hunting Hypothesis Generator that converts cybersecurity intelligence into actionable hunting scenarios.

The platform uses **local Large Language Models (LLM)**, RSS threat intelligence feeds, single article analysis, and organization context to help SOC Analysts,Incident Responders, and Detection Engineers generate high-quality threat hunting hypotheses.

---

##  Overview

Security teams receive thousands of threat intelligence updates every day from advisories, blogs, and vulnerability feeds.

Manually converting this intelligence into actionable hunts requires:

- Understanding attacker behavior
- Mapping threats to MITRE ATT&CK
- Identifying affected technologies
- Creating detection logic
- Prioritizing based on organization context

This project automates that workflow using a **local AI model**.

---

# Architecture

<img width="1110" height="906" alt="Architecture drawio" src="https://github.com/user-attachments/assets/ad2ae007-25a5-47ed-93b4-9c9a6154840f" />



# Features


## Threat Intelligence Feed Management

Add and manage cybersecurity RSS feeds.

Supported:

- Add custom RSS feeds
- Enable feeds
- Disable feeds
- Delete feeds
- Test RSS availability
- Persistent storage

Example sources:

- CISA Advisories
- Security vendor research
- Vulnerability feeds
- Threat intelligence blogs


---

## Organization Context Awareness


Generate targeted hypotheses using:


### Industry / Sector

Examples:

- BFSI
- Healthcare
- Government
- Technology
- Manufacturing
- Energy
- Retail


### Technology Stack

Examples:

- Microsoft 365
- Active Directory
- Azure
- AWS
- Kubernetes
- Fortinet
- CrowdStrike
- Sentinel
- Splunk


Supports:

- Add custom technologies
- Delete custom technologies
- Persistent custom stack


### Geographic Context

Examples:

- Global
- India
- United States
- Europe
- Middle East
- APAC


---

# Threat Date Filtering

Generate hunts based on threat publication time.

Supported:

- Today
- Yesterday
- Custom date range
- Any date


Example:

```
Find threats affecting:

Sector:
BFSI

Location:
India

Technology:
Microsoft 365

Date:
Last 7 days
```

---

# AI Generated Output


The AI generates:

## Executive Summary


High-level threat overview.


---

## Threat Hunting Hypothesis


Example:

```
Adversaries may attempt credential theft against
Microsoft 365 environments using phishing campaigns
observed in recent threat intelligence reports.
```

---

## MITRE ATT&CK Mapping


Example:

| Technique | Description |
|-|-|
| T1566 | Phishing |
| T1078 | Valid Accounts |
| T1059 | Command Execution |


---

## Hunting Steps


Example:

```
1. Review suspicious authentication events

2. Identify impossible travel activity

3. Analyze suspicious inbox rules

4. Review OAuth application permissions
```


---

## Detection Queries


Generates:

- Microsoft Sentinel KQL
- Splunk SPL
- Sigma detection logic


Example:

```kql
SigninLogs
| where ResultType != 0
| summarize count() by UserPrincipalName, IPAddress
```

---

## Required Log Sources


Example:

- Identity logs
- Firewall logs
- EDR telemetry
- Email security logs
- Proxy logs


---

# Technology Stack


## Frontend

- React
- JavaScript
- CSS


## Backend

- Python
- FastAPI


## AI Engine

- Ollama
- Qwen Local LLM


## Storage

- Docker persistent volumes
- JSON based local storage


## Containerization

- Docker
- Docker Compose


---

# Deployment


## Requirements


Install:

- Docker
- Docker Compose


---

Clone repository:

```bash
git clone <repository-url>

cd Threat-Hunting-AI
```


---

Start application:

```bash
docker compose up -d --build
```


---

Check containers:

```bash
docker ps
```


Expected:

```
threat-hunting-ui

threat-hunting-backend

threat-hunting-ollama
```


---

# Access Application


Frontend:

```
http://localhost:5173
```


Backend API:

```
http://localhost:18000/docs
```


Ollama API:

```
http://localhost:21434
```


---

# Local LLM Model


Default:

```
qwen2.5:7b
```


Pull manually:

```bash
docker exec -it threat-hunting-ollama \
ollama pull qwen2.5:7b
```


Verify:

```bash
docker exec -it threat-hunting-ollama \
ollama list
```


---

# Persistent Data


The following data survives container restart:

RSS feeds

Custom technology stack

LLM model files


Stored using Docker volumes:

```
backend_data

ollama_models
```


Remove all saved data:

```bash
docker compose down -v
```


---

# Example Workflow


1. Add RSS threat feeds

2. Select organization industry

3. Select technology stack

4. Choose threat date range

5. Generate hypothesis

6. Review MITRE mapping

7. Export hunting report


---

# Use Cases


## SOC Teams

Create daily hunting activities from new threats.


## Threat Intelligence Teams

Convert intelligence reports into detection ideas.


## Incident Response Teams

Prepare proactive investigations.


## Security Engineers

Create detection engineering backlog.


---

# Roadmap


Planned improvements:


- CVE enrichment
- MITRE ATT&CK API integration
- Vector database support
- Threat actor profiling
- IOC extraction
- STIX/TAXII support
- PDF report generation
- Authentication
- Multi-user support
- Enterprise dashboard


---

# Disclaimer


This tool provides AI-assisted threat hunting recommendations.

Generated hypotheses should always be reviewed and validated by security analysts before production use.


---

# License

Open Source - Community Edition


---

# Author

Developed as a cybersecurity research project focusing on:

- Threat Intelligence Automation
- AI Assisted Security Operations
- Detection Engineering
- SOC Automation
