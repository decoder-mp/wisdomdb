import { Card } from "@/components/ui/Card";

export function VerifyEmailPage() {
  return (
    <div className="mx-auto flex min-h-screen max-w-xl items-center px-4 py-10">
      <Card className="w-full">
        <h1 className="font-display text-4xl">Verify Email</h1>
        <p className="mt-2 text-lore-slate">Confirm your email to protect account integrity and trust inside the circle.</p>
      </Card>
    </div>
  );
}
