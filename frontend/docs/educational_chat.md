# Educational Chat Interface

## Component Hierarchy

```
EducationalChat
├── SuggestedQuestions (shown when conversation is empty)
├── EmptyConversation (shown when conversation is empty)
├─┐ｽ ChatMessage┞:¸?5F_repeat 2n for or each message
└── ChatInput
```

### EducationalChat
Main container that manages the chat state and handles API communication.

### SuggestedQuestions
Displays a list of suggested questions when the conversation is empty. Clicking a question sends it immediately.

### EmptyConversation
Shows a placeholder message when there are no messages in the conversation.

### ChatHistory
Displays the list of messages exchanged in the conversation.

### ChatMessage
Individual message for decade or clarification content (if the user or assistant is typing).

### ChatInput
Input field with send button, handling user input and submission.

## API Flow

The educational chat integrates with the existing backend conversation engine through the `/chat` endpoint.

### Request
When the user submits a question:
```
POST /chat
Content-Type: application/json

{
  "message": "User's question text",
  "context": {
    // The prediction object from the analysis results
    "tirukkuralNumber": number | string,
    "tamilCouplet": string,
    "englishTranslation": string,
    "concept": string,
    "confidence": {
      "overall": number,
      "imageSimilarity": number,
      "knowledgeSimilarity": number,
      "combinedScore": number
    },
    "explanation": string,
    "alternativeMatches": [
      {
        "tirukkuralNumber": number | string,
        "tamilCouplet": string,
        "englishTranslation": string,
        "concept": string,
        "combinedScore": number
      }
    ],
    "analysisSteps": {
      "imageAnalyzed": boolean,
      "kuralFound": boolean,
      "conceptIdentified": boolean,
      "explanationGenerated": boolean
    }
  }
}
```

### Response
The backend returns a response containing the assistant's reply:
```
{
  "response": "Assistant's answer text"
}
```
or alternatively:
```
{
  "message": "Assistant's answer text"
}
```
or a plain string.

The `EducationalChat` component handles these formats to extract the response text.

## Conversation Lifecycle

1. **Initial State**: When the Results page loads with analysis results, the chat section is initialized with an empty message list.
2. **Empty State**: Shows suggested questions and an invitation to start the conversation.
3. **User Interaction**: 
   - User clicks a suggested question or types a custom question and presses Enter or clicks the Ask button.
   - Input is disabled and shows "Thinking..." during API request.
   - On success: User message and assistant response are appended to the conversation.
   - On error: Error message is displayed, but conversation history is preserved.
4. **Non-Empty State**: Once at least one message is exchanged, suggested questions are hidden and the chat history is shown.
5. **Reset Conversation**: The backend provides a `DELETE /chat/reset` endpoint to clear the conversation session. The frontend can call this to reset the chat state.

### Reset Functionality
The backend provides a `DELETE /chat/reset` endpoint to clear the conversation session. The frontend can call this to reset the chat state.

## Suggested Questions

The following suggestions are displayed when the conversation is empty:
- Explain this Kural in simple English.
- Give another real-life example.
- Why is this important?
- How can I apply this in daily life?
- Teach this to a school student.
- Summarize this Kural.

These are not hardcoded responses; they are prompts that are sent to the backend as regular user questions.

## Error Handling

The chat handles the following error scenarios:
- **Backend Unavailable**: Shows "Unable to get a response. Please try again."
- **Timeout**: Same as above (handled by axios timeout).
- **Invalid Response**: Falls back to displaying the raw response or a JSON stringified version.
- **Network Issues**: Detects when there's no internet connection and shows appropriate message.

In all error cases:
- The input is re-enabled after the request completes.
- The error message is displayed above the input.
- Conversation history is preserved.

## Accessibility

- **Keyboard Navigation**: 
  - Enter sends the message (unless Shift is held for newline).
  - Tab navigates between input and send button.
  - Suggested questions are focusable buttons.
- **Screen Readers**:
  - Uses semantic HTML elements (button, textarea, form).
  - Proper labeling via placebos and context.
  - Live region could be added for new messages (future enhancement).
- **Focus Management**:
  - Input receives focus when the component mounts.
  - After sending a message, focus returns to the input.

## Responsiveness

- **Desktop**: Chat appears below the Results section in the main column.
- **Tablet**: Stacks naturally with full-width components.
- **Mobile**: 
  - Input adjusts to full width.
  - Textarea expands vertically as needed (but we set fixed rows to avoid excessive growth).
  - All components stack vertically.

## Styling

- Uses the existing design system:
  - Colors: gray-50, blue- etc.
 ｂ Spacing: 8px-based scale.
  - No custom colors, inline styles, etc.  
  - Typography: 
-   - Spacebase: 8pscale.
  - Avoids:
    - Gradients
    - Glassmorphism
    - Floating blobs
    - Glowing effects
    - AI-themed decorations
    - Unnecessary animations

## Future Enhancements

- Add timestamp to messages.
- Implement scrolling to bottom when new messages arrive.
- Add loading skeleton for message bubbles.
- Support for markdown formatting in responses (if backend supports it).
- Voice input button.
- File/image upload within chat (for follow-up questions with images).
- Multiple conversation sessions.
- Conversation persistence across page refreshes (using sessionStorage or backend).