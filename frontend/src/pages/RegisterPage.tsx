import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { register } from "@/features/auth/api/authApi";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { getApiErrorMessage } from "@/lib/apiError";

const schema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(8),
});

type FormValues = z.infer<typeof schema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const {
    register: registerField,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const passwordValue = watch("password") ?? "";
  const passwordStrength = useMemo(() => {
    const checks = [
      passwordValue.length >= 8,
      /[A-Z]/.test(passwordValue),
      /[a-z]/.test(passwordValue),
      /\d/.test(passwordValue),
      /[^A-Za-z0-9]/.test(passwordValue),
    ].filter(Boolean).length;
    if (checks <= 2) return { label: "Weak", value: 30 };
    if (checks <= 4) return { label: "Fair", value: 65 };
    return { label: "Strong", value: 100 };
  }, [passwordValue]);

  const mutation = useMutation({
    mutationFn: register,
    onSuccess: () => navigate("/login"),
  });

  const mutationErrorMessage = (() => {
    if (!mutation.error) {
      return null;
    }

    return getApiErrorMessage(
      mutation.error,
      "Unable to create account. Check backend server status and try again.",
    );
  })();

  return (
    <div className="mx-auto flex min-h-screen max-w-xl items-center px-4 py-10">
      <Card className="w-full">
        <h1 className="font-display text-4xl">Join Lore</h1>
        <p className="mt-2 text-lore-slate">Create your place in humanity's living memory.</p>

        <form className="mt-6 space-y-4" noValidate onSubmit={handleSubmit((payload) => mutation.mutate(payload))}>
          <div className="space-y-1">
            <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Username" {...registerField("username")} />
            {errors.username ? <p className="text-sm text-lore-terracotta">{errors.username.message}</p> : null}
          </div>
          <div className="space-y-1">
            <input className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2" placeholder="Email" {...registerField("email")} />
            {errors.email ? <p className="text-sm text-lore-terracotta">{errors.email.message}</p> : null}
          </div>
          <div className="space-y-1">
            <div className="relative">
              <input
                className="focus-ring w-full rounded-xl border border-black/15 px-3 py-2 pr-12"
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                {...registerField("password")}
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
            <div className="rounded-xl border border-black/10 bg-white/60 p-2">
              <div className="flex items-center justify-between text-xs uppercase tracking-[0.12em] text-lore-smoke">
                <span>Password strength</span>
                <span>{passwordStrength.label}</span>
              </div>
              <div className="mt-2 h-2 w-full rounded-full bg-black/10">
                <div className="h-full rounded-full bg-gradient-to-r from-lore-ember via-lore-gold to-lore-forest" style={{ width: `${passwordStrength.value}%` }} />
              </div>
            </div>
            {errors.password ? <p className="text-sm text-lore-terracotta">{errors.password.message}</p> : null}
          </div>
          {mutationErrorMessage ? <p className="text-sm text-lore-terracotta">{mutationErrorMessage}</p> : null}
          <Button type="submit" className="w-full">{mutation.isPending ? "Creating account..." : "Create account"}</Button>
        </form>

        <p className="mt-4 text-sm text-lore-slate">
          Already have an account? <Link to="/login" className="font-semibold text-lore-terracotta">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}
