import { useDeferredValue, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { discoverLore } from "@/features/ai/api/aiApi";
import { LoreCard } from "@/features/lore/components/LoreCard";
import { useLoreEngagement } from "@/features/lore/hooks/useLoreEngagement";

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlQuery = searchParams.get("q") ?? "";
  const initialQuery = urlQuery;
  const [query, setQuery] = useState(initialQuery);
  const [submittedQuery, setSubmittedQuery] = useState(initialQuery);
  const deferredQuery = useDeferredValue(submittedQuery);
  const results = useQuery({
    queryKey: ["ai", "discover", deferredQuery],
    queryFn: () => discoverLore(deferredQuery),
    enabled: deferredQuery.trim().length > 0,
  });
  const engagement = useLoreEngagement(results.data?.results.map((item) => item.id) ?? []);

  useEffect(() => {
    setQuery(urlQuery);
    setSubmittedQuery(urlQuery);
  }, [urlQuery]);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="font-display text-4xl">Search</h1>
        <p className="max-w-2xl text-lore-slate">Ask for a theme, craft, season of life, or type of question. Lore searches for depth, not trending keywords.</p>
      </header>

      <Card>
        <form
          className="flex flex-col gap-3 md:flex-row"
          onSubmit={(event) => {
            event.preventDefault();
            const nextQuery = query.trim();
            setSubmittedQuery(nextQuery);
            if (nextQuery) {
              setSearchParams({ q: nextQuery });
            } else {
              setSearchParams({});
            }
          }}
        >
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="focus-ring w-full rounded-2xl border border-black/15 px-4 py-3"
            placeholder="Try: doctor, patience, grief, apprenticeship, parenting"
          />
          <Button type="submit">Search</Button>
        </form>
      </Card>

      {results.isLoading ? <Card>Searching the archive...</Card> : null}
      {submittedQuery && !results.isLoading && !results.data?.results.length ? (
        <EmptyState
          title="No results yet"
          description="Try a broader theme or a different phrasing. Lore favors lived language over rigid taxonomy."
        />
      ) : null}

      <div className="grid gap-4 xl:grid-cols-2">
        {results.data?.results.map((entry) => (
          <LoreCard
            key={entry.id}
            lore={entry}
            isBookmarked={engagement.bookmarkedLoreIds.has(entry.id)}
            isLiked={engagement.likedLoreIds.has(entry.id)}
            likeCount={engagement.likeCounts.get(entry.id) ?? 0}
            onToggleBookmark={(loreId, bookmarked) => engagement.toggleBookmark.mutate({ loreId, bookmarked })}
            onToggleLike={(loreId, liked) => engagement.toggleLike.mutate({ loreId, liked })}
          />
        ))}
      </div>
    </div>
  );
}
