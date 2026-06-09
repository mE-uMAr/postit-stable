import type { Metadata } from "next";
import type { ReactNode } from "react";

import { ThemeProvider } from "@/components/app/providers/ThemeProvider";
import { ToastProvider } from "@/components/app/providers/ToastProvider";
import { WorkspaceProvider } from "@/components/app/providers/WorkspaceProvider";
import { ConfirmProvider } from "@/components/app/providers/ConfirmProvider";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { AppShell } from "@/components/app/AppShell";

import "@/styles/app.css";
import "@/styles/app-views.css";

export const metadata: Metadata = {
  title: "Postit - App",
};

// Applies the saved theme to <html> before paint to avoid a flash of light mode.
const themeScript = `(function(){try{var t=localStorage.getItem('postit-theme')||'light';document.documentElement.setAttribute('data-theme',t);}catch(e){}})();`;

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <WorkspaceProvider>
          <ToastProvider>
            <ConfirmProvider>
              <script dangerouslySetInnerHTML={{ __html: themeScript }} />
              <AppShell>{children}</AppShell>
            </ConfirmProvider>
          </ToastProvider>
        </WorkspaceProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
