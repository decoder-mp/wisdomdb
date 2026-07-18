import { useQuery } from "@tanstack/react-query";
import { fetchCurrentUser } from "@/features/users/api/userApi";
import { useAuth } from "@/app/providers/AuthProvider";

export function useCurrentUser() {
  const { token } = useAuth();

  return useQuery({
    queryKey: ["current-user"],
    queryFn: fetchCurrentUser,
    enabled: Boolean(token),
    staleTime: 60_000,
  });
}