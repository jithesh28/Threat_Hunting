import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://localhost:18000";

const DEFAULT_TECHNOLOGY_OPTIONS = [
  {
    group: "Microsoft",
    options: [
      "Microsoft 365",
      "Microsoft Entra ID / Azure AD",
      "Exchange Online",
      "SharePoint",
      "OneDrive",
      "Microsoft Teams",
      "Microsoft Excel",
      "Windows Server",
      "Active Directory",
      "Microsoft Defender",
      "Microsoft Sentinel"
    ]
  },
  {
    group: "Cloud",
    options: ["AWS", "Azure", "Google Cloud Platform", "Kubernetes", "Docker", "Terraform"]
  },
  {
    group: "Network & VPN",
    options: ["Fortinet VPN", "Palo Alto Firewall", "Cisco ASA", "Cisco AnyConnect", "SonicWall", "F5 BIG-IP", "Zscaler"]
  },
  {
    group: "Security Tools",
    options: ["CrowdStrike", "SentinelOne", "Wazuh", "Splunk", "Elastic Security", "QRadar", "Nessus", "Qualys"]
  },
  {
    group: "Identity & Access",
    options: ["Okta", "Ping Identity", "Duo MFA", "CyberArk", "HashiCorp Vault"]
  },
  {
    group: "Business Applications",
    options: ["Salesforce", "SAP", "Oracle", "ServiceNow", "Jira", "GitHub", "GitLab"]
  }
];

const INDUSTRY_OPTIONS = [
  "BFSI - Banking, Financial Services, Insurance, FinTech",
  "Healthcare & Pharmaceuticals",
  "Government & Public Sector",
  "Defense & Aerospace",
  "Technology, SaaS & Software",
  "Telecommunications",
  "Energy, Utilities, Oil & Gas",
  "Manufacturing & Industrial",
  "Retail & E-commerce",
  "Education",
  "Transportation & Logistics",
  "Media, Entertainment & Social Platforms",
  "Agriculture, Forestry & Food Production",
  "Construction & Real Estate",
  "Professional Services",
  "Hospitality & Travel"
];

const GEO_OPTIONS = [
  "Global",
  "India",
  "United States",
  "United Kingdom",
  "European Union",
  "Middle East",
  "Singapore",
  "Australia",
  "Canada",
  "Japan",
  "South Korea",
  "Africa",
  "Latin America"
];

const PDF_PAGE = {
  width: 612,
  height: 792,
  marginX: 48,
  topY: 744,
  lineHeight: 14,
  maxLines: 48,
  maxChars: 92
};

const escapePdfText = (text) =>
  text.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");

const normalizePdfText = (text) =>
  text
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .replace(/\t/g, "    ")
    .replace(/[^\x0A\x20-\x7E]/g, "-");

const cleanReportHeading = (line) =>
  line
    .replace(/^#+\s*/, "")
    .replace(/^\d+[\).\s-]+/, "")
    .replace(/^[-*]\s*/, "")
    .replace(/\*\*/g, "")
    .replace(/main threat hunting hypothesis\s*:?\s*/i, "")
    .trim();

const shortenHeading = (heading, maxLength = 72) => {
  if (!heading) return "Threat Hunting Hypothesis";
  if (heading.length <= maxLength) return heading;

  const shortened = heading.slice(0, maxLength).replace(/\s+\S*$/, "").trim();
  return `${shortened || heading.slice(0, maxLength).trim()}...`;
};

const getHypothesisHeading = (report) => {
  const lines = normalizePdfText(report)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const hypothesisSectionIndex = lines.findIndex((line) =>
    /main threat hunting hypothesis/i.test(line)
  );

  if (hypothesisSectionIndex >= 0) {
    const sectionHeading = cleanReportHeading(lines[hypothesisSectionIndex]);

    if (sectionHeading) {
      return shortenHeading(sectionHeading);
    }

    const nextLine = lines
      .slice(hypothesisSectionIndex + 1)
      .find((line) => !/^\d+[\).\s-]+/.test(line));

    if (nextLine) {
      return shortenHeading(cleanReportHeading(nextLine));
    }
  }

  const firstContentLine = lines.find((line) => !/executive summary/i.test(line));
  return shortenHeading(cleanReportHeading(firstContentLine || ""));
};

