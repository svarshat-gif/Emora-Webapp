import { cn } from "@/lib/utils";

interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  active?: boolean;
}

export function GlassPanel({ children, className, active = false, ...props }: GlassPanelProps) {
  return (
    <div
      className={cn(
        active ? "glass-panel-active" : "glass-panel",
        "relative rounded-[24px] overflow-hidden",
        className
      )}
      {...props}
    >
      {/* Specular Highlight */}
      <div className="absolute inset-0 border-t border-l border-white/20 rounded-[inherit] pointer-events-none" />
      {children}
    </div>
  );
}
