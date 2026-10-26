const DATA_URL = "./data/public.json";
const currencyCode = "GBP";

function formatMoney(value, currency = currencyCode) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "Not published";
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency,
    maximumFractionDigits: 2
  }).format(value);
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function formatDate(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const date = new Date(`${value}T12:00:00Z`);
  return Number.isNaN(date.getTime())
    ? null
    : new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(date);
}

function renderTrajectory(items, currency) {
  const list = document.getElementById("trajectory-list");
  const empty = document.getElementById("trajectory-empty");
  if (!list || !empty) return;

  const validItems = Array.isArray(items)
    ? items.filter(item => item && formatDate(item.date) && typeof item.total_debt === "number" && Number.isFinite(item.total_debt))
    : [];

  list.replaceChildren();
  if (!validItems.length) {
    list.hidden = true;
    empty.hidden = false;
    return;
  }

  validItems.sort((a, b) => a.date.localeCompare(b.date));
  for (const item of validItems) {
    const row = document.createElement("li");
    row.className = "trajectory-item";
    const date = document.createElement("span");
    date.className = "trajectory-date";
    date.textContent = formatDate(item.date);
    const balance = document.createElement("span");
    balance.className = "trajectory-balance";
    balance.textContent = formatMoney(item.total_debt, currency);
    row.append(date, balance);
    list.append(row);
  }
  list.hidden = false;
  empty.hidden = true;
}

async function loadPublicData() {
  try {
    const response = await fetch(DATA_URL, { cache: "no-store", headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Public summary is not available.");
    const data = await response.json();
    const currency = typeof data.currency === "string" && /^[A-Z]{3}$/.test(data.currency) ? data.currency : currencyCode;
    const summary = data.summary && typeof data.summary === "object" ? data.summary : {};

    setText("total-debt", formatMoney(summary.total_debt, currency));
    setText("monthly-income", formatMoney(summary.monthly_income, currency));
    setText("essential-costs", formatMoney(summary.monthly_essential_costs, currency));
    setText("repayment-capacity", formatMoney(summary.monthly_repayment_capacity, currency));

    const period = typeof data.reporting_period === "string" && data.reporting_period.trim()
      ? data.reporting_period
      : "not published";
    setText("reporting-period", `Reporting period: ${period}.`);

    const reviewedDate = formatDate(data.last_reviewed);
    setText("last-updated", `Last reviewed: ${reviewedDate || "not published"}.`);

    const published = data.status === "published" && reviewedDate;
    setText("data-status", published
      ? `Reviewed public summary · ${reviewedDate}`
      : "Public figures have not been published yet.");

    renderTrajectory(data.trajectory, currency);
  } catch {
    setText("data-status", "Public figures are currently unavailable.");
    setText("reporting-period", "Reporting period: not available.");
    setText("last-updated", "Last reviewed: not available.");
  }
}

loadPublicData();
