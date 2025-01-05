import cv2
import openai
import argparse

from pyaudio import PyAudio, paInt16
from speech_recognition import Microphone, Recognizer, UnknownValueError

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from constants import SYSTEM_PROMPT
from screenstream import ScreenStream
from webcamstream import WebcamStream

from dotenv import load_dotenv
load_dotenv()

class Assistant:
    def __init__(self, model):
        self.chain = self._create_inference_chain(model)

    def answer(self, prompt, image):
        if not prompt:
            return

        print("Prompt:", prompt)

        response = self.chain.invoke(
            {"prompt": prompt, "image_base64": image.decode() if image else None},
            config={"configurable": {"session_id": "unused"}},
        ).strip()

        print("Response:", response)

        if response:
            self._tts(response)

    def _tts(self, response):
        player = PyAudio().open(format=paInt16, channels=1, rate=24000, output=True)

        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            response_format="pcm",
            input=response,
        ) as stream:
            for chunk in stream.iter_bytes(chunk_size=1024):
                player.write(chunk)

    def _create_inference_chain(self, model):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "human",
                    [
                        {"type": "text", "text": "{prompt}"},
                        {
                            "type": "image_url",
                            "image_url": "data:image/jpeg;base64,{image_base64}",
                        },
                    ],
                ),
            ]
        )

        chain = prompt_template | model | StrOutputParser()

        chat_message_history = ChatMessageHistory()
        return RunnableWithMessageHistory(
            chain,
            lambda _: chat_message_history,
            input_messages_key="prompt",
            history_messages_key="chat_history",
        )


def audio_callback(recognizer, audio, stream):
    try:
        prompt = recognizer.recognize_whisper(audio, model="base", language="english")
        assistant.answer(prompt, stream.read(encode=True))

    except UnknownValueError:
        print("There was an error processing the audio.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assistant with Webcam or ScreenStream")
    parser.add_argument(
        "--stream_type", choices=["webcam", "screen"], default="screen",
        help="Choose the type of stream: 'webcam' or 'screen' (default: screen)."
    )

    args = parser.parse_args()

    if args.stream_type == "webcam":
        stream = WebcamStream().start()
    else:
        stream = ScreenStream().start()

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
    # model = ChatOpenAI(model="gpt-4o")
    assistant = Assistant(model)

    recognizer = Recognizer()
    microphone = Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    stop_listening = recognizer.listen_in_background(microphone, lambda r, a: audio_callback(r, a, stream))

    while True:
        frame = stream.read()
        if frame is not None:
            cv2.imshow("Stream", frame)
        if cv2.waitKey(1) in [27, ord("q")]:
            break

    stream.stop()
    cv2.destroyAllWindows()
    stop_listening(wait_for_stop=False)
