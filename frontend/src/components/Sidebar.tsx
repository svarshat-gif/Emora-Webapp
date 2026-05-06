"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, MessageCircle, CalendarDays, Target, Settings, LogOut, Flame } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/authStore";
import { getCompanion } from "@/lib/companions";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageCircle },
  { name: "Calendar", href: "/calendar", icon: CalendarDays },
  { name: "Goals", href: "/goals", icon: Target },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuthStore();
  const companion = getCompanion(user?.personality);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div
      className="w-60 h-full flex flex-col shrink-0 border-r border-white/[0.06] relative overflow-hidden"
      style={{ background: "rgba(6,11,24,0.92)", backdropFilter: "blur(32px)" }}
    >
      {/* Companion ambient glow */}
      <div
        className="absolute -top-16 -left-16 w-56 h-56 rounded-full pointer-events-none opacity-25"
        style={{ backgroundColor: companion.color, filter: "blur(70px)" }}
      />
      <div
        className="absolute -bottom-16 -right-16 w-48 h-48 rounded-full pointer-events-none opacity-10"
        style={{ backgroundColor: companion.color, filter: "blur(60px)" }}
      />

      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 pt-6 pb-7 relative z-10">
        <div className="relative w-7 h-7 shrink-0">
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.9, 0.5] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            className="absolute inset-0 rounded-full"
            style={{ backgroundColor: companion.color, filter: "blur(5px)" }}
          />
          <div className={cn("absolute inset-0 rounded-full bg-gradient-to-br", companion.gradient)} />
        </div>
        <span className="text-base font-bold tracking-tight text-white">Emora</span>
      </div>

      {/* User card */}
      {user && (
        <div className="mx-3 mb-5 p-3 rounded-xl border border-white/[0.06] bg-white/[0.03] relative z-10">
          <div className="flex items-center gap-2.5">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold text-white shrink-0"
              style={{
                background: `linear-gradient(135deg, ${companion.color}90, ${companion.color}40)`,
                boxShadow: `0 0 12px ${companion.glowSoft}`,
              }}
            >
              {user.name?.charAt(0)?.toUpperCase() ?? "?"}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-white truncate leading-tight">{user.name}</p>
              <p className="text-[10px] truncate leading-tight mt-0.5" style={{ color: companion.color }}>
                with {companion.name}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 px-2 space-y-0.5 relative z-10">
        {navItems.map((item, i) => {
          const isActive = pathname === item.href;
          return (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04, duration: 0.25 }}
            >
              <Link
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 text-sm relative group",
                  isActive ? "text-white font-medium" : "text-white/35 hover:text-white/70 hover:bg-white/[0.04]"
                )}
                style={isActive ? {
                  background: `${companion.color}14`,
                  border: `1px solid ${companion.color}28`,
                } : {}}
              >
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full"
                    style={{ backgroundColor: companion.color }}
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  />
                )}
                <item.icon
                  className="w-4 h-4 shrink-0"
                  style={isActive ? { color: companion.color } : {}}
                />
                <span className="text-[13px]">{item.name}</span>
              </Link>
            </motion.div>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="px-3 pb-5 space-y-2 relative z-10">
        {user && user.streak > 0 && (
          <div
            className="flex items-center gap-2 px-3 py-2 rounded-xl border"
            style={{ background: "rgba(251,146,60,0.07)", borderColor: "rgba(251,146,60,0.18)" }}
          >
            <Flame className="w-3.5 h-3.5 text-orange-400 shrink-0" />
            <span className="text-xs font-semibold text-orange-300">{user.streak} day streak</span>
          </div>
        )}
        <div className="h-px bg-white/[0.05]" />
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full text-white/25 hover:text-red-400/80 transition-colors rounded-xl hover:bg-red-400/[0.05] text-[13px]"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
