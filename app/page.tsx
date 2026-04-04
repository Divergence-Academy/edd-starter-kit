/**
 * app/page.tsx — Root page, redirects to /chat
 * ⚠️  This file is COMPLETE — no changes needed.
 */

import { redirect } from "next/navigation";

export default function Home() {
  redirect("/chat");
}
