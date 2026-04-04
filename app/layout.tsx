/**
 * app/layout.tsx — Root layout
 * ⚠️  This file is COMPLETE — no changes needed.
 */

export const metadata = {
  title: "AdventureWorks EDD",
  description: "Evaluation-Driven Development Starter Kit",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
