import React, { useEffect, useState } from 'react';
import { connectToGasWebSocket, disconnectFromGasWebSocket } from '@/services/gasService';
import { GasFee } from '@/types/gas';
import GasCard from './GasCard';
import { toast } from 'sonner';
// import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
// import FeeIndicator from './FeeIndicator';
// import { formatDistanceToNow } from 'date-fns';
// import { Button } from './ui/button';
// import { History } from 'lucide-react';z
// import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const [gasFees, setGasFees] = useState<GasFee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    
    connectToGasWebSocket(
      (data) => {
        setGasFees(data);
        setError(null);
        setLoading(false);
      },
      (errorMessage) => {
        console.error('WebSocket error:', errorMessage);
        setError(errorMessage);
        setLoading(false);
        toast.error('Could not load gas fees', {
          description: 'Please try refreshing the page'
        });
      }
    );

    return () => {
      disconnectFromGasWebSocket();
    };
  }, []);

  // Separate main cryptocurrencies (BTC, ETH, SOL) from the others
  const mainCryptos = gasFees.filter(fee => 
    ["bitcoin", "ethereum", "solana"].includes(fee.network)
  );
  
  const otherCryptos = gasFees.filter(fee => 
    !["bitcoin", "ethereum", "solana"].includes(fee.network)
  );

  if (loading && gasFees.length === 0) {
    return (
      <div className="container py-12">
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="flex flex-col items-center gap-4">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <p className="text-sm text-muted-foreground">Loading gas fees...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && gasFees.length === 0) {
    return (
      <div className="container py-12">
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="text-center space-y-4">
            <p className="text-destructive">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="px-4 py-2 bg-secondary hover:bg-secondary/80 rounded-md text-sm"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-12">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mainCryptos.map((gasFee) => (
          <GasCard key={gasFee.network} gasData={gasFee} />
        ))}
      </div>
      
      {loading && gasFees.length > 0 && (
        <div className="mt-6 text-center">
          <p className="text-xs text-muted-foreground animate-pulse">Refreshing gas fees...</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
