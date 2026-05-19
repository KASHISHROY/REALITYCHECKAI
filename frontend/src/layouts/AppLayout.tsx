import { ScanSearch } from "lucide-react";
import type { PropsWithChildren } from "react";

export function AppLayout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen overflow-hidden bg-background text-foreground">
      <header className="border-b border-border/80 bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-6">
          <a className="flex items-center gap-3" href="/">
            <span className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-surface">
              <ScanSearch className="h-5 w-5 text-accent" aria-hidden="true" />
            </span>
            <span className="text-sm font-semibold">RealityCheck AI</span>
          </a>
          <nav className="hidden items-center gap-6 text-sm text-muted-foreground sm:flex">
            <a className="transition hover:text-foreground" href="#signals">
              Signals
            </a>
            <a className="transition hover:text-foreground" href="#stack">
              Stack
            </a>
          </nav>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}

