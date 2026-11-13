const root = document.querySelector("#local-authority-explorer");
const dataUrl = new URL("../data/derived/local_authority_history.json", import.meta.url);
const svgNS = "http://www.w3.org/2000/svg";
const medianColor = "#247367";
const lowerColor = "#d68d38";
const yearTicks = [1997, 2000, 2005, 2010, 2015, 2020, 2025];

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function svgElement(tag, attributes = {}, text) {
  const node = document.createElementNS(svgNS, tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, String(value));
  if (text !== undefined) node.textContent = text;
  return node;
}

function latestValue(series) {
  const years = Object.keys(series).map(Number).sort((a, b) => b - a);
  const year = years.find(candidate => Number.isFinite(series[String(candidate)]));
  return year === undefined ? null : { year, value: series[String(year)] };
}

function formatRatio(value) {
  return Number.isFinite(value) ? `${value.toFixed(2)}x` : "No estimate";
}

function metric(label, result) {
  const card = element("div", "authority-metric");
  card.append(element("span", "authority-metric-label", label));
  card.append(element("strong", "authority-metric-value", result ? formatRatio(result.value) : "No estimate"));
  card.append(element("span", "authority-metric-year", result ? `Latest available: ${result.year}` : "No available year"));
  return card;
}

function pathFor(years, series, x, y) {
  let path = "";
  let drawing = false;
  years.forEach((year, index) => {
    const value = series[String(year)];
    if (!Number.isFinite(value)) {
      drawing = false;
      return;
    }
    path += `${drawing ? "L" : "M"}${x(index)},${y(value)} `;
    drawing = true;
  });
  return path.trim();
}

function drawChart(svg, years, area) {
  const width = 820, height = 420;
  const margin = { top: 26, right: 28, bottom: 62, left: 76 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const allValues = [...Object.values(area.median), ...Object.values(area.lower_quartile)].filter(Number.isFinite);
  const maxValue = Math.max(10, Math.ceil(Math.max(...allValues, 5) / 5) * 5);
  const x = index => margin.left + index * plotWidth / (years.length - 1);
  const y = value => margin.top + plotHeight - value * plotHeight / maxValue;

  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-labelledby", "area-chart-title area-chart-description");
  svg.append(svgElement("title", { id: "area-chart-title" }, `${area.name}: affordability ratios over time`));
  svg.append(svgElement("desc", { id: "area-chart-description" }, "Annual median-price and lower-quartile-price ratios compared with workplace earnings from 1997 to 2025."));

  const step = maxValue <= 20 ? 5 : 10;
  for (let value = 0; value <= maxValue; value += step) {
    svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: y(value), y2: y(value), class: "chart-grid" }));
    svg.append(svgElement("text", { x: margin.left - 12, y: y(value) + 4, "text-anchor": "end", class: "chart-tick" }, String(value)));
  }
  if (maxValue >= 5) {
    svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: y(5), y2: y(5), class: "chart-benchmark" }));
    svg.append(svgElement("text", { x: margin.left + 8, y: y(5) - 8, class: "chart-benchmark-label" }, "5x broad indicator"));
  }
  yearTicks.forEach(year => {
    const index = years.indexOf(year);
    if (index < 0) return;
    svg.append(svgElement("line", { x1: x(index), x2: x(index), y1: height - margin.bottom, y2: height - margin.bottom + 5, class: "chart-axis" }));
    svg.append(svgElement("text", { x: x(index), y: height - margin.bottom + 25, "text-anchor": "middle", class: "chart-tick" }, String(year)));
  });
  svg.append(svgElement("line", { x1: margin.left, x2: margin.left, y1: margin.top, y2: height - margin.bottom, class: "chart-axis" }));
  svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: height - margin.bottom, y2: height - margin.bottom, class: "chart-axis" }));
  svg.append(svgElement("text", { x: 20, y: margin.top + plotHeight/2, transform: `rotate(-90 20 ${margin.top + plotHeight/2})`, "text-anchor": "middle", class: "chart-axis-label" }, "Ratio (times annual gross earnings)"));
  svg.append(svgElement("path", { d: pathFor(years, area.median, x, y), class: "chart-line chart-line-median" }));
  svg.append(svgElement("path", { d: pathFor(years, area.lower_quartile, x, y), class: "chart-line chart-line-lower" }));
}

function showArea(area, years, summary, chart, status) {
  const median = latestValue(area.median);
  const lower = latestValue(area.lower_quartile);
  const stats = element("div", "authority-metrics");
  stats.append(metric("Median price / median earnings", median));
  stats.append(metric("Lower-quartile price / lower-quartile earnings", lower));
  const change = Number.isFinite(area.median["2024"]) && Number.isFinite(area.median["2025"])
    ? area.median["2025"] - area.median["2024"] : null;
  const changeCard = element("div", "authority-metric");
  changeCard.append(element("span", "authority-metric-label", "Median-ratio change, 2024 to 2025"));
  changeCard.append(element("strong", "authority-metric-value", change === null ? "Unavailable" : `${change > 0 ? "+" : ""}${change.toFixed(2)}x`));
  changeCard.append(element("span", "authority-metric-year", change === null ? "No comparable 2025 value" : change < 0 ? "Ratio fell" : change > 0 ? "Ratio rose" : "No change"));
  stats.append(changeCard);
  summary.replaceChildren(stats);
  drawChart(chart, years, area);
  status.textContent = `${area.name}, ${area.country}. Showing annual estimates from ${years[0]} to ${years[years.length - 1]}.`;
}

async function start() {
  if (!root) return;
  try {
    const response = await fetch(dataUrl, { cache: "force-cache" });
    if (!response.ok) throw new Error(`Area data could not be loaded (HTTP ${response.status}).`);
    const payload = await response.json();
    const areas = payload.areas.slice().sort((a, b) => a.name.localeCompare(b.name, "en-GB"));
    const label = element("label", "authority-select-label", "Choose a local authority");
    const select = element("select", "authority-select");
    select.id = "authority-select";
    select.setAttribute("aria-label", "Choose a local authority");
    for (const area of areas) select.append(new Option(`${area.name} (${area.country})`, area.code));
    const controls = element("div", "authority-controls");
    controls.append(label, select);
    const status = element("p", "authority-status");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const summary = element("div", "authority-summary");
    const chartWrap = element("div", "authority-chart-wrap");
    const chart = svgElement("svg", { class: "authority-chart", focusable: "false" });
    chartWrap.append(chart);
    const legend = element("div", "authority-legend");
    legend.append(element("span", "legend-item legend-median", "Median price / median earnings"));
    legend.append(element("span", "legend-item legend-lower", "Lower-quartile price / lower-quartile earnings"));
    const note = element("p", "authority-chart-note", "A higher ratio means a larger price relative to gross workplace earnings. Estimates are annual and may be revised by the ONS.");
    root.replaceChildren(controls, status, summary, legend, chartWrap, note);
    const update = () => {
      const area = areas.find(item => item.code === select.value);
      if (area) showArea(area, payload.years, summary, chart, status);
    };
    select.addEventListener("change", update);
    update();
  } catch (error) {
    root.replaceChildren(element("p", "explorer-error", error instanceof Error ? error.message : "The local-authority series could not be loaded."));
  }
}

start();
