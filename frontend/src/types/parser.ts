export interface ParserMetrics {
  skillsExtracted: number;
  experienceYears: number;
  parsingTimeMs: number;
  successRate: number;
  accuracyEstimate: string;
  name: string;
  type: 'npl' | 'regex';
}

export interface ComparisonResult {
  parserA: ParserMetrics;
  parserB: ParserMetrics;
  winner: 'A' | 'B' | 'tie';
  generatedAt: string;
  resumesTested: number;
}

export interface ComparisonChart {
  skills: {
    labels: string[];
    data: number[];
  };
  performance: {
    labels: string[];
    data: number[];
  };
}
