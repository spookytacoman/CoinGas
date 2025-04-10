
import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { GasFee, NetworkSpeed } from '@/types/gas';
import { cn } from '@/lib/utils';
import FeeIndicator from './FeeIndicator';
import { formatDistanceToNow } from 'date-fns';
import { Bitcoin, Cpu, Coins, History } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from './ui/button';

interface GasCardProps {
  gasData: GasFee;
}

const GasCard: React.FC<GasCardProps> = ({ gasData }) => {
  const { network, symbol, speeds, lastUpdated } = gasData;

  // Get icon based on network
  const getNetworkIcon = () => {
    switch (network) {
      case 'bitcoin':
        return <Bitcoin className="h-6 w-6 text-bitcoin" />;
      case 'ethereum':
        return <Cpu className="h-6 w-6 text-ethereum" />;
      case 'solana':
        return <Coins className="h-6 w-6 text-solana" />;
      case 'polygon':
        return <Coins className="h-6 w-6 text-polygon" />;
      case 'avalanche':
        return <Coins className="h-6 w-6 text-avalanche" />;
      case 'binance':
        return <Coins className="h-6 w-6 text-binance" />;
      case 'cardano':
        return <Coins className="h-6 w-6 text-cardano" />;
      case 'polkadot':
        return <Coins className="h-6 w-6 text-polkadot" />;
      default:
        return <Coins className="h-6 w-6" />;
    }
  };

  // Get card gradient class based on network
  const gradientClass = `card-gradient-${network}`;
  
  return (
    <Card className={cn("backdrop-blur-sm border border-white/10 overflow-hidden", gradientClass)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          {getNetworkIcon()}
          <span className="uppercase">{symbol}</span>
        </CardTitle>
        <span className="text-xs text-muted-foreground capitalize">
          {network} Network
        </span>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {speeds.map((speed) => (
            <SpeedRow key={speed.level} speed={speed} />
          ))}
        </div>
      </CardContent>
      <CardFooter className="flex justify-between items-center pt-2">
        <span className="text-xs text-muted-foreground">
          Updated {formatDistanceToNow(new Date(lastUpdated), { addSuffix: true })}
        </span>
        <Button variant="outline" size="sm" asChild>
          <Link to={`/historical/${network}`}>
            <History className="mr-1" />
            Historical
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
};

interface SpeedRowProps {
  speed: NetworkSpeed;
}

const SpeedRow: React.FC<SpeedRowProps> = ({ speed }) => {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <FeeIndicator level={speed.level} pulseEffect={true} />
        <span className="capitalize text-sm font-medium">{speed.level}</span>
      </div>
      <div className="flex flex-col items-end">
        <span className="text-sm font-semibold">{speed.gasPrice}</span>
        <span className="text-xs text-muted-foreground">{speed.estimatedTime}</span>
      </div>
    </div>
  );
};

export default GasCard;
