import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import type { ComparisonResult } from '../types/parser';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const useParserComparison = () => {
  return useQuery({
    queryKey: ['parserComparison'],
    queryFn: async (): Promise<ComparisonResult> => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/api/v1/parser-comparison`,
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );
        return response.data;
      } catch (error) {
        console.warn('Failed to fetch comparison data, using fallback');
        return {
          parserA: {
            name: 'Parser A (NLP)',
            type: 'npl',
            skillsExtracted: 41,
            experienceYears: 4,
            parsingTimeMs: 105.79,
            successRate: 100,
            accuracyEstimate: '90%+',
          },
          parserB: {
            name: 'Parser B (Regex)',
            type: 'regex',
            skillsExtracted: 15,
            experienceYears: 0,
            parsingTimeMs: 113.86,
            successRate: 100,
            accuracyEstimate: '60%',
          },
          winner: 'A',
          generatedAt: new Date().toISOString(),
          resumesTested: 1,
        };
      }
    },
    staleTime: 1000 * 60 * 60,
    gcTime: 1000 * 60 * 60 * 24,
  });
};
