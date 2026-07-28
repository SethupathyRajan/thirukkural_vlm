#!/usr/bin/env python3
"""
CLI Interface for Thirukkural Educational AI
This script provides a command-line interface to upload an image, ask a question,
and get a Thirukkural-based answer with explanation.
"""

import sys
import os
import json
import base64
import mimetypes
from pathlib import Path

# Try to import tkinter for file dialog
try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    import requests
except ImportError:
    print("Error: The 'requests' library is required but not installed.")
    print("Please install it using: pip install requests")
    sys.exit(1)

# Configuration
CHAT_URL = "http://localhost:8000/chat/"  # endpoint that accepts image+question
TIMEOUT = 30  # seconds

def validate_image_file(file_path):
    """Validate that the file exists and is an image."""
    if not os.path.isfile(file_path):
        return False, f"File not found: {file_path}"

    # Check file extension
    valid_extensions = {'.png', '.jpg', '.jpeg', '.jpe', '.jfif'}
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in valid_extensions:
        return False, f"Unsupported file extension: {ext}. Supported: {', '.join(valid_extensions)}"

    # Optional: Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and not mime_type.startswith('image/'):
        return False, f"File does not appear to be an image: {mime_type}"

    return True, ""

def encode_image_to_base64(image_path):
    """Read image file and return base64 encoded string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def chat_with_image(image_b64, question):
    """Send image and question to the /chat/ endpoint and return response."""
    try:
        payload = {
            "image": image_b64,
            "question": question
        }
        response = requests.post(CHAT_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to the backend. Ensure the backend server is running on http://localhost:8000"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The backend may be overloaded or unresponsive."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Backend returned an error: {e.response.status_code} - {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred during the request: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid response from backend: not valid JSON"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def display_result(prediction, answer, explanation):
    """Display the prediction, answer, and explanation in a user-friendly format."""
    print("\n" + "="*60)
    print("🎯 THIRUKKURAL PREDICTION & ANSWER")
    print("="*60)

    print(f"\n🔢 Kural ID: {prediction.get('kural_id', 'N/A')}")
    print(f"💡 Concept: {prediction.get('concept', 'N/A')}")
    print(f"📖 Chapter (Adhigaram): {prediction.get('adhigaram', 'N/A')}")
    print(f"📚 Section (Paal): {prediction.get('paal', 'N/A')}")

    # English Kural formatted 4-3
    english_kural = prediction.get('english_kural', 'N/A')
    if english_kural != 'N/A':
        words = english_kural.split()
        if len(words) >= 7:
            line1 = " ".join(words[:4])
            line2 = " ".join(words[4:7])
            if len(words) > 7:
                line2 += " " + " ".join(words[7:])
            print(f"\n📜 English Kural:")
            print(f"   {line1}")
            print(f"   {line2}")
        else:
            # fallback: just print as is
            print(f"\n📜 English Kural:")
            print(f"   {english_kural}")
    else:
        print(f"\n📜 English Kural: N/A")

    print(f"\n✅ Correct Answer (from prediction): {prediction.get('correct_answer', 'N/A')}")

    print(f"\n💬 Explanation:")
    print(f"   {explanation}")

    print(f"\n📊 Similarity Scores:")
    print(f"   • Image Similarity: {prediction.get('image_similarity', 0):.4f}")
    print(f"   • Knowledge Similarity: {prediction.get('knowledge_similarity', 0):.4f}")
    print(f"   • Combined Score: {prediction.get('combined_score', 0):.4f}")
    print(f"   • Confidence: {prediction.get('confidence', 0):.4f}")

    # Top matches (optional)
    top_matches = prediction.get('top_matches', [])
    if top_matches:
        print(f"\n🔝 Top Matches:")
        for i, match in enumerate(top_matches[:5], 1):
            print(f"   {i}. Scenario {match.get('scenario_id', 'N/A')} (Score: {match.get('combined_score', 0):.4f})")
            print(f"      Concept: {match.get('concept', 'N/A')}")
            print(f"      Kural: {match.get('english_kural', 'N/A')[:100]}...")

    # Answer to user's question
    print(f"\n❓ Answer to your question:")
    print(f"   {answer}")

    print("\n" + "="*60)

def select_via_dialog():
    """Open a file dialog to select an image file."""
    if not TKINTER_AVAILABLE:
        return None, "tkinter is not available for file dialog"

    root = tk.Tk()
    root.withdraw()
    root.update()
    file_path = filedialog.askopenfilename(
        title="Select an image file",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.jpe *.jfif"),
            ("All files", "*.*")
        ]
    )
    root.destroy()

    if not file_path:
        return None, "No file selected"
    return file_path, ""

def main():
    """Main function to run the CLI interface."""
    print("🔍 Thirukkural Educational AI - CLI Interface")
    print("-" * 50)
    print("Ask a question, provide an image, and get a Thirukkural-based answer.")

    if TKINTER_AVAILABLE:
        print("💡 Tip: You can use the file dialog to select an image, or enter a path manually.")
    else:
        print("⚠️  File dialog not available (tkinter missing). Please enter image paths manually.")

    while True:
        # 1. Ask the user for a question
        question = input("\n❓ Enter your question about the image (or 'quit' to exit): ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        if not question:
            print("⚠️  Please enter a valid question.")
            continue

        # 2. Get image path (dialog or manual)
        if TKINTER_AVAILABLE:
            choice = input("\n📁 Select image via (d)ialog or (p)ath entry? [d/p]: ").strip().lower()
            if choice == 'd':
                image_path, error_msg = select_via_dialog()
                if error_msg:
                    print(f"❌ {error_msg}")
                    continue
                if not image_path:
                    print("⚠️  No file selected. Please try again.")
                    continue
            elif choice == 'p':
                image_path = input("\n📁 Enter the path to an image file: ").strip()
                if not image_path:
                    print("⚠️  Please enter a valid file path.")
                    continue
                # Remove surrounding quotes if present
                if (image_path.startswith('"') and image_path.endswith('"')) or \
                   (image_path.startswith("'") and image_path.endswith("'")):
                    image_path = image_path[1:-1]
            else:
                print("⚠️  Invalid choice. Please enter 'd' or 'p'.")
                continue
        else:
            image_path = input("\n📁 Enter the path to an image file: ").strip()
            if not image_path:
                print("⚠️  Please enter a valid file path.")
                continue
            # Remove surrounding quotes if present
            if (image_path.startswith('"') and image_path.endswith('"')) or \
               (image_path.startswith("'") and image_path.endswith("'")):
                image_path = image_path[1:-1]

        # 3. Validate the image file
        is_valid, error_msg = validate_image_file(image_path)
        if not is_valid:
            print(f"❌ {error_msg}")
            continue

        # 4. Encode image to base64
        print(f"\n📤 Encoding image: {image_path}")
        try:
            image_b64 = encode_image_to_base64(image_path)
        except Exception as e:
            print(f"❌ Failed to encode image: {e}")
            continue

        # 5. Send request to backend
        print("⏳ Getting answer from the AI...")
        result = chat_with_image(image_b64, question)

        if "error" in result:
            print(f"\n❌ {result['error']}")
            continue

        # 6. Extract needed fields from response
        # Expected keys: answer, prediction, explanation
        answer = result.get('answer', 'No answer provided.')
        explanation = result.get('explanation', 'No explanation provided.')
        prediction = result.get('prediction', {})

        # 7. Display results
        display_result(prediction, answer, explanation)

        # 8. Ask if user wants to continue
        if input("\n🔄 Ask another question? (y/n): ").lower() not in ['y', 'yes']:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 An unexpected error occurred: {str(e)}")
        sys.exit(1)