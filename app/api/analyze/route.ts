import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

type RecordRow = {
  BusinessType: string;
  LocalArea: string;
  Status: string;
  geo_point_2d: string;
  IssuedDate: string;
};

type DataContext = {
  dfFiltered: RecordRowEnriched[];
  dfIssued: RecordRowEnriched[];
  bigTypes: string[];
  localAreas: string[];
  todayRef: Date;
};

type RecordRowEnriched = RecordRow & {
  lat: number;
  long: number;
  IssuedDate_dt: Date | null;
};

let cachedContext: DataContext | null = null;

function loadCsvOnce(): DataContext {
  if (cachedContext) return cachedContext;

  const csvPath = path.join(process.cwd(), "business-licences.csv");
  const raw = fs.readFileSync(csvPath, "utf8");

  const lines = raw.split(/\r?\n/).filter((l) => l.trim().length > 0);
  const header = lines[0].split(";");
  const rows: RecordRow[] = [];

  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(";");
    const rowObj: any = {};
    header.forEach((h, idx) => {
      rowObj[h] = cols[idx] ?? "";
    });
    rows.push(rowObj as RecordRow);
  }

  const filtered0 = rows
    .map((r) => {
      let localArea = r.LocalArea;
      if (localArea === "Arbutus Ridge") localArea = "Arbutus-Ridge";
      return { ...r, LocalArea: localArea };
    })
    .filter((r) => r.LocalArea !== "UBC")
    .filter((r) => r.geo_point_2d && r.geo_point_2d.trim().length > 0)
    .map((r) => {
      const [latStr, longStr] = r.geo_point_2d.split(",");
      const lat = parseFloat(latStr);
      const long = parseFloat(longStr);
      const issuedDate = r.IssuedDate;
      const dt =
        issuedDate && issuedDate.trim()
          ? new Date(issuedDate)
          : null;
      return { ...r, lat, long, IssuedDate_dt: dt } as RecordRowEnriched;
    });

  const dropTypes = new Set<string>([
    "Information Communication Technology",
    "Digital Entertainment and Interactive Technology",
    "Publishing and Journalism Services",
    "Marketing Public Relations Advertising and Event Promotion Services",
    "Consulting and Management Services",
    "Business Support Services",
    "Design Services",
    "Architectural and Engineering Services",
    "Legal Services",
    "Insurance Services",
    "Financial Services",
    "Financial Institution",
    "Brokerage Services",
    "Real Estate Services",
    "Artist Agency",
    "Association or Society",
    "Mining Services",
    "Forestry Services",
    "Oil Gas and Other Fuels",
    "Logistics Services",
    "Transportation and Support Services",
    "Warehouse Operator - Food",
    "Warehouse Operator - Non-Food",
    "Wholesale Dealer - Food",
    "Wholesale Dealer - Non-Food",
    "Non-Food Manufacturer Assembler and Processor",
    "Food Manufacturer Assembler and Processor",
    "Recycling and Resource Recovery Services",
    "Waste Collection and Hauling Services",
    "Marine Service Station",
    "Soliciting For Charity",
    "Cannabis Licence Application",
    "Liquor License Application",
    "Temp Liquor Licence Amendment",
    "Adult Retail Store *Historic*",
  ]);

  const dfFiltered0 = filtered0.filter((r) => !dropTypes.has(r.BusinessType));

  const infrastructureTypes = new Set<string>([
    "Mining Services",
    "Forestry Services",
    "Oil Gas and Other Fuels",
    "Logistics Services",
    "Transportation and Support Services",
    "Warehouse Operator - Food",
    "Warehouse Operator - Non-Food",
    "Wholesale Dealer - Food",
    "Wholesale Dealer - Non-Food",
    "Non-Food Manufacturer Assembler and Processor",
    "Food Manufacturer Assembler and Processor",
    "Recycling and Resource Recovery Services",
    "Waste Collection and Hauling Services",
    "Marine Service Station",
    "Parking Area / Garage",
  ]);

  const dfFiltered1 = dfFiltered0.filter(
    (r) => !infrastructureTypes.has(r.BusinessType)
  );

  const typeCounts: Record<string, number> = {};
  for (const r of dfFiltered1) {
    typeCounts[r.BusinessType] = (typeCounts[r.BusinessType] ?? 0) + 1;
  }

  const bigTypes = Object.entries(typeCounts)
    .filter(([, count]) => count > 644)
    .map(([name]) => name)
    .sort();

  const dfFiltered = dfFiltered1.filter((r) => bigTypes.includes(r.BusinessType));
  const dfIssued = dfFiltered.filter((r) => r.Status === "Issued");

  const localAreas = Array.from(
    new Set(dfFiltered.map((r) => r.LocalArea).filter((v) => v && v.length > 0))
  ).sort();

  const issuedDates = dfIssued
    .map((r) => r.IssuedDate_dt)
    .filter((d): d is Date => d instanceof Date && !isNaN(d.getTime()));
  const todayRef =
    issuedDates.length > 0 ? new Date(Math.max(...issuedDates.map((d) => d.getTime()))) : new Date();

  cachedContext = {
    dfFiltered,
    dfIssued,
    bigTypes,
    localAreas,
    todayRef,
  };

  return cachedContext;
}

