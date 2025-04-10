
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="py-6 border-t border-border/40">
      <div className="container flex flex-col sm:flex-row justify-between items-center gap-4">
        <div className="text-sm text-muted-foreground">
          © 2025 CoinGas. All rights reserved.
        </div>
        <div className="text-xs text-muted-foreground">
          Gas fees are estimates and may vary. Not financial advice.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
