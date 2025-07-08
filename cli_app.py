import json
import os
from datetime import datetime
from video_generator import generate_video, load_config

def get_wojak_characters(base_path="assets/wojacks"):
    characters = {}
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, file).replace("\\", "/")
                relative_path = os.path.relpath(full_path, start=base_path).replace("\\", "/")
                characters[relative_path] = full_path
    return characters

def main():
    config = load_config("config.json")
    available_characters = get_wojak_characters()

    print("Welcome to the Wojak Video Maker CLI!")
    print("-------------------------------------")

    # Display available characters
    print("Available Wojak Characters:")
    for i, (rel_path, full_path) in enumerate(available_characters.items()):
        print(f"{i+1}. {rel_path}")

    selected_characters_config = []
    while True:
        try:
            char_choice = input("\nEnter the number of a Wojak character to add (or 'done' to finish): ")
            if char_choice.lower() == 'done':
                break

            char_index = int(char_choice) - 1
            if 0 <= char_index < len(available_characters):
                selected_rel_path = list(available_characters.keys())[char_index]
                selected_full_path = available_characters[selected_rel_path]

                start_time = float(input(f"Enter start time for {selected_rel_path} (seconds): "))
                duration = float(input(f"Enter duration for {selected_rel_path} (seconds): "))
                text = input(f"Enter text for {selected_rel_path} (optional, leave blank for none): ")
                side = input(f"Enter side for {selected_rel_path} (left/right, default: left): ") or "left"
                rotate_input = input(f"Rotate {selected_rel_path} if on right side? (yes/no, default: yes): ") or "yes"
                rotate = rotate_input.lower() == 'yes'

                selected_characters_config.append({
                    "image": selected_full_path,
                    "start_time": start_time,
                    "duration": duration,
                    "text": text,
                    "side": side,
                    "rotate": rotate
                })
            else:
                print("Invalid character number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'done'.")

    if not selected_characters_config:
        print("No characters selected. Exiting.")
        return

    # Update config with selected characters
    config["characters"] = selected_characters_config

    # Generate video
    output_path = generate_video(config)

    print(f"\nVideo generated successfully: {output_path}")

if __name__ == "__main__":
    main()
