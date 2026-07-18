import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { completePasswordReset } from "@/features/auth/api/authApi";
import { getApiErrorMessage } from "@/lib/apiError";

const schema = z
  .object({
    newPassword: z.string().min(8),
    confirmPassword: z.string().min(8),
  })
  .refine((value) => value.newPassword === value.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

type FormValues = z.infer<typeof schema>;

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const mutation = useMutation({
    mutationFn: (payload: FormValues) =>
      completePasswordReset({ token, new_password: payload.newPassword }),
    onSuccess: () => reset(),
  });

  const mutationErrorMessage = mutation.error
    ? getApiErrorMessage(mutation.error, "Unable to reset password. Request a fresh reset link and try again.")
    : null;

  return (
    <div className="mx-auto flex min-h-screen max-w-xl items-center px-4 py-10">
      <Card className="w-full">
        <h1 className="font-display text-4xl">Reset Password</h1>
        <p className="mt-2 text-lore-slate">Choose a strong new password to secure your Lore account.</p>

        {!token ? <p className="mt-4 text-sm text-lore-terracotta">This reset link is missing its token. Request a new email.</p> : null}

        <form className="mt-6 space-y-4" noValidate onSubmit={handleSubmit((payload) => mutation.mutate(payload))}>
          <div className="space-y-1">
            <div className="relative">
              <input
                className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2 pr-12"
                type={showPassword ? "text" : "password"}
                placeholder="New password"
                {...register("newPassword")}
              />
              <button
                type="button"
                className="focus-ring absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-2 text-lore-slate"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((value) => !value)}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.newPassword ? <p className="text-sm text-lore-terracotta">{errors.newPassword.message}</p> : null}
          </div>
          <div className="space-y-1">
            <div className="relative">
              <input
                className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2 pr-12"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm new password"
                {...register("confirmPassword")}
              />
              <button
                type="button"
                className="focus-ring absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-2 text-lore-slate"
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                onClick={() => setShowConfirmPassword((value) => !value)}
              >
                {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.confirmPassword ? <p className="text-sm text-lore-terracotta">{errors.confirmPassword.message}</p> : null}
          </div>
          {mutation.isSuccess ? <p className="text-sm text-lore-forest">Password reset complete. You can sign in now.</p> : null}
          {mutationErrorMessage ? <p className="text-sm text-lore-terracotta">{mutationErrorMessage}</p> : null}
          <Button type="submit" className="w-full" disabled={!token}>{mutation.isPending ? "Updating password..." : "Set new password"}</Button>
        </form>

        <p className="mt-4 text-sm text-lore-slate">
          <Link to="/forgot-password" className="font-semibold text-lore-terracotta">Request another reset email</Link>
        </p>
      </Card>
    </div>
  );
}
