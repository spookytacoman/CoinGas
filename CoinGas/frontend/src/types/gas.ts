
export type FeeLevel = 'low' | 'medium' | 'high';

export interface NetworkSpeed {
  level: FeeLevel;
  gasPrice: string;
  estimatedTime: string;
}

export interface GasFee {
  network: string;
  symbol: string;
  speeds: NetworkSpeed[];
  lastUpdated: string;
}

export interface HistoricalGasData {
  date: string;
  low: number;
  medium: number;
  high: number;
}
