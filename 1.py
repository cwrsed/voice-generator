from elevenlabs import ElevenLabs, Voice, VoiceSettings, save, play
from dotenv import load_dotenv
import json
import os
import io

def load_settings():
    settings_path = "settings.json"
    default_settings = {
        "stability": 0.50, 
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True,
        "model_id": "eleven_multilingual_v2"
    }

    if not os.path.exists(settings_path):
        with open(settings_path, "w") as file:
            json.dump(default_settings, file, indent=4)

    with open(settings_path, "r") as file:
        return json.load(file)

def edit_settings():
    with open("settings.json", "r+") as file:
        settings = json.load(file)
        while True:
            try:
                clear_console()
                for i, (k, v) in enumerate(settings.items(), 1):
                    print(f"[{i}] {k}: {v}")
                option = int(input("Select option to edit (0 to exit): "))
                if option == 0: return
                sett = list(settings.keys())[option-1]
            except (IndexError, ValueError):
                    print("Invalid option")
                    os.system("pause")
                    continue

            match sett:
                case "use_speaker_boost":
                    changeItem = input("True or False? (t/f): ").lower()
                    if changeItem == 't': settings[sett] = True
                    elif changeItem == 'f': settings[sett] = False
                case "model_id":
                    changeItem = input("Enter model: ").lower()
                    settings[sett] = changeItem
                case _:
                    while True:
                        changeItem = float(input("Enter a number between 0.0 to 1.0: "))
                        if 0.0 <= changeItem <= 1.0: 
                            settings[sett] = changeItem
                            break
            file.seek(0)
            json.dump(settings, file, indent=4)
            file.truncate()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def verify_api_key(client):
    try:
        client.voices.get_all(show_legacy=True)
        return True
    except Exception as e:
        print(f"Invalid API Key. Error message: {e}")
        return False
    
def get_api_key():
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not api_key:
        while True:
            api_key = input("Enter your ElevenLabs API Key: ").strip()
            client = ElevenLabs(api_key=api_key)

            if verify_api_key(client):
                with open(".env", "w") as env_file:
                    env_file.write(f"\nELEVENLABS_API_KEY={api_key}")
                print("API Key saved to .env ✅")
                os.system("pause")
                return api_key

    return api_key

def start_program():
    client = ElevenLabs(
        api_key=get_api_key(),
    )

    while True:
        clear_console()

        voice_list = get_voices(client)

        if voice_list == None:
            print("An error occurred while fetching the voices.")
            break
        
        list_voices(voice_list)
        
        voice = select_voice(voice_list)

        if voice == None:
            return

        text = get_text()

        settings = load_settings()

        i = 0
        while True:
            audio = generate_voice(text, voice, settings, client)

            if audio == None:
                break

            option = input("Do you want to save the audio? ([y]es/[n]o/[b]ack): ").lower()
            match option:
                case "y":
                    i = 1
                    while os.path.exists(f"audio_{i}.mp3"):
                        i += 1
                    save(audio, f"audio_{i}")
                    break
                case "b":
                    break
                case "n":
                    pass

def generate_voice(text, voice, settings, client):
    clear_console()
    print("Generating audio...")
    try:
        audio = client.generate(
            text=text,
            voice=Voice(
                voice_id=voice,
                settings=VoiceSettings(
                    stability=settings["stability"],
                    similarity_boost=settings["similarity_boost"],
                    style=settings["style"],
                    use_speaker_boost=settings["use_speaker_boost"],
                    model_id=settings["model_id"]
                )
            )
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        os.system("pause")
        return None
    
    audio_bytes = b"".join(audio)
    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.seek(0)
    play(audio_stream)

    return audio

def get_text():
    print("Digite o texto (pressione ENTER para finalizar):")
    lines = []
    while True:
        line = input("> ").strip()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

def select_voice(voice_list):
    voices = list(voice_list.keys())
    while True:
        try:
            voice_num = int(input("Enter the voice number (0 to exit): "))
            if voice_num == 0:
                return None
            if 1 <= voice_num <= len(voices):
                return voice_list[voices[voice_num - 1]]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")

def list_voices(voice_list):
    for i, name in enumerate(voice_list.keys(), 1):
        print(f"[{i}] {name}")

def get_voices(client):
    try:
        voices = json.loads(client.voices.get_all(show_legacy=True).json())
        voice_list = {item['name']: item['voice_id'] for item in voices['voices']}
        voice_list = dict(sorted(voice_list.items()))
        return voice_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        
def main():
    options = {
        "1": edit_settings,
        "2": start_program,
        "3": exit
    }

    while True:
        clear_console()
        print("==== ElevenLabs Voice Generator ====")
        print("1. Adjust Settings")
        print("2. Generate Voice")
        print("3. Exit")
        option = input("Choose an option: ")

        if option in options:
            options[option]()
        else:
            print("Opção inválida. Tente novamente.")
            os.system("pause")

if __name__ == "__main__":
    main()