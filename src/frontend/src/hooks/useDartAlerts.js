import { useCallback, useState } from "react";

const RSS_URL =
  "https://news.google.com/rss/search?q=site:x.com/DARTAlerts+when:7d&hl=en-US&gl=US&ceid=US:en";

function parseRSS(xmlString) {
  const parser = new DOMParser();
  const xml = parser.parseFromString(xmlString, "text/xml");

  const items = Array.from(xml.querySelectorAll("item"));

  return items.map((item) => ({
    title: item.querySelector("title")?.textContent || "",
    link: item.querySelector("link")?.textContent || "",
    pubDate: item.querySelector("pubDate")?.textContent || "",
  }));
}

export function useDartAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch(RSS_URL);
      const text = await res.text();

      const parsed = parseRSS(text);
      setAlerts(parsed);
    } catch (err) {
      setError("Failed to load DART alerts.");
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    alerts,
    loading,
    error,
    fetchAlerts,
  };
}