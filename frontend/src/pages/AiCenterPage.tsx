import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { discoverForMe, extractThemes, summarizeText } from "@/features/ai/api/aiApi";
import { useCurrentUser } from "@/hooks/useCurrentUser";

export function AiCenterPage() {
  const currentUser = useCurrentUser();
  const [text, setText] = useState("");
  const summary = useMutation({ mutationFn: summarizeText });
  const themes = useMutation({ mutationFn: extractThemes });
  const personalDiscovery = useQuery({
    queryKey: ["ai", "discover", "me"],
    queryFn: discoverForMe,
    enabled: Boolean(currentUser.data),
  });

  return (
    <div className="space-y-6">
      <h1 className="font-display text-4xl">AI Center</h1>
      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <h2 className="font-display text-2xl">Theme Extraction</h2>
          <p className="mt-2 text-lore-slate">Extract and normalize themes from stories to improve discovery.</p>
          <textarea
            className="focus-ring mt-4 min-h-[180px] w-full rounded-2xl border border-black/15 px-4 py-3"
            placeholder="Paste a story, memory, or question here."
            value={text}
            onChange={(event) => setText(event.target.value)}
          />
          <div className="mt-4 flex gap-2">
            <Button onClick={() => themes.mutate(text)} disabled={!text.trim() || themes.isPending}>
              {themes.isPending ? "Extracting..." : "Extract themes"}
            </Button>
            <Button variant="outline" onClick={() => summary.mutate(text)} disabled={!text.trim() || summary.isPending}>
              {summary.isPending ? "Summarizing..." : "Summarize"}
            </Button>
          </div>
          {themes.data?.themes.length ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {themes.data.themes.map((theme) => (
                <span key={theme} className="rounded-full bg-lore-gold/25 px-3 py-1 text-sm text-lore-charcoal">
                  {theme}
                </span>
              ))}
            </div>
          ) : null}
          {summary.data?.summary ? <p className="mt-4 reading-prose text-lore-charcoal">{summary.data.summary}</p> : null}
        </Card>
        <Card>
          <h2 className="font-display text-2xl">Knowledge Discovery</h2>
          <p className="mt-2 text-lore-slate">Find related stories and suggested topics based on lived patterns.</p>
          {personalDiscovery.isLoading ? <p className="mt-4 text-lore-slate">Looking for adjacent wisdom...</p> : null}
          {!personalDiscovery.isLoading && !personalDiscovery.data?.results.length ? (
            <EmptyState
              title="Nothing to discover yet"
              description="Add at least one story of your own and Lore will begin looking for related wisdom from other people."
              actionLabel="Share a story"
              actionTo="/create"
            />
          ) : null}
          <div className="mt-4 space-y-3">
            {personalDiscovery.data?.results.slice(0, 4).map((item) => (
              <Link key={item.id} to={`/lore/${item.id}`}>
                <Card className="bg-lore-ivory/70 transition hover:-translate-y-0.5 hover:shadow-xl">
                  <p className="text-xs uppercase tracking-[0.12em] text-lore-forest">{item.theme}</p>
                  <p className="mt-2 font-display text-2xl">{item.person}</p>
                  <p className="mt-2 line-clamp-2 text-lore-slate">{item.question}</p>
                </Card>
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
