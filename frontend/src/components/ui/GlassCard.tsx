import React from 'react';
import { Card } from './Card';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
  glow?: 'blue' | 'cyan' | 'emerald' | 'purple' | 'none';
  onClick?: () => void;
}

// Compatibility wrapper rendering clean academic research Card
export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  hoverEffect = false,
  onClick,
}) => {
  return (
    <Card className={className} hoverEffect={hoverEffect} onClick={onClick}>
      {children}
    </Card>
  );
};
