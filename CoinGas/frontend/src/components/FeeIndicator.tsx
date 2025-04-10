
import React from 'react';
import { cn } from '@/lib/utils';
import { FeeLevel } from '@/types/gas';

interface FeeIndicatorProps {
  level: FeeLevel;
  className?: string;
  pulseEffect?: boolean;
}

const FeeIndicator: React.FC<FeeIndicatorProps> = ({ 
  level, 
  className,
  pulseEffect = false
}) => {
  const baseClasses = "inline-block h-3 w-3 rounded-full";
  const colorClasses = {
    low: "bg-fee-low",
    medium: "bg-fee-medium",
    high: "bg-fee-high"
  };
  
  return (
    <span 
      className={cn(
        baseClasses, 
        colorClasses[level], 
        pulseEffect && "animate-pulse-glow",
        className
      )}
    />
  );
};

export default FeeIndicator;
