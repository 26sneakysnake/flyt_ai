import { cn } from '@/lib/utils'

interface CriticalityBadgeProps {
  level: 'CRITICAL' | 'WARNING' | 'NORMAL' | 'INFO'
  className?: string
}

const badgeStyles = {
  CRITICAL: 'bg-red-500/20 text-red-300 border-red-500/50',
  WARNING: 'bg-orange-500/20 text-orange-300 border-orange-500/50',
  NORMAL: 'bg-green-500/20 text-green-300 border-green-500/50',
  INFO: 'bg-blue-500/20 text-blue-300 border-blue-500/50',
}

const badgeIcons = {
  CRITICAL: '🔴',
  WARNING: '🟡',
  NORMAL: '🟢',
  INFO: '🔵',
}

export default function CriticalityBadge({ level, className }: CriticalityBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border',
        badgeStyles[level],
        className
      )}
    >
      <span>{badgeIcons[level]}</span>
      <span>{level}</span>
    </span>
  )
}