const slugifyFilename = (value) => {
  const slug = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);

  return slug || "threat-hunting-hypothesis";
};

const wrapPdfLine = (line, maxChars) => {
  if (!line.trim()) return [""];

  const words = line.split(/\s+/);
  const lines = [];
  let current = "";

  words.forEach((word) => {
    if (word.length > maxChars) {
      if (current) {
        lines.push(current);
        current = "";
      }

      for (let index = 0; index < word.length; index += maxChars) {
        lines.push(word.slice(index, index + maxChars));
      }

      return;
    }

    const nextLine = current ? `${current} ${word}` : word;

    if (nextLine.length > maxChars) {
      lines.push(current);
      current = word;
    } else {
      current = nextLine;
    }
  });

  if (current) lines.push(current);

  return lines;
};

const createReportPdf = (report, heading) => {
  const normalizedReport = normalizePdfText(report);
  const generatedAt = new Date().toLocaleString();
  const sourceLines = [
    normalizePdfText(heading),
    "Threat Hunting Hypothesis Report",
    `Generated: ${generatedAt}`,
    "",
    ...normalizedReport.split("\n")
  ];

  const wrappedLines = sourceLines.flatMap((line) =>
    wrapPdfLine(line, PDF_PAGE.maxChars)
  );

  const pages = [];

  for (let index = 0; index < wrappedLines.length; index += PDF_PAGE.maxLines) {
    pages.push(wrappedLines.slice(index, index + PDF_PAGE.maxLines));
  }

  const pageCount = Math.max(pages.length, 1);
  const fontObjectId = 3 + pageCount * 2;
  const objects = [];
  const pageObjectIds = [];

  objects[1] = "<< /Type /Catalog /Pages 2 0 R >>";

  pages.forEach((pageLines, index) => {
    const pageObjectId = 3 + index * 2;
    const contentObjectId = pageObjectId + 1;
    pageObjectIds.push(pageObjectId);

    const textCommands = pageLines
      .map((line) => `(${escapePdfText(line)}) Tj T*`)
      .join("\n");
    const stream = [
      "BT",
      "/F1 10 Tf",
      `${PDF_PAGE.lineHeight} TL`,
      `${PDF_PAGE.marginX} ${PDF_PAGE.topY} Td`,
      textCommands,
      "ET"
    ].join("\n");

    objects[pageObjectId] =
      `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PDF_PAGE.width} ${PDF_PAGE.height}] /Resources << /Font << /F1 ${fontObjectId} 0 R >> >> /Contents ${contentObjectId} 0 R >>`;
    objects[contentObjectId] = `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`;
  });

  objects[2] =
    `<< /Type /Pages /Kids [${pageObjectIds.map((id) => `${id} 0 R`).join(" ")}] /Count ${pageObjectIds.length} >>`;
  objects[fontObjectId] =
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>";

  let pdf = "%PDF-1.4\n";
  const offsets = [0];

  for (let id = 1; id < objects.length; id += 1) {
    if (!objects[id]) continue;

    offsets[id] = pdf.length;
    pdf += `${id} 0 obj\n${objects[id]}\nendobj\n`;
  }

  const xrefOffset = pdf.length;
  pdf += `xref\n0 ${objects.length}\n`;
  pdf += "0000000000 65535 f \n";

  for (let id = 1; id < objects.length; id += 1) {
    pdf += `${String(offsets[id] || 0).padStart(10, "0")} 00000 n \n`;
  }

  pdf += `trailer\n<< /Size ${objects.length} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;

  return pdf;
};

function MultiSelectDropdown({ label, options, selected, setSelected }) {
  const [open, setOpen] = useState(false);

  const toggleOption = (option) => {
    if (selected.includes(option)) {
      setSelected(selected.filter((item) => item !== option));
    } else {
      setSelected([...selected, option]);
    }
  };

  return (
    <div className="dropdown-block">
      <label>{label}</label>

      <button type="button" className="dropdown-trigger" onClick={() => setOpen(!open)}>
        {selected.length > 0 ? `${selected.length} selected` : "Select options"}
      </button>

      {open && (
        <div className="dropdown-menu">
          {options.map((option) => (
            <label className="dropdown-option" key={option}>
              <input
                type="checkbox"
                checked={selected.includes(option)}
                onChange={() => toggleOption(option)}
              />
              {option}
            </label>
          ))}
        </div>
      )}

      {selected.length > 0 && (
        <div className="selected-pills">
          {selected.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}
    </div>
  );
}

function TechnologyDropdown({ selected, setSelected, customTechnologies }) {
  const [open, setOpen] = useState(false);

  const mergedGroups = [...DEFAULT_TECHNOLOGY_OPTIONS];

  if (customTechnologies.length > 0) {
    mergedGroups.push({
      group: "Custom",
      options: customTechnologies.map((tech) => tech.name)
    });
  }

  const toggleOption = (option) => {
    if (selected.includes(option)) {
      setSelected(selected.filter((item) => item !== option));
    } else {
      setSelected([...selected, option]);
    }
  };

  return (
    <div className="dropdown-block">
      <label>Technology Stack</label>

      <button type="button" className="dropdown-trigger" onClick={() => setOpen(!open)}>
        {selected.length > 0 ? `${selected.length} selected` : "Select technologies"}
      </button>

      {open && (
        <div className="dropdown-menu large">
          {mergedGroups.map((group) => (
            <div className="tech-group-dropdown" key={group.group}>
              <h4>{group.group}</h4>

              {group.options.map((option) => (
                <label className="dropdown-option" key={option}>
                  <input
                    type="checkbox"
                    checked={selected.includes(option)}
                    onChange={() => toggleOption(option)}
                  />
                  {option}
                </label>
              ))}
            </div>
          ))}
        </div>
      )}

      {selected.length > 0 && (
        <div className="selected-pills">
          {selected.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}
    </div>
  );
}

function App() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [hypothesisMode, setHypothesisMode] = useState("context");

  const [feeds, setFeeds] = useState([]);
  const [customTechnologies, setCustomTechnologies] = useState([]);

  const [feedName, setFeedName] = useState("");
  const [feedUrl, setFeedUrl] = useState("");
  const [feedCategory, setFeedCategory] = useState("Custom");

  const [customTechName, setCustomTechName] = useState("");
  const [customTechGroup, setCustomTechGroup] = useState("Custom");

  const [industries, setIndustries] = useState([]);
  const [geoLocations, setGeoLocations] = useState([]);
  const [technologyStack, setTechnologyStack] = useState([]);

  const [dateMode, setDateMode] = useState("today");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [articleUrl, setArticleUrl] = useState("");

  const [loading, setLoading] = useState(false);
  const [hypothesis, setHypothesis] = useState(null);

  const isArticleMode = hypothesisMode === "article";
  const hasMinimumInput =
    industries.length > 0 ||
    geoLocations.length > 0 ||
    technologyStack.length > 0 ||
    dateMode !== "any";
  const hasArticleUrl = articleUrl.trim().length > 0;

  const loadSettings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings`);
      const data = await response.json();

      setFeeds(data.rss_feeds || []);
      setCustomTechnologies(data.custom_technologies || []);
    } catch {
      alert("Failed to load saved settings from backend.");
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const addFeed = async () => {
    if (!feedName.trim() || !feedUrl.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/rss/feeds`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: feedName.trim(),
          url: feedUrl.trim(),
          category: feedCategory.trim() || "Custom",
          enabled: true
        })
      });

      const data = await response.json();

      if (data.status === "success") {
        setFeeds(data.rss_feeds || []);
        setFeedName("");
        setFeedUrl("");
        setFeedCategory("Custom");
      } else {
        alert(data.message || "Failed to add RSS feed.");
      }
    } catch {
      alert("Failed to add RSS feed. Backend may be unreachable.");
    }
  };

  const toggleFeed = async (feedId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rss/feeds/${feedId}/toggle`, {
        method: "PUT"
      });

      const data = await response.json();

      if (data.status === "success") {
        setFeeds(data.rss_feeds || []);
      } else {
        alert(data.message || "Failed to update RSS feed.");
      }
    } catch {
      alert("Failed to update RSS feed. Backend may be unreachable.");
    }
  };

  const removeFeed = async (feedId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rss/feeds/${feedId}`, {
        method: "DELETE"
      });

      const data = await response.json();

      if (data.status === "success") {
        setFeeds(data.rss_feeds || []);
      } else {
        alert(data.message || "Failed to delete RSS feed.");
      }
    } catch {
      alert("Failed to delete RSS feed. Backend may be unreachable.");
    }
  };

  const testFeed = async (feed) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rss/test`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(feed)
      });

      const data = await response.json();

      alert(
        data.status === "success"
          ? `Feed working: ${data.feed_title}`
          : `Feed failed: ${data.message}`
      );
    } catch {
      alert("Feed test failed. Backend may be unreachable.");
    }
  };

  const addCustomTechnology = async () => {
    if (!customTechName.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/technologies`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: customTechName.trim(),
          group: customTechGroup.trim() || "Custom"
        })
      });

      const data = await response.json();

      if (data.status === "success") {
        setCustomTechnologies(data.custom_technologies || []);
        setCustomTechName("");
        setCustomTechGroup("Custom");
      } else {
        alert(data.message || "Failed to add technology.");
      }
    } catch {
      alert("Failed to add technology. Backend may be unreachable.");
    }
  };

  const deleteCustomTechnology = async (technologyId, technologyName) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/technologies/${technologyId}`, {
        method: "DELETE"
      });

      const data = await response.json();

      if (data.status === "success") {
        setCustomTechnologies(data.custom_technologies || []);
        setTechnologyStack(technologyStack.filter((item) => item !== technologyName));
      } else {
        alert(data.message || "Failed to delete technology.");
      }
    } catch {
      alert("Failed to delete technology. Backend may be unreachable.");
    }
  };

  const generateHypothesis = async () => {
    setLoading(true);
    setHypothesis(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/hypothesis/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          sector: industries.join(", "),
          geo_location: geoLocations.join(", "),
          technology_stack: technologyStack,
          threat_date: dateMode,
          date_from: dateFrom,
          date_to: dateTo
        })
      });

      const data = await response.json();
      setHypothesis(data);
    } catch {
      setHypothesis({
        error: "Failed to generate hypothesis. Check backend and Ollama containers."
      });
    } finally {
      setLoading(false);
    }
  };

  const generateArticleHypothesis = async () => {
    if (!hasArticleUrl) return;

    setLoading(true);
    setHypothesis(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/hypothesis/article`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          url: articleUrl.trim()
        })
      });

      const data = await response.json();
      setHypothesis(data);
    } catch {
      setHypothesis({
        error: "Failed to generate hypothesis from article URL. Check backend and Ollama containers."
      });
    } finally {
      setLoading(false);
    }
  };

  const changeMode = (mode) => {
    setHypothesisMode(mode);
    setHypothesis(null);
  };

  const exportReport = () => {
    if (!hypothesis?.report) return;

    const heading = getHypothesisHeading(hypothesis.report);
    const pdf = createReportPdf(hypothesis.report, heading);
    const blob = new Blob([pdf], {
      type: "application/pdf"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `${slugifyFilename(heading)}.pdf`;
    link.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="app">
      <nav className="top-nav">
        <div className="brand-mark">TH</div>

        <div className="nav-title">
          <span>Threat Hunting</span>
          <strong>Hypothesis Generator</strong>
        </div>

        <button className="settings-btn" onClick={() => setSettingsOpen(true)}>
          Settings
        </button>
      </nav>

      <section className="hero-band">
        <div className="hero-content">
          <p className="eyebrow">AI-Assisted Threat Intelligence</p>
          <h1>Generate hunting hypotheses from current context or one article.</h1>
          <p>
            Start with current context, technology stack, geography, and sector,
            or switch to a single cybersecurity article URL.
          </p>
        </div>
      </section>

      <div className="mode-toggle-wrap">
        <div className="mode-toggle" aria-label="Hypothesis generation mode">
          <button
            className={!isArticleMode ? "mode-active" : ""}
            onClick={() => changeMode("context")}
          >
            Current Context
          </button>

          <button
            className={isArticleMode ? "mode-active" : ""}
            onClick={() => changeMode("article")}
          >
            Article URL
          </button>
        </div>
      </div>

      <main className="main-grid">
        {!isArticleMode && (
        <section className="panel context-panel">
          <p className="section-label">Organization Context</p>
          <h2>Input Scope</h2>

          <div className="date-card">
            <label>Threat Date Range</label>

            <div className="date-options">
              <button
                className={dateMode === "any" ? "date-active" : ""}
                onClick={() => setDateMode("any")}
              >
                Any Date
              </button>

              <button
                className={dateMode === "today" ? "date-active" : ""}
                onClick={() => setDateMode("today")}
              >
                Today
              </button>

              <button
                className={dateMode === "yesterday" ? "date-active" : ""}
                onClick={() => setDateMode("yesterday")}
              >
                Yesterday
              </button>

              <button
                className={dateMode === "custom" ? "date-active" : ""}
                onClick={() => setDateMode("custom")}
              >
                Custom Range
              </button>
            </div>

            {dateMode === "custom" && (
              <div className="custom-date-row">
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                />

                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                />
              </div>
            )}
          </div>

          <MultiSelectDropdown
            label="Industry / Sector"
            options={INDUSTRY_OPTIONS}
            selected={industries}
            setSelected={setIndustries}
          />

          <MultiSelectDropdown
            label="Geo Location"
            options={GEO_OPTIONS}
            selected={geoLocations}
            setSelected={setGeoLocations}
          />

          <TechnologyDropdown
            selected={technologyStack}
            setSelected={setTechnologyStack}
            customTechnologies={customTechnologies}
          />

          <button
            className="primary-cta"
            disabled={loading || !hasMinimumInput}
            onClick={generateHypothesis}
          >
            {loading ? "Generating..." : "Generate Hypothesis"}
          </button>

          {!hasMinimumInput && (
            <p className="hint">
              Select at least one option: date, industry, geo location, or
              technology stack.
            </p>
          )}
        </section>
        )}

        {isArticleMode && (
        <section className="panel context-panel article-panel">
          <p className="section-label">Single Article URL</p>
          <h2>Article Scope</h2>

          <label className="url-label" htmlFor="article-url">
            Cybersecurity Blog or Article URL
          </label>

          <input
            id="article-url"
            className="article-url-input"
            type="url"
            placeholder="https://example.com/security-research/article"
            value={articleUrl}
            onChange={(event) => setArticleUrl(event.target.value)}
          />

          <button
            className="primary-cta"
            disabled={loading || !hasArticleUrl}
            onClick={generateArticleHypothesis}
          >
            {loading ? "Extracting..." : "Generate Hypothesis"}
          </button>

          {!hasArticleUrl && (
            <p className="hint">
              Paste the article URL to fetch, extract, and generate a hunting hypothesis.
            </p>
          )}
        </section>
        )}

        <section className="panel output-panel">
          <div className="output-header">
            <div>
              <p className="section-label">Hypothesis Generator</p>
              <h2>Generated Report</h2>
            </div>

            {hypothesis?.report && (
              <button className="outline-cta" onClick={exportReport}>
                Export Report
              </button>
            )}
          </div>

          {!hypothesis && (
            <div className="empty-state">
              <h3>No hypothesis generated yet.</h3>
              <p>
                {isArticleMode
                  ? "Paste a cybersecurity article URL and run the generator."
                  : "Configure the context and run the generator. Supporting RSS articles will appear below the final report."}
              </p>
            </div>
          )}

          {hypothesis?.error && <p className="error">{hypothesis.error}</p>}

          {hypothesis?.report && <pre className="report-box">{hypothesis.report}</pre>}

          {hypothesis?.articles?.length > 0 && (
            <div className="supporting-articles">
              <h3>Supporting Threat Articles</h3>

              <ul>
                {hypothesis.articles.map((article, index) => (
                  <li key={index}>
                    <a href={article.link} target="_blank" rel="noreferrer">
                      {article.title}
                    </a>
                    <small>
                      {article.feed} {article.published && `| ${article.published}`}
                    </small>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </main>

      {settingsOpen && (
        <div className="modal-backdrop">
          <div className="settings-modal">
            <div className="modal-header">
              <div>
                <p className="section-label">Settings</p>
                <h2>RSS Feed Manager</h2>
              </div>

              <button className="close-btn" onClick={() => setSettingsOpen(false)}>
                Close
              </button>
            </div>

            <div className="settings-section">
              <h3>Add RSS Feed</h3>

              <div className="feed-form">
                <input
                  placeholder="Feed name"
                  value={feedName}
                  onChange={(e) => setFeedName(e.target.value)}
                />

                <input
                  placeholder="RSS feed URL"
                  value={feedUrl}
                  onChange={(e) => setFeedUrl(e.target.value)}
                />

                <input
                  placeholder="Category"
                  value={feedCategory}
                  onChange={(e) => setFeedCategory(e.target.value)}
                />

                <button className="primary-cta small" onClick={addFeed}>
                  Add Feed
                </button>
              </div>

              <div className="feed-list">
                {feeds.map((feed) => (
                  <div className="feed-item" key={feed.id}>
                    <div>
                      <strong>{feed.name}</strong>
                      <p>{feed.url}</p>

                      <div className="feed-badges">
                        <span>{feed.category}</span>
                        <span className={feed.enabled ? "status-on" : "status-off"}>
                          {feed.enabled ? "Enabled" : "Disabled"}
                        </span>
                      </div>
                    </div>

                    <div className="feed-actions">
                      <button onClick={() => toggleFeed(feed.id)}>
                        {feed.enabled ? "Disable" : "Enable"}
                      </button>

                      <button onClick={() => testFeed(feed)}>Test</button>

                      <button className="danger-btn" onClick={() => removeFeed(feed.id)}>
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="settings-section">
              <h3>Custom Technology Stack</h3>

              <div className="feed-form">
                <input
                  placeholder="Technology name, example: FortiEDR"
                  value={customTechName}
                  onChange={(e) => setCustomTechName(e.target.value)}
                />

                <input
                  placeholder="Group, example: Security Tools"
                  value={customTechGroup}
                  onChange={(e) => setCustomTechGroup(e.target.value)}
                />

                <button className="primary-cta small" onClick={addCustomTechnology}>
                  Add Technology
                </button>
              </div>

              <div className="feed-list">
                {customTechnologies.length === 0 && (
                  <p className="hint">No custom technologies added yet.</p>
                )}

                {customTechnologies.map((technology) => (
                  <div className="feed-item" key={technology.id}>
                    <div>
                      <strong>{technology.name}</strong>

                      <div className="feed-badges">
                        <span>{technology.group}</span>
                      </div>
                    </div>

                    <div className="feed-actions">
                      <button
                        className="danger-btn"
                        onClick={() =>
                          deleteCustomTechnology(technology.id, technology.name)
                        }
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

export default App;

