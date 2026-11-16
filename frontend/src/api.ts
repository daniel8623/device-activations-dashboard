export type Summary = {
  today: number;
  week: number;
  month: number;
  year: number;
  timezone: string;
};

export type Granularity = "day" | "week" | "month" | "year";

export type TimeseriesPoint = {
  bucket_start: string; // "YYYY-MM-DD", start of the period in Israel time
  count: number;
};

export type Timeseries = {
  granularity: Granularity;
  timezone: string;
  points: TimeseriesPoint[];
};

export async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return (await response.json()) as T;
}