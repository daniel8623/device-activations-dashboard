import { useEffect, useState } from "react";
import { fetchJson } from "../api";

type FetchState<T> = {
  data: T | null;
  error: string | null;
  loading: boolean;
};

export function useFetch<T>(url: string): FetchState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError(null);
      try {
        setData(await fetchJson<T>(url, controller.signal));
      } catch (err) {
        if (controller.signal.aborted) return; // A newer request replaced this one.
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    load();
    return () => controller.abort();
  }, [url]);

  return { data, error, loading };
}