function concentrationScore(
  ctx: DataContext,
  businessType: string,
  localArea: string
): number {
  const dfIssued = ctx.dfIssued;

  const A = dfIssued.filter(
    (r) => r.BusinessType === businessType && r.LocalArea === localArea
  ).length;
  const B = dfIssued.filter((r) => r.LocalArea === localArea).length;
  const C = dfIssued.filter((r) => r.BusinessType === businessType).length;
  const D = dfIssued.length;

  if (B === 0 || D === 0 || C === 0) return 0;

  const locationProp = A / B;
  const totalProp = C / D;
  if (totalProp === 0) return 0;
  return locationProp / totalProp;
}

const goneStatuses = new Set(["Gone Out of Business", "Inactive"]);

function relativeClosureRisk(
  ctx: DataContext,
  businessType: string,
  localArea: string
): number {
  const { dfIssued, dfFiltered } = ctx;

  const countActive = dfIssued.filter(
    (r) => r.BusinessType === businessType && r.LocalArea === localArea
  ).length;

  const countClosure = dfFiltered.filter(
    (r) =>
      r.BusinessType === businessType &&
      r.LocalArea === localArea &&
      goneStatuses.has(r.Status)
  ).length;

  if (countActive === 0) return 0;

  const closureRate = countClosure / countActive;

  const cityActive = dfIssued.filter((r) => r.BusinessType === businessType).length;
  const cityClosure = dfFiltered.filter(
    (r) => r.BusinessType === businessType && goneStatuses.has(r.Status)
  ).length;
  if (cityActive === 0) return 0;
  const baselineClosureRate = cityClosure / cityActive;
  if (baselineClosureRate === 0) return 0;

  return closureRate / baselineClosureRate;
}

function relativeRecency(
  ctx: DataContext,
  businessType: string,
  localArea: string
): number | null {
  const dfDate = ctx.dfIssued.filter(
    (r) => r.IssuedDate_dt instanceof Date && !isNaN(r.IssuedDate_dt.getTime())
  );
  const todayRef = ctx.todayRef;

  function meanOfRecentFraction(sub: RecordRowEnriched[]): {
    k: number;
    meanDt: Date | null;
  } {
    const n = sub.length;
    if (n === 0) return { k: 0, meanDt: null };
    const k = Math.ceil((1 / 7) * n);
    const recent = [...sub].sort(
      (a, b) =>
        (b.IssuedDate_dt?.getTime() ?? 0) - (a.IssuedDate_dt?.getTime() ?? 0)
    ).slice(0, k);
    const times = recent
      .map((r) => r.IssuedDate_dt)
      .filter((d): d is Date => d instanceof Date && !isNaN(d.getTime()))
      .map((d) => d.getTime());
    if (times.length === 0) return { k, meanDt: null };
    const meanTime = times.reduce((a, b) => a + b, 0) / times.length;
    return { k, meanDt: new Date(meanTime) };
  }

  const localSub = dfDate.filter(
    (r) => r.BusinessType === businessType && r.LocalArea === localArea
  );
  const { meanDt: localMeanDt } = meanOfRecentFraction(localSub);
  if (!localMeanDt) return null;

  const citySub = dfDate.filter((r) => r.BusinessType === businessType);
  const { meanDt: cityMeanDt } = meanOfRecentFraction(citySub);
  if (!cityMeanDt) return null;

  const localAgeDays = (todayRef.getTime() - localMeanDt.getTime()) / (1000 * 86400);
  const baselineAgeDays = (todayRef.getTime() - cityMeanDt.getTime()) / (1000 * 86400);

  if (baselineAgeDays === 0 || localAgeDays === 0) return 0;
  const rel = localAgeDays / baselineAgeDays;
  return 1 / rel;
}

