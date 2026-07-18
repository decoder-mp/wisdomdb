import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Heart, Bookmark, MessageSquare, Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { createComment, deleteComment, fetchComments, updateComment } from "@/features/comments/api/commentApi";
import { deleteLore, fetchLoreById, updateLore } from "@/features/lore/api/loreApi";
import { useLoreEngagement } from "@/features/lore/hooks/useLoreEngagement";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { getApiErrorMessage } from "@/lib/apiError";
import { formatDate } from "@/lib/utils";
import type { LoreInput } from "@/types/api";

export function LoreDetailsPage() {
  const { loreId = "" } = useParams();
  const numericLoreId = Number(loreId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const currentUser = useCurrentUser();
  const lore = useQuery({ queryKey: ["lore", loreId], queryFn: () => fetchLoreById(loreId), enabled: Boolean(loreId) });
  const comments = useQuery({
    queryKey: ["comments", numericLoreId],
    queryFn: () => fetchComments(numericLoreId),
    enabled: Number.isFinite(numericLoreId) && numericLoreId > 0,
  });

  const engagement = useLoreEngagement(Number.isFinite(numericLoreId) && numericLoreId > 0 ? [numericLoreId] : []);
  const isOwner = lore.data?.user_id === currentUser.data?.id;
  const [isEditingLore, setIsEditingLore] = useState(false);
  const [commentDraft, setCommentDraft] = useState("");
  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [editingCommentValue, setEditingCommentValue] = useState("");
  const [loreDraft, setLoreDraft] = useState<LoreInput>({
    person: "",
    profession: "",
    years_experience: 0,
    theme: "",
    question: "",
    lore: "",
  });

  useEffect(() => {
    if (lore.data && !isEditingLore) {
      setLoreDraft({
        person: lore.data.person,
        profession: lore.data.profession,
        years_experience: lore.data.years_experience,
        theme: lore.data.theme,
        question: lore.data.question,
        lore: lore.data.lore,
      });
    }
  }, [isEditingLore, lore.data]);

  const saveLore = useMutation({
    mutationFn: (payload: Partial<LoreInput>) => updateLore(numericLoreId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["lore", loreId] });
      await queryClient.invalidateQueries({ queryKey: ["lore"] });
      setIsEditingLore(false);
    },
  });

  const removeLore = useMutation({
    mutationFn: () => deleteLore(numericLoreId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["lore"] });
      navigate("/explore");
    },
  });

  const addComment = useMutation({
    mutationFn: (content: string) => createComment(numericLoreId, content),
    onSuccess: async () => {
      setCommentDraft("");
      await queryClient.invalidateQueries({ queryKey: ["comments", numericLoreId] });
      await queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const saveComment = useMutation({
    mutationFn: ({ commentId, content }: { commentId: number; content: string }) => updateComment(commentId, content),
    onSuccess: async () => {
      setEditingCommentId(null);
      setEditingCommentValue("");
      await queryClient.invalidateQueries({ queryKey: ["comments", numericLoreId] });
    },
  });

  const removeComment = useMutation({
    mutationFn: deleteComment,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["comments", numericLoreId] });
    },
  });

  if (lore.isLoading) {
    return <p>Loading story...</p>;
  }

  if (lore.isError || !lore.data) {
    return <p className="text-lore-terracotta">Unable to load this story right now.</p>;
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Card className="space-y-8 p-8 md:p-12">
        <header className="space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-3">
              <Link to={`/search?q=${encodeURIComponent(lore.data.theme)}`} className="text-xs uppercase tracking-[0.15em] text-lore-forest transition hover:text-lore-ocean">
                {lore.data.theme}
              </Link>
              <h1 className="font-display text-4xl md:text-5xl">{lore.data.person}</h1>
              <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-lore-slate">
                <Link to={`/profile?userId=${lore.data.author.id}`} className="transition hover:text-lore-charcoal">
                  by {lore.data.author.username}
                </Link>
                <span>{lore.data.profession || "Life storyteller"}</span>
                <span>{lore.data.years_experience} years of experience</span>
                <span>{formatDate(lore.data.created_at)}</span>
              </div>
            </div>

            {isOwner ? (
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={() => setIsEditingLore((value) => !value)}>
                  <Pencil className="mr-2 h-4 w-4" />
                  {isEditingLore ? "Cancel" : "Edit"}
                </Button>
                <Button variant="ghost" onClick={() => removeLore.mutate()}>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </Button>
              </div>
            ) : null}
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant={engagement.likedLoreIds.has(numericLoreId) ? "primary" : "ghost"}
              onClick={() => engagement.toggleLike.mutate({ loreId: numericLoreId, liked: engagement.likedLoreIds.has(numericLoreId) })}
            >
              <Heart className={`mr-2 h-4 w-4 ${engagement.likedLoreIds.has(numericLoreId) ? "fill-current" : ""}`} />
              {engagement.likeCounts.get(numericLoreId) ?? 0} likes
            </Button>
            <Button
              type="button"
              variant={engagement.bookmarkedLoreIds.has(numericLoreId) ? "outline" : "ghost"}
              onClick={() => engagement.toggleBookmark.mutate({ loreId: numericLoreId, bookmarked: engagement.bookmarkedLoreIds.has(numericLoreId) })}
            >
              <Bookmark className={`mr-2 h-4 w-4 ${engagement.bookmarkedLoreIds.has(numericLoreId) ? "fill-current" : ""}`} />
              {engagement.bookmarkedLoreIds.has(numericLoreId) ? "Saved" : "Save story"}
            </Button>
          </div>
        </header>

        {isEditingLore ? (
          <form
            className="grid gap-4"
            onSubmit={(event) => {
              event.preventDefault();
              saveLore.mutate(loreDraft);
            }}
          >
            <input className="focus-ring rounded-xl border border-black/15 px-3 py-2" value={loreDraft.person} onChange={(event) => setLoreDraft((value) => ({ ...value, person: event.target.value }))} />
            <input className="focus-ring rounded-xl border border-black/15 px-3 py-2" value={loreDraft.profession} onChange={(event) => setLoreDraft((value) => ({ ...value, profession: event.target.value }))} />
            <input className="focus-ring rounded-xl border border-black/15 px-3 py-2" type="number" value={loreDraft.years_experience} onChange={(event) => setLoreDraft((value) => ({ ...value, years_experience: Number(event.target.value) }))} />
            <input className="focus-ring rounded-xl border border-black/15 px-3 py-2" value={loreDraft.theme} onChange={(event) => setLoreDraft((value) => ({ ...value, theme: event.target.value }))} />
            <textarea className="focus-ring min-h-[96px] rounded-xl border border-black/15 px-3 py-2" value={loreDraft.question} onChange={(event) => setLoreDraft((value) => ({ ...value, question: event.target.value }))} />
            <textarea className="focus-ring min-h-[220px] rounded-xl border border-black/15 px-3 py-2" value={loreDraft.lore} onChange={(event) => setLoreDraft((value) => ({ ...value, lore: event.target.value }))} />
            <div className="flex gap-2">
              <Button type="submit" disabled={saveLore.isPending}>{saveLore.isPending ? "Saving..." : "Save changes"}</Button>
              <Button type="button" variant="ghost" onClick={() => setIsEditingLore(false)}>Cancel</Button>
            </div>
            {saveLore.isError ? <p className="text-sm text-lore-terracotta">{getApiErrorMessage(saveLore.error, "Unable to save changes.")}</p> : null}
          </form>
        ) : (
          <>
            <section>
              <h2 className="font-display text-2xl">Question</h2>
              <p className="mt-2 reading-prose">{lore.data.question}</p>
            </section>
            <section>
              <h2 className="font-display text-2xl">Lore</h2>
              <p className="mt-2 whitespace-pre-wrap reading-prose">{lore.data.lore}</p>
            </section>
          </>
        )}
      </Card>

      <section className="space-y-4">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-5 w-5 text-lore-terracotta" />
          <h2 className="font-display text-3xl">Conversation</h2>
        </div>

        <Card>
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              if (!commentDraft.trim()) {
                return;
              }
              addComment.mutate(commentDraft.trim());
            }}
          >
            <textarea
              className="focus-ring min-h-[120px] w-full rounded-2xl border border-black/15 px-4 py-3"
              placeholder="Add a thoughtful response or question"
              value={commentDraft}
              onChange={(event) => setCommentDraft(event.target.value)}
            />
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm text-lore-slate">Comments are part of the archive too. Keep them useful and kind.</p>
              <Button type="submit" disabled={addComment.isPending}>{addComment.isPending ? "Posting..." : "Post comment"}</Button>
            </div>
            {addComment.isError ? <p className="text-sm text-lore-terracotta">{getApiErrorMessage(addComment.error, "Unable to post comment.")}</p> : null}
          </form>
        </Card>

        {comments.isLoading ? <Card>Loading comments...</Card> : null}
        {!comments.isLoading && !comments.data?.length ? (
          <EmptyState
            title="No comments yet"
            description="Be the first reader to respond. A good question can preserve as much wisdom as a good answer."
          />
        ) : null}

        <div className="space-y-3">
          {comments.data?.map((comment) => {
            const isCommentOwner = comment.user_id === currentUser.data?.id;
            const isEditingThisComment = editingCommentId === comment.id;
            return (
              <Card key={comment.id} className="space-y-3">
                <div className="flex items-center justify-between gap-3 text-sm text-lore-slate">
                  <Link to={`/profile?userId=${comment.user_id}`} className="transition hover:text-lore-charcoal">
                    Contributor #{comment.user_id}
                  </Link>
                  <span>{formatDate(comment.created_at)}</span>
                </div>
                {isEditingThisComment ? (
                  <form
                    className="space-y-3"
                    onSubmit={(event) => {
                      event.preventDefault();
                      saveComment.mutate({ commentId: comment.id, content: editingCommentValue.trim() });
                    }}
                  >
                    <textarea className="focus-ring min-h-[110px] w-full rounded-2xl border border-black/15 px-4 py-3" value={editingCommentValue} onChange={(event) => setEditingCommentValue(event.target.value)} />
                    <div className="flex gap-2">
                      <Button type="submit" disabled={saveComment.isPending}>{saveComment.isPending ? "Saving..." : "Save"}</Button>
                      <Button type="button" variant="ghost" onClick={() => setEditingCommentId(null)}>Cancel</Button>
                    </div>
                  </form>
                ) : (
                  <p className="whitespace-pre-wrap text-lore-charcoal">{comment.content}</p>
                )}
                {isCommentOwner && !isEditingThisComment ? (
                  <div className="flex gap-2">
                    <Button variant="ghost" onClick={() => {
                      setEditingCommentId(comment.id);
                      setEditingCommentValue(comment.content);
                    }}>
                      Edit
                    </Button>
                    <Button variant="ghost" onClick={() => removeComment.mutate(comment.id)}>
                      Delete
                    </Button>
                  </div>
                ) : null}
              </Card>
            );
          })}
        </div>
      </section>
    </div>
  );
}
