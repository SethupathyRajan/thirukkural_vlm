# Results Page

## Overview

The Results page displays the analysis results after an image is uploaded and processed by the backend. It follows a specific information hierarchy to present the findings in an educational context.

## Information Hierarchy

The Results page displays information in the exact following order:

1. **Uploaded Image**
   - Shows the image that was uploaded by the user
   - Displays filename and image dimensions (if available)

2. **Matched Thirukkural**
   - Shows the Thirukkural that best matches the uploaded image
   - Displays: Thirukkural number, Tamil couplet, English translation

3. **Ethical Concept Identified**
   - Shows the ethical concept derived from the matched Thirukkural
   - Displays the concept title/description

4. **Confidence Metrics**
   - Shows confidence scores for the analysis
   - Displays: Overall Confidence, Image Similarity, Knowledge Similarity, Combined Score
   - Each metric is shown as a percentage with a visual progress bar

5. **Explanation**
   - Shows the AI-generated reasoning explaining why the Thirukkural matches the image
   - Provides educational context about the connection

6. **Alternative Matches**
   - Shows alternative Thirukkural matches that were considered
   - Displays: Scenario ID, Concept, Combined Score (as percentage)
   - Each alternative includes a visual progress bar for the score

## Component Structure

```
ResultsPage
├── UploadedImageCard
├── KuralCard
├── ConceptCard
├── ConfidenceCard
├── ExplanationCard
└── AlternativeMatchesCard
```

### UploadedImageCard

Displays the uploaded image with filename and dimensions.

**Props:**
- `preview`: string - URL of the image preview
- `name`: string - Filename of the uploaded image
- `width`: number (optional) - Image width in pixels
- `height`: number (optional) - Image height in pixels

### KuralCard

Displays the matched Thirukkural details.

**Props:**
- `tirukkuralNumber`: number | string - The Thirukkural number
- `tamilCouplet`: string - The Tamil couplet of the Thirukkural
- `englishTranslation`: string - The English translation of the Thirukkural

### ConceptCard

Displays the ethical concept identified from the analysis.

**Props:**
- `concept`: string - The ethical concept title/description

### ConfidenceCard

Displays confidence metrics with visual progress bars.

**Props:**
- `confidence`: Object containing:
  - `overall`: number (0-1) - Overall confidence score
  - `imageSimilarity`: number (0-1) - Similarity between image and Thirukkural features
  - `knowledgeSimilarity`: number (0-1) - Similarity based on knowledge base
  - `combinedScore`: number (0-1) - Combined confidence score

### ExplanationCard

Displays the AI-generated explanation.

**Props:**
- `explanation`: string (optional) - The explanation text

### AlternativeMatchesCard

Displays alternative Thirukkural matches.

**Props:**
- `alternatives`: Array of objects, each containing:
  - `scenarioId`: number | string - Identifier for the alternative scenario
  - `concept`: string - Ethical concept of the alternative
  - `combinedScore`: number (0-1) - Confidence score for this alternative

## Data Flow

1. User uploads an image on the Home page
2. Image is validated (type: PNG/JPG/JPEG, size < 5MB)
3. Preview and image dimensions are generated client-side
4. Image is sent to backend `/predict` endpoint via POST request
5. Backend processes the image and returns prediction data
6. Frontend navigates to Results page, passing image and prediction data via React Router `state`
7. Results page extracts data and displays it in the specified hierarchy using components
8. User can navigate back to Home page using the back button

## Styling & Design

- Follows the design system: no gradients, glassmorphism, purple/blue AI themes
- Uses gray color scheme with blue/green/purple/indigo accents for confidence metrics
- Responsive layout: stacks vertically on mobile, can use grid on larger screens
- Accessible: proper heading hierarchy, color contrast, focus states
- Loading states handled on previous page (Home page shows "Analyzing..." during upload)

## Error Handling

- If no state is available (direct navigation to Results), displays message to go back and upload an image
- Component-level error handling for missing data (e.g., AlternativeMatchesCard shows "No alternative matches found" when array is empty)