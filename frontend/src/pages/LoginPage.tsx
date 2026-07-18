import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/app/providers/AuthProvider";
import { login } from "@/features/auth/api/authApi";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { getApiErrorMessage } from "@/lib/apiError";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const { login: setAuth } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setAuth(data.access_token);
      navigate("/dashboard");
    },
  });

  const mutationErrorMessage = (() => {
    if (!mutation.error) {
      return null;
    }

    return getApiErrorMessage(
      mutation.error,
      "Unable to sign in. Check your credentials and backend server status.",
    );
  })();

  return (
    <div className="mx-auto flex min-h-screen max-w-xl items-center px-4 py-10">
      <Card className="w-full">
        <h1 className="font-display text-4xl">Welcome back to Lore</h1>
        <p className="mt-2 text-lore-slate">Return to the circle of lived wisdom.</p>

        <form className="mt-6 space-y-4" noValidate onSubmit={handleSubmit((payload) => mutation.mutate(payload))}>
          <div className="space-y-1">
            <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Email" {...register("email")} />
            {errors.email ? <p className="text-sm text-lore-terracotta">{errors.email.message}</p> : null}
          </div>
          <div className="space-y-1">
            <div className="relative">
              <input
                className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2 pr-12"
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                {...register("password")}
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
            {errors.password ? <p className="text-sm text-lore-terracotta">{errors.password.message}</p> : null}
          </div>
          {mutationErrorMessage ? <p className="text-sm text-lore-terracotta">{mutationErrorMessage}</p> : null}
          <Button type="submit" className="w-full">{mutation.isPending ? "Signing in..." : "Sign in"}</Button>
        </form>

        <p className="mt-4 text-sm text-lore-slate">
          New here? <Link to="/register" className="font-semibold text-lore-terracotta">Create account</Link>
        </p>
        <p className="mt-2 text-sm text-lore-slate">
          Locked out? <Link to="/forgot-password" className="font-semibold text-lore-terracotta">Reset your password</Link>
        </p>
      </Card>
    </div>
  );
}
