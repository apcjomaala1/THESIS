import requests
import json
import csv
import time

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "dolphin-llama3" # You can use standard "llama3" here too, both work for safe text!
OUTPUT_FILE = "synthetic_safe_data.csv"
NUM_EXAMPLES_PER_SCENARIO = 20 # 20 per scenario = 60 total safe conversations

# --- The Safe Scenarios (Hard Negatives) ---
scenarios = [
    {
        "name": "Casual Roblox Gaming",
        "prompt": "Write a realistic, casual 12-line chat log between two teenage friends playing Roblox. They are talking about a new game update, trading items, or lagging. Use internet slang like 'fr', 'lol', 'bet', 'lag'. Output ONLY the raw chat log, one message per line. Start every line with exactly [User A]: or [User B]:"
    },
    {
        "name": "School and Homework",
        "prompt": "Write a realistic, casual 12-line chat log between two classmates complaining about an upcoming exam or a strict teacher. Use casual teenage slang like 'rn', 'ngl', 'bruh'. Output ONLY the raw chat log, one message per line. Start every line with exactly [User A]: or [User B]:"
    },
     {
        "name": "Discord Hanging Out",
        "prompt": "Write a realistic, casual 12-line chat log between two friends hanging out in a Discord server. They are talking about sharing memes, listening to music, or playing Stardew Valley. Use slang. Output ONLY the raw chat log, one message per line. Start every line with exactly [User A]: or [User B]:"
    }
]

def generate_chat(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8 # Keeps the chats varied and natural
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
    print(f"--- Starting Safe Synthetic Data Generation ({MODEL_NAME}) ---")
    
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['convo_id', 'line', 'author', 'text', 'is_predator', 'is_suspicious', 'image_type'])
        
        convo_id = 1
        
        for scenario in scenarios:
            print(f"\nGenerating scenario: {scenario['name']}...")
            for i in range(NUM_EXAMPLES_PER_SCENARIO):
                print(f"  - Generating safe conversation {i+1}/{NUM_EXAMPLES_PER_SCENARIO}")
                raw_chat = generate_chat(scenario['prompt'])
                
                if raw_chat:
                    lines = raw_chat.replace('\r', '').split('\n')
                    line_num = 1
                    
                    for line in lines:
                        line = line.strip()
                        if not line or ("[" not in line and "]" not in line): 
                            continue 
                        
                        # Labels are strictly 0 (Safe)
                        is_predator = 0
                        is_suspicious = 0
                        author = "User_A_Sim" if "[User A]" in line or "[user a]" in line.lower() else "User_B_Sim"
                        
                        # Strip out the bracket tags
                        clean_text = line.split("]:", 1)[-1].strip() if "]:" in line else line.replace("[User A]", "").replace("[User B]", "").strip()
                        
                        if clean_text:
                            writer.writerow([f"safe_synth_{convo_id}", line_num, author, clean_text, is_predator, is_suspicious, "none"])
                            line_num += 1
                    
                    convo_id += 1
                    time.sleep(0.5) 
    
    print(f"\nSUCCESS: Safe synthetic data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()