import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { forgotPassword } from "@/features/auth/api/authApi";
import { getApiErrorMessage } from "@/lib/apiError";

const schema = z.object({
  email: z.string().email(),
});

type FormValues = z.infer<typeof schema>;

export function ForgotPasswordPage() {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const mutation = useMutation({
    mutationFn: forgotPassword,
    onSuccess: () => reset(),
  });

  const mutationErrorMessage = mutation.error
    ? getApiErrorMessage(mutation.error, "Unable to request password reset. Try again shortly.")
    : null;

  return (
    <div className="mx-auto flex min-h-screen max-w-xl items-center px-4 py-10">
      <Card className="w-full">
        <h1 className="font-display text-4xl">Forgot Password</h1>
        <p className="mt-2 text-lore-slate">Enter your email to receive a secure reset link and continue your journey.</p>

        <form className="mt-6 space-y-4" noValidate onSubmit={handleSubmit((payload) => mutation.mutate(payload))}>
          <div className="space-y-1">
            <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Email" {...register("email")} />
            {errors.email ? <p className="text-sm text-lore-terracotta">{errors.email.message}</p> : null}
          </div>
          {mutation.isSuccess ? (
            <p className="text-sm text-lore-forest">If that account exists, a reset link has been sent.</p>
          ) : null}
          {mutationErrorMessage ? <p className="text-sm text-lore-terracotta">{mutationErrorMessage}</p> : null}
          <Button type="submit" className="w-full">{mutation.isPending ? "Sending reset link..." : "Email reset link"}</Button>
        </form>

        <p className="mt-4 text-sm text-lore-slate">
          Remembered it? <Link to="/login" className="font-semibold text-lore-terracotta">Return to sign in</Link>
        </p>
      </Card>
    </div>
  );
}
