import sys
import json
import os
import subprocess
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

def create_chat_completion(prompt, chat_session, model="gpt-3.5-turbo"):
    try:
        client = OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="sk-1234567890"
        )
        
        chat_session.messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=model,
            messages=chat_session.messages
        )
        
        assistant_message = response.choices[0].message.content
        chat_session.messages.append({"role": "assistant", "content": assistant_message})
        return assistant_message

    except Exception as e:
        print(colored(f"Error: {str(e)}", 'red'), file=sys.stderr)
        return None

def users():
    return [
        {"name": "Hoc", "email": "viethocle2603@gmail.com"},
        {"name": "Duy", "email": "duy@example.com"},
        {"name": "Huy", "email": "huy@example.com"}
    ]

def find_recipient(chat_message, user_list):
    chat_message_lower = chat_message.lower()
    for user in user_list:
        if user["name"].lower() in chat_message_lower:
            return user["email"], user["name"]
    return None, None

def extract_json_from_response(response_text):
    try:
        # Find JSON content between triple backticks
        if '```json' in response_text:
            json_text = response_text.split('```json')[1].split('```')[0].strip()
        else:
            # Try to find first valid JSON in the text
            json_text = response_text.strip()
            
        email_data = json.loads(json_text)
        
        # Validate required fields
        required_fields = ['to', 'subject', 'body']
        if all(field in email_data for field in required_fields):
            return email_data
        else:
            return {"error": "Missing required email fields"}
            
    except json.JSONDecodeError:
        return {"error": "Failed to parse email JSON"}
    except Exception as e:
        return {"error": f"Error processing email: {str(e)}"}
    
def format_email_speech(email_data):
    try:
        return (
            f"Email generated successfully. "
            f"To: {email_data['to']}. "
            f"Subject: {email_data['subject']}. "
            f"Body: {email_data['body']}"
        )
    except KeyError:
        return "Error formatting email content"
def open_mail_app(email):
    try:
        subject = email["subject"]
        body = email["body"]
        recipient = email["to"]
        
        mailto_link = f"mailto:{recipient}?subject={subject}&body={body}"
        subprocess.run(["open", mailto_link], check=True)
        print(colored("Opened Mail app with email draft.", 'green'))
    except Exception as e:
        print(colored(f"Error opening Mail app: {e}", 'red'))
    
def generate_email(chat_message, user_list):
    recipient_email, recipient_name = find_recipient(chat_message, user_list)
    
    if not recipient_email:
        return {"error": "No matching recipient found."}
    
    prompt = f"""
    You are an AI assistant that generates professional emails based on a given user message.
    
    **User Message:** "{chat_message}"
    **Recipient Name:** {recipient_name}
    **Recipient Email:** {recipient_email}
    **My name is Hoc Le.**
    **My birthday is March 26.**
    
    Generate an appropriate email with a subject and body.
    Output JSON format:
    {{
      "to": "{recipient_email}",
      "subject": "Generated Email Subject",
      "body": "Generated Email Body"
    }}
    """
    
    chat_session = ChatSession()
    response_text = create_chat_completion(prompt, chat_session)
    
    try:
        print("\nAI:", response_text)
        return extract_json_from_response(response_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response as JSON."}

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

        prompt = chat_session.get_voice_input() if cmd == 'v' else input(colored("\nYou: ", 'green')).strip()

        if prompt:
            if "send email" in prompt.lower():
                print(colored("Processing email request...", 'yellow'))
                email = generate_email(prompt, users())
                if "error" in email:
                    print(colored(f"Error: {email['error']}", 'red'))
                else:
                    print(colored("Email generated successfully!", 'green'))
                    print(json.dumps(email, indent=4))
                    # Send email here
                    # open email in macOS and paste the generated email
                    open_mail_app(email)
                    speech_content = format_email_speech(email)
                    chat_session.speak_response(speech_content)
                continue
            
            response = create_chat_completion(prompt, chat_session)
            if response:
                print("\nAI:", response)
                if voice_output:
                    chat_session.speak_response(response)

if __name__ == "__main__":
    main()
