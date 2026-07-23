import React, { useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import UploadedImageCard from '@/components/results/UploadedImageCard';
import KuralCard from '@/components/results/KuralCard';
import ConceptCard from '@/components/results/ConceptCard';
import ConfidenceCard from '@/components/results/ConfidenceCard';
import ExplanationCard from '@/components/results/ExplanationCard';
import AlternativeMatchesCard from '@/components/results/AlternativeMatchesCard';
import EducationalChat from '@/components/chat/EducationalChat';
import Button from '@/components/ui/button';

const Results: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as {
    image: {
      preview: string;
      name: string;
      width?: number;
      height?: number;
    };
    prediction: {
      tirukkuralNumber: number | string;
      tamilCouplet: string;
      englishTranslation: string;
      concept: string;
      confidence: {
        overall: number;
        imageSimilarity: number;
        knowledgeSimilarity: number;
        combinedScore: number;
      };
      explanation?: string;
      alternativeMatches: Array<{
        tirukkuralNumber: number | string;
        tamilCouplet: string;
        englishTranslation: string;
        concept: string;
        combinedScore: number;
      }>;
      analysisSteps: {
        imageAnalyzed: boolean;
        kuralFound: boolean;
        conceptIdentified: boolean;
        explanationGenerated: boolean;
      };
    };
  } | null;

  const handleRefresh = useCallback(() => {
    // In a real app, this might trigger a refetch of the data
    // For now, we'll just show a toast or redirect to home for retry
    navigate('/', { replace: true });
  }, [navigate]);

  if (!state) {
    return (
      <div className="min-h-screen bg-white flex flex-col items-center justify-center py-12">
        <div className="text-center">
          <div className="mb-6">
            <svg className="mx-auto h-12 w-12 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            No Analysis Data Available
          </h1>
          <p className="text-gray-600 mb-6">
            It looks like there's no analysis data to display. This might happen if you navigated directly to this page.
          </p>
          <div className="space-x-3">
            <Button
              variant="primary"
              onClick={() => navigate('/')}
              className="px-6 py-2"
            >
              Go to Upload Page
            </Button>
            <Button
              variant="outline"
              onClick={handleRefresh}
              className="px-6 py-2"
            >
              Refresh Page
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const { image, prediction } = state;

  return (
    <div className="min-h-screen bg-white">
      {/* The header and navigation are provided by AppLayout */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Analysis Results
          </h1>
          <p className="text-gray-600 mb-4">
            Analysis complete for "{image.name}". Explore the results below.
          </p>
          <div className="flex items-center space-x-3">
            <div className="h-0.5 flex-1 bg-gray-200"></div>
            <span className="px-2 text-xs text-gray-500">Step 1 of 2</span>
            <div className="h-0.5 flex-1 bg-gray-200"></div>
          </div>
        </div>

        {/* Information Hierarchy as specified */}
        <div className="space-y-8">
          {/* 1. Uploaded Image */}
          <section>
            <h2 className="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg className="h-4 w-4 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 01-2 2H5l-2 3V9a2 2 0 012-2h5l3-3 3 3h5z"></path>
              </svg>
              Uploaded Image
            </h2>
            <div className="space-y-4">
              <UploadedImageCard
                preview={image.preview}
                name={image.name}
                width={image.width}
                height={image.height}
              />
              {!image.width || !image.height ? (
                <p className="text-sm text-gray-500">
                  Image dimensions: Loading...
                </p>
              ) : (
                <p className="text-sm text-gray-500">
                  Image dimensions: {image.width} × {image.height}px
                </p>
              )}
            </div>
          </section>

          {/* 2. Matched Thirukkural */}
          <section>
            <h2 className="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg className="h-4 w-4 text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
              </svg>
              Matched Thirukkural
            </h2>
            <div className="space-y-4">
              <KuralCard
                tirukkuralNumber={prediction.tirukkuralNumber}
                tamilCouplet={prediction.tamilCouplet}
                englishTranslation={prediction.englishTranslation}
              />
            </div>
          </section>

          {/* 3. Ethical Concept */}
          <section>
            <h2 className="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg className="h-4 w-4 text-green-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 12l2 2 4-4m6-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Ethical Concept Identified
            </h2>
            <div className="space-y-4">
              <ConceptCard concept={prediction.concept} />
            </div>
          </section>

          {/* 4. Confidence */}
          <section>
            <h2 className="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg className="h-4 w-4 text-purple-600" viewBox="0 0 24 24 20" fill="none" strokeWidth="2">
                <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm0 10c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"></path>
              </svg>
              Confidence Metrics
            </h2>
            <div className="space-y-4">
              <ConfidenceCard confidence={prediction.confidence} />
            </div>
          </section>

          {/* 5. Explanation */}
          <section>
            <h2 className="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg className="h-4 w-4 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 12h6m2 0a2 2 0 110 4h-6m0-6a2 2 0 100 4h-2m2-4a2 2 0 110 4h-2m4 8a2 2 0 100-4"></path>
              </svg>
              Explanation
            </h2>
            <div className="space-y-4">
              {prediction.explanation ? (
                <ExplanationCard explanation={prediction.explanation} />
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">
                    No explanation available for this analysis.
                  </p>
                </div>
              )}
            </div>
          </section>

          {/* 6. Alternative Matches */}
          <section>
            <h2 className="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg className="h-4 w-4 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm0 10c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"></path>
              </svg>
              Alternative Matches
            </h2>
            <div className="space-y-4">
              {prediction.alternativeMatches && prediction.alternativeMatches.length > 0 ? (
                <AlternativeMatchesCard alternatives={prediction.alternativeMatches} />
              ) : (
                <div className="text-center py-8">
                  <div className="flex items-center justify-center mb-4">
                    <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                      <svg className="h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622"></path>
                      </svg>
                    </div>
                  </div>
                  <p className="text-gray-500">
                    No alternative matches were found for this analysis.
                  </p>
                  <p className="text-sm text-gray-400 mt-2">
                    Try uploading a different image to see alternative interpretations.
                  </p>
                </div>
              )}
            </div>
          </section>

          {/* 7. Educational Conversation */}
          <section>
            <h2 className="font-semibold text-gray-800 mb-2 flex items-center space-x-2">
              <svg className="h-4 w-4 text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.732 19.299A1 1 0 0113 18V8h-2v10a1 1 0 01-.732 1.299"></path>
                <path d="M16.268 10.701A1 1 0 0015 12H9a1 1 0 000 2h6z"></path>
              </svg>
              Ask About This Kural
            </h2>
            <div className="space-y-4">
              <EducationalChat
                image={image}
                prediction={prediction}
              />
            </div>
          </section>
        </div>

        {/* Action Bar */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Analysis ID: {Math.random().toString(36).substr(2, 9)}
            </div>
            <div className="flex space-x-3">
              <Button
                variant="outline"
                onClick={handleRefresh}
                size="sm"
              >
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4v5h-3"></path>
                  <path d="M10 4H7a2 2 0 00-2 2v2"></path>
                  <path d="M20 4v5h3"></path>
                  <p>Refresh Analysis</p>
                  <path d="M14 4h3a2 2 0 012 2v2"></path>
                </svg>
                Refresh
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate('/')}
                size="sm"
              >
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14"></path>
                  <path d="M12 5l7 7-7 7"></path>
                </svg>
                New Analysis
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Results;