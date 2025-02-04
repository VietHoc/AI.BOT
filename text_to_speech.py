import pyttsx3

def speak_japanese(text, voice_id):
    engine = pyttsx3.init()
    engine.setProperty('voice', voice_id)
    engine.say(text)
    engine.runAndWait()

# Danh sách giọng tiếng Nhật
voices = [
    "com.apple.eloquence.ja-JP.Eddy",
    "com.apple.eloquence.ja-JP.Flo",
    "com.apple.eloquence.ja-JP.Grandma",
    "com.apple.eloquence.ja-JP.Grandpa",
    "com.apple.voice.compact.ja-JP.Kyoko"
]

# Văn bản tiếng Nhật
text = "DESTINY-Breast06試験では具体的に転移性乳癌(mBC)の中でもHER2低発現または、HER2超低発現患者（新しい分類の患者タイプ）に対してトラスツズマブデルクステカン(TDXd)をファーストライン化学療法として処方した場合に着目した。"

for voice in voices:
    print(f"Đang đọc với giọng: {voice}")
    speak_japanese(text, voice)