function classifyScore(x: number | null): "Low" | "Typical" | "High" {
  if (x === null) return "Typical";
  if (x < 0.9) return "Low";
  if (x > 1.1) return "High";
  return "Typical";
}

function marketInterpretation(
  ctx: DataContext,
  businessType: string,
  localArea: string
) {
  const concScore = concentrationScore(ctx, businessType, localArea);
  const riskScore = relativeClosureRisk(ctx, businessType, localArea);
  const recencyScore = relativeRecency(ctx, businessType, localArea);

  const concLevel = classifyScore(concScore);
  const riskLevel = classifyScore(riskScore);
  const recencyLevel = classifyScore(recencyScore);

  let title: string;
  let summary: string;

  if (riskLevel === "High") {
    title = "High Risk";
    summary =
      "Businesses of this type close or become inactive here at an unusually high rate. Even if demand appears strong, survivability is poor, making entry risky.";
  } else if (concLevel === "Low" && recencyLevel === "Low") {
    title = "Underserved and Healthy";
    summary =
      "Few competitors and little recent entry activity, with no elevated closure risk. This may indicate unmet demand or white space, though discretion is still required.";
  } else if (concLevel === "Low" && recencyLevel === "High") {
    title = "Emerging Market";
    summary =
      "Historically sparse market with strong recent entry momentum. This suggests early growth, offering opportunity, but not without uncertainty.";
  } else if (concLevel === "High" && recencyLevel === "High") {
    title = "Competitive Growth";
    summary =
      "Crowded market with many recent entrants. Demand may be strong, but competition is intense and success depends on differentiation.";
  } else if (concLevel === "High" && recencyLevel === "Low") {
    title = "Saturated / Mature";
    summary =
      "Crowded market with few recent openings. The market appears mature or slowing, making entry difficult without a clear differentiating factor.";
  } else if (concLevel === "Typical") {
    title = "Typical / Stable Market";
    summary =
      "Market size and structure closely resemble the citywide norm for this business type. No strong directional signals are present, so full discretion must be used.";
  } else {
    title = "Mixed / Ambiguous";
    summary =
      "Signals conflict or are weak. Quantitative metrics alone do not point to a clear conclusion, and qualitative context or external data may be necessary.";
  }

  return {
    business_type: businessType,
    local_area: localArea,
    concentration_score: concScore,
    concentration_level: concLevel,
    closure_risk_score: riskScore,
    closure_risk_level: riskLevel,
    recency_score: recencyScore,
    recency_level: recencyLevel,
    interpretation_title: title,
    interpretation_summary: summary,
  };
}

export async function GET() {
  const ctx = loadCsvOnce();
  return NextResponse.json({
    businessTypes: ctx.bigTypes,
    localAreas: ctx.localAreas,
  });
}

export async function POST(req: NextRequest) {
  const { businessType, localArea } = await req.json();
  const ctx = loadCsvOnce();
  const result = marketInterpretation(ctx, businessType, localArea);

  const dfPlot = ctx.dfFiltered
    .filter((r) => r.BusinessType === businessType)
    .map((r) => {
      let statusGroup = "Other";
      if (r.Status === "Issued") {
        statusGroup = "Issued";
      } else if (goneStatuses.has(r.Status)) {
        statusGroup = "Closure/Inactive";
      }
      let group = "Background";
      if (r.BusinessType === businessType) {
        group = "Citywide Registration";
      }
      if (r.BusinessType === businessType && r.LocalArea === localArea) {
        group = `${localArea} Registration`;
      }
      return {
        lat: r.lat,
        long: r.long,
        localArea: r.LocalArea,
        group,
        statusGroup,
      };
    });

  return NextResponse.json({
    result,
    points: dfPlot,
  });
}

