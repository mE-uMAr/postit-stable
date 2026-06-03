import type { Metadata } from "next";
import type { ReactNode } from "react";

import { ThemeProvider } from "@/components/app/providers/ThemeProvider";
import { ToastProvider } from "@/components/app/providers/ToastProvider";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { AdminShell } from "@/components/admin/AdminShell";

import "@/styles/app.css";
import "@/styles/app-views.css";

export const metadata: Metadata = {
  title: "Postit — Admin",
};

const themeScript = `(function(){try{var t=localStorage.getItem('postit-theme')||'light';document.documentElement.setAttribute('data-theme',t);}catch(e){}})();`;

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <script dangerouslySetInnerHTML={{ __html: themeScript }} />
          <AdminShell>{children}</AdminShell>
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
