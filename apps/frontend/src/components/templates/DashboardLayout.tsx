import { BarChart3, BriefcaseBusiness, CalendarCheck, LayoutDashboard, Plus, Users } from "lucide-react";
import { SearchBar } from "@/components/molecules/SearchBar";
import { Button } from "@/components/atoms/Button";
import Link from "next/link";
import type { Route } from "next";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/dashboard/candidates", label: "Candidates", icon: Users },
  { href: "/dashboard/interviews", label: "Interviews", icon: CalendarCheck },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 }
];

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="dash-layout">
      <aside className="dash-sidebar">
        <Link className="brand" href="/">
          <span>NH</span>
          <div>
            <strong>NeuroHire</strong>
            <small>Autonomous Intelligence</small>
          </div>
        </Link>
        <nav>
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <Link href={item.href as Route} key={item.href}>
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <Button icon={<Plus size={16} />} className="sidebar-action">New requisition</Button>
      </aside>
      <main>
        <header className="dash-top">
          <SearchBar />
          <div className="top-status"><span className="pulse-dot" /> 8 agents online</div>
        </header>
        {children}
      </main>
    </div>
  );
}
