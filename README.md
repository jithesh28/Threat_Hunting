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


<mxfile host="app.diagrams.net">
  <diagram name="Page-1" id="SdP0kBfQ80SLqPcuTFl2">
    <mxGraphModel dx="1288" dy="703" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-1" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Output" vertex="1">
          <mxGeometry height="104" width="1108" x="20" y="900" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-2" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Threat Sources" vertex="1">
          <mxGeometry height="54" width="167" x="293" y="100" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-3" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="RSS Collector" vertex="1">
          <mxGeometry height="54" width="155" x="398" y="204" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-4" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="RSS Feeds" vertex="1">
          <mxGeometry height="54" width="131" x="510" y="100" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-5" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Article Extractor" vertex="1">
          <mxGeometry height="54" width="179" x="485" y="308" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-6" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Article URL" vertex="1">
          <mxGeometry height="54" width="141" x="603" y="204" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-7" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Intelligence Processor" vertex="1">
          <mxGeometry height="54" width="217" x="466" y="412" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-8" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Organization Context Engine" vertex="1">
          <mxGeometry height="78" width="260" x="445" y="516" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-9" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Local LLM Engine&#xa;Ollama + Qwen" vertex="1">
          <mxGeometry height="78" width="182" x="484" y="644" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-10" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Threat Hunting Hypothesis Engine" vertex="1">
          <mxGeometry height="78" width="260" x="445" y="772" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-11" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="MITRE Mapping" vertex="1">
          <mxGeometry height="54" width="167" x="55" y="925" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-12" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Hunting Steps" vertex="1">
          <mxGeometry height="54" width="159" x="272" y="925" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-13" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Detection Queries" vertex="1">
          <mxGeometry height="54" width="189" x="480" y="925" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-14" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Required Logs" vertex="1">
          <mxGeometry height="54" width="159" x="719" y="925" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-15" parent="1" style="whiteSpace=wrap;strokeWidth=2;fillColor=light-dark(#eeeeee,#1f2020);strokeColor=light-dark(#999999,#cccccc);fontColor=light-dark(#333333,#cccccc);" value="Analyst Report" vertex="1">
          <mxGeometry height="54" width="164" x="929" y="925" as="geometry" />
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-16" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-2" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.17;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-3" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="376" y="179" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-17" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-4" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.84;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-3" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="575" y="179" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-18" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-3" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.21;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-5" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="476" y="283" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-19" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-6" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.79;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-5" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="674" y="283" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-20" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-5" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-7" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points" />
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-21" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-7" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-8" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points" />
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-22" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-8" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-9" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points" />
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-23" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-9" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-10" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points" />
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-24" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-10" style="curved=1;startArrow=none;endArrow=block;exitX=0;exitY=0.74;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-11" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="138" y="875" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-25" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-10" style="curved=1;startArrow=none;endArrow=block;exitX=0;exitY=0.98;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-12" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="351" y="875" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-26" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-10" style="curved=1;startArrow=none;endArrow=block;exitX=0.5;exitY=1;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-13" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points" />
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-27" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-10" style="curved=1;startArrow=none;endArrow=block;exitX=1;exitY=0.98;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-14" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="799" y="875" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="Gaa7GcHc_YyA_d92bGl7-28" edge="1" parent="1" source="Gaa7GcHc_YyA_d92bGl7-10" style="curved=1;startArrow=none;endArrow=block;exitX=1;exitY=0.74;entryX=0.5;entryY=0;rounded=0;" target="Gaa7GcHc_YyA_d92bGl7-15" value="">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1011" y="875" />
            </Array>
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>



---

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

✔ RSS feeds

✔ Custom technology stack

✔ LLM model files


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