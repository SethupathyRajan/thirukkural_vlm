# Image Upload Feature Documentation

## Component Hierarchy

```
HomePage
├── Header (from AppLayout)
├── Main Content
│   ├── Alert (for upload errors)
│   ├── Card (Upload Container)
│   │   └── ImageUploader
│   │       ├── UploadPlaceholder (drop zone)
│   │       │   ├── UploadIcon
│   │       │   └ instructions
│   │       ├── ImagePreview (when file selected)
│   │       │   ├── Preview Image
│   │       │   └── Remove Button
│   │       └── UploadActions
│   │           └── Analyze Button (with loading state)
│   └── Action Bar
│       └── Analyze Button (primary action)
```

## Upload Flow

1. **User Interaction**:
   - User visits the home page (`/`)
   - Clicks the upload area or drags/drops an image file
   - System validates file type (PNG, JPG, JPEG) and size (<5MB)
   - If valid, displays image preview with filename, size, and remove option
   - If invalid, shows error message below the upload area

2. **Analysis**:
   - User clicks "Analyze Image" button
   - Button enters loading state (shows "Analyzing..." text)
   - FormData is created with the selected file
   - POST request sent to `/predict` endpoint with multipart/form-data
   - UI controls are disabled during upload

3. **Result Handling**:
   - On success: User navigated to `/results` page with prediction data in state
   - On error: Error message displayed, user can try again
   - On network/server error: Friendly error message shown

## Validation Rules

### File Type Validation
- Accepted MIME types: `image/png`, `image/jpeg`, `image/jpg`
- Rejected types show: "Unsupported file type. Please upload a PNG, JPG, or JPEG image."

### File Size Validation
- Maximum size: 5MB (5,242,880 bytes)
- Oversized files show: "File size too large. Please upload an image smaller than 5MB."

### Additional Validation
- Empty files are rejected by the browser's file input
- No client-side virus scanning (would be done on backend if required)

## API Interaction

### Endpoint
- `POST /predict`
- Content-Type: `multipart/form-data`
- Form data key: `image` (File object)

### Request Example
```javascript
const formData = new FormData();
formData.append('image', fileObject);

await api.post('/predict', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  }
});
```

### Response Handling
- On success (200): Response data is passed to the results page via React Router state
- On error (4xx/5xx): Error is caught and converted to user-friendly message
- Network errors: Handled by axios interceptors and converted to generic message

## Error Handling

### User-Friendly Messages
- File validation errors: Specific to the validation failure
- Upload errors: "Unable to analyze the image. Please try again."
- Network errors: "Unable to connect to the service. Please check your connection and try again."
- Server errors: "The service encountered an error. Please try again later."

### Error Display
- Validation errors: Shown below the upload area in red alert box
- Upload errors: Shown in the same location as validation errors
- All errors are cleared when a new file is selected

### Recovery
- Users can always remove the current file and select a new one
- After error, the analyze button returns to enabled state (if file is present)

## Future Extensions

### Immediate Enhancements
1. **Image Preview Enhancements**:
   - Add image dimensions display
   - Show orientation-corrected preview
   - Add image compression preview

2. **Upload Experience**:
   - Add progress bar for large file uploads
   - Implement chunked upload for very large files
   - Add drag-over visual feedback

3. **Validation**:
   - Add configurable file size limit via environment variables
   - Add MIME type validation based on file content (not just extension)
   - Add virus scanning integration point

### Architectural Improvements
1. **State Management**:
   - Consider using React Query for upload state caching
   - Implement optimistic UI for successful uploads
   - Add upload retry mechanism with exponential backoff

2. **Accessibility**:
   - Add ARIA live regions for dynamic error messages
   - Improve keyboard navigation for drop zone
   - Add screen reader announcements for upload progress

3. **Performance**:
   - Implement image preview generation using Web Workers
   - Add client-side image resizing for thumbnails
   - Implement request deduplication for rapid successive uploads

### Feature Extensions
1. **Multiple File Support**:
   - Allow selecting multiple images
   - Show gallery preview
   - Process batch uploads

2. **Image Editing**:
   - Add basic cropping/rotation before upload
   - Add zoom/pan for preview
   - Add annotation tools (for educational use cases)

3. **Integration Points**:
   - Add direct camera capture support
   - Add clipboard paste support
   - Add integration with cloud storage providers

## Implementation Notes

### Styling
- Uses Tailwind CSS utility classes
- Follows the established design system:
  - White background (`bg-white`)
  - Light gray cards (`bg-gray-50`)
  - Blue accent color (`bg-primary`)
  - Generous spacing (8px grid)
  - No gradients, glassmorphism, or decorative animations

### Accessibility Features Implemented
- Keyboard navigable controls
- ARIA labels for icon buttons
- Focus states on interactive elements
- Semantic HTML structure
- Sufficient color contrast (WCAG AA)
- Responsive design for mobile/tablet/desktop

### Performance Considerations
- Image previews use object URLs (revoked on removal)
- Lazy file reading (only reads when needed)
- No unnecessary re-renders during drag operations
- Button disabled state prevents duplicate submissions