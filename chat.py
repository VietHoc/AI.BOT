import sys
from openai import OpenAI
from termcolor import colored
import speech_recognition as sr
import pyttsx3

class ChatSession:
    def __init__(self):
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant. Show your thinking process between <think></think> tags."}
        ]
        self.recognizer = sr.Recognizer()

    def get_voice_input(self):
        try:
            with sr.Microphone() as source:
                print(colored("\nListening... (speak now)", 'yellow'))
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                print(colored("Processing...", 'yellow'))
                
                text = self.recognizer.recognize_google(audio)
                print(colored(f"\nYou said: {text}", 'green'))
                return text
                
        except sr.WaitTimeoutError:
            print(colored("No speech detected", 'red'))
        except sr.UnknownValueError:
            print(colored("Could not understand audio", 'red'))
        except sr.RequestError as e:
            print(colored(f"Could not request results; {e}", 'red'))
        return None
    
    def speak_response(self, text, rate=150):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(colored(f"Speech error: {e}", 'red'))

def format_response(response):
    # Split response if thinking tags exist
    parts = response.split('<think>')
    if len(parts) > 1:
        thinking = parts[1].split('</think>')[0].strip()
        final_response = parts[-1].strip()
        return (
            colored("\n🤔 Thinking Process:", 'yellow') + 
            colored(f"\n{thinking}", 'cyan') +
            colored("\n\n📝 Response:", 'green') +
            colored(f"\n{final_response}", 'white')
        )
    return colored(f"\n{response}", 'white')

def extract_and_speak_response(response, chat_session, speak=True):
    # Extract final answer after </think> tag
    parts = response.split('</think>')
    final_answer = parts[-1].strip() if len(parts) > 1 else response
    
    # Format complete response for display
    formatted = format_response(response)
    
    # Speak final answer if enabled
    if speak:
        chat_session.speak_response(final_answer)
        
    return formatted


def create_chat_completion(prompt, chat_session, model="gpt-3.5-turbo"):
    try:
        client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="sk-xxxxxx"
        )

        chat_session.messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=model,
            messages=chat_session.messages
        )
        
        assistant_message = response.choices[0].message.content
        chat_session.messages.append({"role": "assistant", "content": assistant_message})
        return format_response(assistant_message)

    except Exception as e:
        print(colored(f"Error: {str(e)}", 'red'), file=sys.stderr)
        return None
    
def process_voice_input(chat_session):
    try:
        text = chat_session.get_voice_input()
        if text:
            response = create_chat_completion(text, chat_session)
            if response:
                print("\nAI:", response)
        return text
    except Exception as e:
        print(colored(f"Error processing voice input: {e}", 'red'))
        return None
    
def main():
    chat_session = ChatSession()
    voice_output = False
    
    while True:
        cmd = input(colored("\nCommand (t/v/s/exit): ", 'cyan')).strip().lower()
        
        if cmd == 'exit':
            break
        elif cmd == 's':
            voice_output = not voice_output
            print(colored(f"Speech output: {'enabled' if voice_output else 'disabled'}", 'yellow'))
            continue
            
        if cmd == 'v':
            prompt = chat_session.get_voice_input()
        else:
            prompt = input(colored("\nYou: ", 'green')).strip()
            
        if prompt:
            response = create_chat_completion(prompt, chat_session)
            if response:
                print(extract_and_speak_response(response, chat_session, voice_output))

if __name__ == "__main__":
    main()