"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import "./globals.css";

const Plot = dynamic(() => import("../components/PlotMap"), { ssr: false });

type MarketResult = {
  business_type: string;
  local_area: string;
  concentration_score: number;
  concentration_level: string;
  closure_risk_score: number;
  closure_risk_level: string;
  recency_score: number | null;
  recency_level: string;
  interpretation_title: string;
  interpretation_summary: string;
};

type Point = {
  lat: number;
  long: number;
  localArea: string;
  group: string;
  statusGroup: string;
};

type OptionsResponse = {
  businessTypes: string[];
  localAreas: string[];
};

export default function HomePage() {
  const [options, setOptions] = useState<OptionsResponse | null>(null);
  const [businessType, setBusinessType] = useState("");
  const [localArea, setLocalArea] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MarketResult | null>(null);
  const [points, setPoints] = useState<Point[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadOptions() {
      try {
        const res = await fetch("/api/analyze");
        if (!res.ok) throw new Error("Failed to load options");
        const data: OptionsResponse = await res.json();
        setOptions(data);
        if (data.businessTypes.length > 0) {
          setBusinessType(data.businessTypes[0]);
        }
        if (data.localAreas.length > 0) {
          setLocalArea(data.localAreas[0]);
        }
      } catch (e) {
        console.error(e);
        setError("Unable to load options.");
      }
    }
    loadOptions();
  }, []);

  async function runAnalysis() {
    if (!businessType || !localArea) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ businessType, localArea }),
      });
      if (!res.ok) throw new Error("Failed to run analysis");
      const data = await res.json();
      setResult(data.result);
      setPoints(data.points);
    } catch (e) {
      console.error(e);
      setError("Unable to run analysis.");
    } finally {
      setLoading(false);
    }
  }

  const renderLevel = (level: string) => {
    const colors: Record<string, { bg: string; fg: string }> = {
      Low: { bg: "#c3e6cb", fg: "#155724" },
      Typical: { bg: "#f2f2f2", fg: "#333333" },
      High: { bg: "#f5c6cb", fg: "#721c24" },
    };
    const { bg, fg } = colors[level] ?? colors["Typical"];
    return (
      <span
        style={{
          display: "inline-block",
          padding: "6px 10px",
          borderRadius: 999,
          background: bg,
          color: fg,
          fontWeight: 600,
          fontSize: "0.9rem",
          border: "1px solid rgba(0,0,0,0.08)",
        }}
      >
        {level}
      </span>
    );
  };

  return (
    <main className="page">
      <header className="header">
        <h1>Vancouver Business Registrations: Inferences for Market Interpretation</h1>
        <h3>David Chang</h3>
        <p>
          This tool uses City of Vancouver business registration data to help interpret local market
          conditions for different business types across neighbourhoods. By combining measures of{" "}
          <strong>concentration</strong>, <strong>closure risk</strong>, and{" "}
          <strong>recency of openings</strong>, it infers a narrative about competition, stability,
          and momentum in a given area.
        </p>
      </header>

      <section className="hero">
        <img
          src="https://images.pexels.com/photos/29072584/pexels-photo-29072584.jpeg"
          alt="Vancouver Skyline"
        />
        <div className="hero-caption">
          Vancouver Skyline (Credit: Luke Lawreszuk)
        </div>
      </section>

      {options && (
        <section className="controls">
          <label>
            Business Type
            <select
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
            >
              {options.businessTypes.map((bt) => (
                <option key={bt} value={bt}>
                  {bt}
                </option>
              ))}
            </select>
          </label>

          <label>
            Neighbourhood (LocalArea)
            <select
              value={localArea}
              onChange={(e) => setLocalArea(e.target.value)}
            >
              {options.localAreas.map((la) => (
                <option key={la} value={la}>
                  {la}
                </option>
              ))}
            </select>
          </label>

          <button onClick={runAnalysis} disabled={loading}>
            {loading ? "Running..." : "Run"}
          </button>
        </section>
      )}

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="results">
          <h2>{result.interpretation_title}</h2>
          <p>{result.interpretation_summary}</p>

          <h3>Scores</h3>
          <div className="scores-grid">
            <div className="score-row">
              <div>
                <div className="metric-label">Concentration score</div>
                <div className="metric-value">
                  {result.concentration_score.toFixed(2)}
                </div>
              </div>
              <div>{renderLevel(result.concentration_level)}</div>
              <a href="#concentration" className="how-link">
                How was this calculated?
              </a>
            </div>

            <div className="score-row">
              <div>
                <div className="metric-label">Closure risk score</div>
                <div className="metric-value">
                  {result.closure_risk_score.toFixed(2)}
                </div>
              </div>
              <div>{renderLevel(result.closure_risk_level)}</div>
              <a href="#closure-risk" className="how-link">
                How was this calculated?
              </a>
            </div>

            <div className="score-row">
              <div>
                <div className="metric-label">Recency score</div>
                <div className="metric-value">
                  {result.recency_score === null
                    ? "N/A"
                    : result.recency_score.toFixed(2)}
                </div>
              </div>
              <div>{renderLevel("Typical")}</div>
              <a href="#recency" className="how-link">
                How was this calculated?
              </a>
            </div>
          </div>
        </section>
      )}

      {points.length > 0 && (
        <section className="map-section">
          <Plot businessType={businessType} localArea={localArea} points={points} />
        </section>
      )}

      <section className="about">
        <h2>About this Project</h2>
        <p>
          The City of Vancouver has a rich and diverse business landscape, represented by a dataset
          in their Open Data Portal. This dataset holds records of business registrations from 2024
          onwards (over 130,000 registrations). This app uses that dataset to make inferences about
          the market as a whole.
        </p>

        <div id="concentration" className="metric-explainer">
          <h3>Concentration Score</h3>
          <p>
            The concentration score measures how common a given business type is in a specific
            neighbourhood, relative to how common it is across Vancouver as a whole.
          </p>
          <p>
            First, compute the proportion of all issued businesses in that neighbourhood that are of
            the selected business type. Then compute the proportion of all issued businesses
            citywide that are of that same business type. The concentration score is the ratio of
            these two proportions.
          </p>
        </div>

        <div id="closure-risk" className="metric-explainer">
          <h3>Closure Risk Score</h3>
          <p>
            The closure risk score measures how likely businesses of a given type are to close or
            become inactive in a specific neighbourhood, relative to the citywide norm for that
            business type.
          </p>
        </div>

        <div id="recency" className="metric-explainer">
          <h3>Recency Score</h3>
          <p>
            The recency score captures how recently new businesses of a given type have been
            opening in a neighbourhood, compared to the citywide trend. It focuses on recent
            momentum by looking at the most recent one-seventh of issued registrations.
          </p>
        </div>
      </section>
    </main>
  );
}

