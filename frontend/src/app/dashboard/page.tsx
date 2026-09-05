import { redirect } from "next/navigation";

/**
 * /dashboard — Redirect to root dashboard ("/").
 */
export default function DashboardRedirectPage() {
  redirect("/");
}
