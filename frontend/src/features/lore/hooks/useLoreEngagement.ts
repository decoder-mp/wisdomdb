import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { createBookmark, deleteBookmark, fetchBookmarks } from "@/features/bookmarks/api/bookmarkApi";
import { fetchLikeCount, fetchMyLikes, likeLore, unlikeLore } from "@/features/likes/api/likeApi";

export function useLoreEngagement(loreIds: number[]) {
  const queryClient = useQueryClient();

  const bookmarksQuery = useQuery({
    queryKey: ["bookmarks"],
    queryFn: fetchBookmarks,
  });

  const likesQuery = useQuery({
    queryKey: ["likes", "me"],
    queryFn: fetchMyLikes,
  });

  const likeCountQueries = useQueries({
    queries: loreIds.map((loreId) => ({
      queryKey: ["likes", loreId],
      queryFn: () => fetchLikeCount(loreId),
      enabled: loreIds.length > 0,
      staleTime: 20_000,
    })),
  });

  const bookmarkMutation = useMutation({
    mutationFn: async ({ loreId, bookmarked }: { loreId: number; bookmarked: boolean }) => (
      bookmarked ? deleteBookmark(loreId) : createBookmark(loreId)
    ),
    onMutate: async ({ loreId, bookmarked }) => {
      await queryClient.cancelQueries({ queryKey: ["bookmarks"] });
      const previous = queryClient.getQueryData<Array<{ id: number; user_id: number; lore_id: number }>>(["bookmarks"]);
      queryClient.setQueryData<Array<{ id: number; user_id: number; lore_id: number }>>(["bookmarks"], (current = []) => {
        if (bookmarked) {
          return current.filter((item) => item.lore_id !== loreId);
        }
        return [...current, { id: -loreId, user_id: -1, lore_id: loreId }];
      });
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["bookmarks"], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
    },
  });

  const likeMutation = useMutation({
    mutationFn: async ({ loreId, liked }: { loreId: number; liked: boolean }) => (
      liked ? unlikeLore(loreId) : likeLore(loreId)
    ),
    onMutate: async ({ loreId, liked }) => {
      await queryClient.cancelQueries({ queryKey: ["likes", "me"] });
      await queryClient.cancelQueries({ queryKey: ["likes", loreId] });

      const previousLikes = queryClient.getQueryData<Array<{ id: number; user_id: number; lore_id: number }>>(["likes", "me"]);
      const previousCount = queryClient.getQueryData<{ lore_id: number; likes: number }>(["likes", loreId]);

      queryClient.setQueryData<Array<{ id: number; user_id: number; lore_id: number }>>(["likes", "me"], (current = []) => {
        if (liked) {
          return current.filter((item) => item.lore_id !== loreId);
        }
        return [...current, { id: -loreId, user_id: -1, lore_id: loreId }];
      });

      queryClient.setQueryData<{ lore_id: number; likes: number }>(["likes", loreId], (current) => ({
        lore_id: loreId,
        likes: Math.max(0, (current?.likes ?? 0) + (liked ? -1 : 1)),
      }));

      return { previousLikes, previousCount };
    },
    onError: (_error, variables, context) => {
      if (context?.previousLikes) {
        queryClient.setQueryData(["likes", "me"], context.previousLikes);
      }
      if (context?.previousCount) {
        queryClient.setQueryData(["likes", variables.loreId], context.previousCount);
      }
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: ["likes", "me"] });
      queryClient.invalidateQueries({ queryKey: ["likes", variables.loreId] });
    },
  });

  const bookmarkedLoreIds = new Set((bookmarksQuery.data ?? []).map((item) => item.lore_id));
  const likedLoreIds = new Set((likesQuery.data ?? []).map((item) => item.lore_id));
  const likeCounts = new Map(
    loreIds.map((loreId, index) => [loreId, likeCountQueries[index]?.data?.likes ?? 0]),
  );

  return {
    bookmarksQuery,
    likesQuery,
    bookmarkedLoreIds,
    likedLoreIds,
    likeCounts,
    isCountsLoading: likeCountQueries.some((query) => query.isLoading),
    toggleBookmark: bookmarkMutation,
    toggleLike: likeMutation,
  };
}