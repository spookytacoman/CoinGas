
import React from 'react';
import { CloudCog, Wind } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="py-6">
      <div className="container flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Wind className="h-8 w-8 text-fee-medium animate-pulse-glow" />
            <div className="absolute -bottom-1 -right-1">
              <CloudCog className="h-4 w-4 text-fee-medium/70" />
            </div>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">
            <span className="text-white">Coin</span>
            <span className="text-fee-medium">Gas</span>
          </h1>
        </div>
        <div className="text-sm text-muted-foreground">
          Real-time cryptocurrency gas fees
        </div>
      </div>
    </header>
  );
};

export default Header;
