from transformers import pipeline

def main():
    print("Loading your custom AI model...")
    
    # Load the model you just trained
    classifier = pipeline(
        "text-classification", 
        model="./final_moderation_model", 
        tokenizer="./final_moderation_model"
    )
    
    print("\n--- AI Chat Moderation Active ---")
    print("Type a message to scan it. Type 'quit' to exit.\n")
    
    while True:
        user_input = input("User Message: ")
        
        if user_input.lower() == 'quit':
            print("Shutting down...")
            break
            
        # Run the AI on the input
        result = classifier(user_input)[0]
        
        # Translate the AI's label into readable text
        label = result['label']
        confidence = result['score'] * 100
        
        if label == "LABEL_1":
            print(f"⚠️  FLAGGED: Potential Grooming/Predatory Behavior ({confidence:.2f}% confidence)\n")
        else:
            print(f"✅  SAFE: Normal Conversation ({confidence:.2f}% confidence)\n")

if __name__ == "__main__":
    main()