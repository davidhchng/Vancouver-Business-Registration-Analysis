import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Vancouver Business Registrations",
  description:
    "Market interpretation tool using City of Vancouver business registration data.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

