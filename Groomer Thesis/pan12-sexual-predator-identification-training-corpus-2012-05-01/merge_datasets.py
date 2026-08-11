import pandas as pd

def main():
    print("--- Assembling Master Training Dataset (V2) ---")

    # 1. List all your datasets (Including the new Synthetic one!)
    dataset_files = [
        'pan12_final_dataset.csv',             
        'anonymized_group_chat_dataset.csv',   
        'DiscordCommunityChat.csv',            
        'RobloxPredatorTriesToRun.csv',        
        'WeGotARobloxPredatorArrested.csv',    
        'WeGotARobloxPredatorArrested2.csv',
        'synthetic_grooming_data.csv'          # <--- Added our new local data!
    ]

    dataframes = []
    
    # 2. Load the data (Keeping ALL columns this time)
    for file in dataset_files:
        try:
            df = pd.read_csv(file)
            
            # Notice we are no longer filtering out is_suspicious or author!
            # We append the whole rich dataframe.
            dataframes.append(df)
            print(f"✅ Loaded {file}: {len(df)} rows")
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")

    # 3. Merge, Clean, and Shuffle
    print("\nMerging and cleaning data...")
    master_df = pd.concat(dataframes, ignore_index=True)
    
    # We still want to drop rows that are completely blank or missing the core label
    master_df = master_df.dropna(subset=['text', 'is_predator']) 
    master_df['text'] = master_df['text'].astype(str)
    
    # Shuffle the dataset so positive and negative cases are randomized
    master_df = master_df.sample(frac=1, random_state=42).reset_index(drop=True) 

    # 4. Save the finalized output
    output_name = 'master_training_dataset.csv'
    master_df.to_csv(output_name, index=False)
    print(f"\nSUCCESS: Dataset created as '{output_name}' with {len(master_df)} total rows.")
    print("Columns retained:", list(master_df.columns))

if __name__ == "__main__":
    main()