import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Incentive AI Chat",
  description: "Chat with Incentive AI in a ChatGPT-inspired interface.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
