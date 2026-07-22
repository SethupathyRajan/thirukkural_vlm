"""
Demonstration of the Educational Conversation Engine for the Thirukkural
Scenario-Based Decision-Making System.

This script shows how to use the conversation engine with the existing
inference and explainability engines to have an educational conversation
about a retrieved Thirukkural concept.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from inference import InferenceEngine
from explainability import ExplainabilityEngine
from conversation_engine import ConversationEngine


def main():
    print("Thirukkural Scenario-Based Decision-Making System")
    print("Phase 3.3: Educational Conversation Engine Demo")
    print("=" * 55)

    # Initialize engines
    print("\n1. Initializing inference engine...")
    inference_engine = InferenceEngine()
    inference_engine.load()
    print("   ✓ Inference engine ready")

    print("\n2. Initializing explainability engine...")
    explainability_engine = ExplainabilityEngine()
    print("   ✓ Explainability engine ready")

    print("\n3. Initializing conversation engine...")
    conversation_engine = ConversationEngine()
    print("   ✓ Conversation engine ready")

    # Make a prediction
    image_path = Path(__file__).parent / "dataset" / "images" / "S001.jpg"
    if not image_path.exists():
        print(f"\n⚠️  Warning: Image not found at {image_path}")
        print("   Using a placeholder prediction for demonstration...")

        # We'll simulate a prediction for demonstration purposes
        # In a real scenario, we would use the actual image
        from prediction import Prediction, MatchResult

        # Create a mock prediction for demonstration
        mock_prediction = Prediction(
            scenario_id="S001",
            kural_id=1,
            concept="Wisdom",
            adhigaram="Chapter 1 (Aram)",
            paal="Aram",
            english_kural="Having investigated learning, it has been stated that it is unfading.  \
                             Learning that is enjoyed by children and causes joy is perfect.",
            scenario="Student practicing Tamil letter 'அ' on slate before reading words",
            question="Your teacher has assigned a new Tamil poem to learn, but you're struggling with the basic letters. Skipping the alphabet practice would let you start the poem sooner. How do you approach your study session?",
            correct_answer="A",
            explanation="Strong foundations enable confident advancement in learning. When we thoroughly master basic concepts before moving to more complex material, we build lasting understanding that prevents frustration and the wasted effort of having to backtrack and relearn fundamentals later in the learning process.",
            image_similarity=1.0,
            knowledge_similarity=1.0,
            combined_score=1.0,
            confidence=1.0,
            top_matches=[
                MatchResult("S001", 1.0, 1.0, 1.0, "Wisdom", "Having investigated learning, it has been stated that it is unfading.  Learning that is enjoyed by children and causes joy is perfect."),
                MatchResult("S002", 0.85, 0.86, 0.84, "Ethics", "Some other ethical concept"),
                MatchResult("S003", 0.80, 0.81, 0.79, "Knowledge", "Another knowledge concept")
            ]
        )
        prediction = mock_prediction
        print("   ⚠️  Using mock prediction for demonstration")
    else:
        print(f"\n4. Making prediction for {image_path.name}...")
        prediction = inference_engine.predict(str(image_path))
        print(f"   ✓ Prediction: {prediction.scenario_id} (confidence: {prediction.confidence:.4f})")

    # Generate explanation
    print("\n5. Generating explanation...")
    explanation = explainability_engine.generate_explanation(prediction)
    print("   ✓ Explanation generated")

    # Show the explanation (optional)
    print("\n6. Generated Explanation:")
    print("-" * 50)
    print(explainability_engine.format_explanation(explanation))
    print("-" * 50)

    # Initialize conversation engine with the prediction and explanation
    print("\n7. Initializing conversation with the retrieved knowledge...")
    conversation_engine.initialize(prediction, explanation)
    print("   ✓ Conversation ready")

    # Demonstrate educational conversation
    print("\n8. Educational Conversation Demo:")
    print("-" * 40)

    # Question 1: Simple explanation
    question1 = "Explain this Kural in simple English."
    print(f"\nQ: {question1}")
    answer1 = conversation_engine.ask(question1)
    print(f"A: {answer1}")

    # Question 2: Request for an example
    question2 = "Can you give me another real-life example of this principle?"
    print(f"\nQ: {question2}")
    answer2 = conversation_engine.ask(question2)
    print(f"A: {answer2}")

    # Question 3: Application to daily life
    question3 = "How can I apply this teaching in my daily life?"
    print(f"\nQ: {question3}")
    answer3 = conversation_engine.ask(question3)
    print(f"A: {answer3}")

    # Question 4: Comparison (will show limitation)
    question4 = "How does this compare to the concept of justice in Thirukkural?"
    print(f"\nQ: {question4}")
    answer4 = conversation_engine.ask(question4)
    print(f"A: {answer4}")

    # Question 5: For a student
    question5 = "Explain this to a school student."
    print(f"\nQ: {question5}")
    answer5 = conversation_engine.ask(question5)
    print(f"A: {answer5}")

    # Show conversation history
    print("\n9. Conversation History:")
    print("-" * 40)
    history = conversation_engine.get_history()
    for i, turn in enumerate(history, 1):
        print(f"{i}. {turn['role'].capitalize()}: {turn['content'][:100]}{'...' if len(turn['content']) > 100 else ''}")

    print("\n✓ Demo completed successfully!")
    print("\nNote: This demonstration used a mock conversation model.")
    print("In a production setting, you would plug in a real LLM (like Claude, GPT, or a local model)")
    print("through the ConversationModel abstraction layer.")


if __name__ == "__main__":
    main()