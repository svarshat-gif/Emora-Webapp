import { format, formatDistanceToNow, isToday, isYesterday, parseISO } from "date-fns";

export function formatDate(dateStr: string): string {
  const date = parseISO(dateStr);
  if (isToday(date)) return "Today";
  if (isYesterday(date)) return "Yesterday";
  return format(date, "MMM d, yyyy");
}

export function formatRelative(dateStr: string): string {
  return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
}

export function formatTime(dateStr: string): string {
  return format(parseISO(dateStr), "h:mm a");
}

export function formatMonthYear(year: number, month: number): string {
  return format(new Date(year, month - 1, 1), "MMMM yyyy");
}

export function toDateKey(date: Date): string {
  return format(date, "yyyy-MM-dd");
}
