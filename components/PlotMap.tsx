"use client";

import Plot from "react-plotly.js";

type Point = {
  lat: number;
  long: number;
  localArea: string;
  group: string;
  statusGroup: string;
};

export default function PlotMap({
  businessType,
  localArea,
  points,
}: {
  businessType: string;
  localArea: string;
  points: Point[];
}) {
  const data = [
    {
      x: points.map((p) => p.long),
      y: points.map((p) => p.lat),
      text: points.map((p) => `${p.localArea}`),
      mode: "markers",
      type: "scatter",
      marker: {
        size: 8,
        opacity: 0.6,
      },
      transforms: [
        {
          type: "groupby",
          groups: points.map((p) => p.group),
        },
      ],
    },
  ];

  return (
    <Plot
      data={data as any}
      layout={{
        title: { text: `${businessType} in ${localArea} vs Vancouver` },
        xaxis: {
          title: { text: "Longitude" },
          color: "#e5e7eb",
          gridcolor: "#1f2937",
        },
        yaxis: {
          title: { text: "Latitude" },
          color: "#e5e7eb",
          gridcolor: "#1f2937",
        },
        paper_bgcolor: "#020617",
        plot_bgcolor: "#020617",
        font: { color: "#f9fafb" },
        height: 600,
        autosize: true,
      }}
      style={{ width: "100%", height: "100%" }}
      config={{ responsive: true }}
    />
  );
}

