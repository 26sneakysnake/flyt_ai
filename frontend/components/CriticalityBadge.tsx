import { cn } from '@/lib/utils'

interface CriticalityBadgeProps {
  level: 'CRITICAL' | 'WARNING' | 'NORMAL' | 'INFO'
  className?: string
}

const badgeStyles = {
  CRITICAL: 'bg-red-100 text-red-800 border-red-300',
  WARNING: 'bg-orange-100 text-orange-800 border-orange-300',
  NORMAL: 'bg-green-100 text-green-800 border-green-300',
  INFO: 'bg-blue-100 text-blue-800 border-blue-300',
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
