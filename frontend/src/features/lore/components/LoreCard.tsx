import { Heart, Bookmark, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { Lore } from "@/types/api";
import { estimateReadingTime, formatDate } from "@/lib/utils";

type LoreCardProps = {
  lore: Lore;
  isBookmarked: boolean;
  isLiked: boolean;
  likeCount: number;
  onToggleBookmark: (loreId: number, bookmarked: boolean) => void;
  onToggleLike: (loreId: number, liked: boolean) => void;
  profileTo?: string;
};

export function LoreCard({
  lore,
  isBookmarked,
  isLiked,
  likeCount,
  onToggleBookmark,
  onToggleLike,
  profileTo = `/profile?userId=${lore.author.id}`,
}: LoreCardProps) {
  return (
    <Card className="group relative overflow-hidden bg-white/80 transition hover:-translate-y-1 hover:shadow-xl">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-lore-gold/0 via-lore-gold/60 to-lore-gold/0" />
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <Link
              to={`/search?q=${encodeURIComponent(lore.theme)}`}
              className="text-xs uppercase tracking-[0.18em] text-lore-forest transition hover:text-lore-ocean"
            >
              {lore.theme}
            </Link>
            <Link to={`/lore/${lore.id}`} className="mt-2 block font-display text-2xl text-lore-charcoal transition hover:text-lore-terracotta">
              {lore.person}
            </Link>
            <Link to={profileTo} className="mt-1 block text-sm text-lore-slate transition hover:text-lore-charcoal">
              by {lore.author.username} · {lore.profession || "Storyteller"}
            </Link>
          </div>
          <p className="whitespace-nowrap text-xs uppercase tracking-[0.12em] text-lore-smoke">{formatDate(lore.created_at)}</p>
        </div>

        <p className="line-clamp-2 text-sm text-lore-slate">{lore.question}</p>
        <p className="line-clamp-4 reading-prose text-lore-charcoal/90">{lore.lore}</p>
        <p className="text-xs uppercase tracking-[0.13em] text-lore-smoke">{estimateReadingTime(lore.lore)}</p>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant={isLiked ? "primary" : "ghost"}
              className="px-3 py-2"
              aria-label={isLiked ? "Unlike story" : "Like story"}
              onClick={() => onToggleLike(lore.id, isLiked)}
            >
              <Heart className={`mr-2 h-4 w-4 transition ${isLiked ? "fill-current scale-105" : ""}`} />
              {likeCount}
            </Button>
            <Button
              type="button"
              variant={isBookmarked ? "outline" : "ghost"}
              className="px-3 py-2"
              aria-label={isBookmarked ? "Remove bookmark" : "Bookmark story"}
              onClick={() => onToggleBookmark(lore.id, isBookmarked)}
            >
              <Bookmark className={`mr-2 h-4 w-4 transition ${isBookmarked ? "fill-current -rotate-3" : ""}`} />
              Save
            </Button>
          </div>

          <Link to={`/lore/${lore.id}`} className="inline-flex items-center gap-2 text-sm font-semibold text-lore-terracotta transition hover:text-lore-charcoal">
            Read story
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
          </Link>
        </div>
      </div>
    </Card>
  );
}