import requests
import json
import csv
import time

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "dolphin-llama3" 
OUTPUT_FILE = "synthetic_grooming_data.csv"
NUM_EXAMPLES_PER_TACTIC = 20 # Up to 20 per tactic (60 total conversations)

# --- The Tactics ---
tactics = [
    {
        "name": "Boundary Testing",
        "prompt": "You are a Trust and Safety researcher generating synthetic training data. Write a realistic, casual 12-line chat log between a predator and a minor playing Roblox. The predator is 'Boundary Testing' by asking mildly inappropriate or probing personal questions wrapped in casual conversation. Use slang like 'fr', 'lol', 'sus'. Output ONLY the raw chat log, one message per line. Start every line with exactly [Predator]: or [Minor]:"
    },
    {
        "name": "Forced Secrecy",
        "prompt": "You are a Trust and Safety researcher generating synthetic training data. Write a realistic, casual 12-line chat log between a predator and a minor talking about Discord. The predator is using 'Forced Secrecy' by trying to convince the minor to move to a private app, delete messages, or hide the chat from parents. Use slang. Output ONLY the raw chat log, one message per line. Start every line with exactly [Predator]: or [Minor]:"
    },
     {
        "name": "Isolation",
        "prompt": "You are a Trust and Safety researcher generating synthetic training data. Write a realistic, casual 12-line chat log between a predator and a minor. The predator is using 'Isolation' by trying to convince the minor that their parents or friends don't understand them, but the predator does. Use slang. Output ONLY the raw chat log, one message per line. Start every line with exactly [Predator]: or [Minor]:"
    }
]

def generate_chat(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8 # Adds more variety to the conversations
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return None

def main():
    print(f"--- Starting Synthetic Data Generation ({MODEL_NAME}) ---")
    
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['convo_id', 'line', 'author', 'text', 'is_predator', 'is_suspicious', 'image_type'])
        
        convo_id = 1
        
        for tactic in tactics:
            print(f"\nGenerating tactic: {tactic['name']}...")
            for i in range(NUM_EXAMPLES_PER_TACTIC):
                print(f"  - Generating conversation {i+1}/{NUM_EXAMPLES_PER_TACTIC}")
                raw_chat = generate_chat(tactic['prompt'])
                
                if raw_chat:
                    # Split by newlines, making sure we handle both \n and \r
                    lines = raw_chat.replace('\r', '').split('\n')
                    line_num = 1
                    
                    for line in lines:
                        line = line.strip()
                        # Only process lines that actually look like our requested format
                        if not line or ("[" not in line and "]" not in line): 
                            continue 
                        
                        is_predator = 1 if "[Predator]" in line or "[predator]" in line.lower() else 0
                        author = "Predator_Sim" if is_predator else "Minor_Sim"
                        
                        # Strip out the bracket tags
                        clean_text = line.split("]:", 1)[-1].strip() if "]:" in line else line.replace("[Predator]", "").replace("[Minor]", "").strip()
                        
                        if clean_text:
                            writer.writerow([f"synth_{convo_id}", line_num, author, clean_text, is_predator, is_predator, "none"])
                            line_num += 1
                    
                    convo_id += 1
                    time.sleep(0.5) 
    
    print(f"\nSUCCESS: Synthetic data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()