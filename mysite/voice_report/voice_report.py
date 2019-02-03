# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

import time,audioop, math, sys, argparse
from gcloud.credentials import get_credentials
from google.cloud.speech.v1beta1 import cloud_speech_pb2
from google.rpc import code_pb2
from grpc.beta import implementations
import numpy as np
import wave

import threading

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

#音声のファイル保存の有無フラグ
SAVE_VOICE_FG = False

class stdout:
    BOLD = "\033[1m"
    END = "\033[0m"
    CLEAR = "\033[2K"

def bold(string):
    return stdout.BOLD + string + stdout.END

def printr(string):
    sys.stdout.write("\r" + stdout.CLEAR)
    sys.stdout.write(string)
    sys.stdout.flush()

class Result:
    def __init__(self):
        self.transcription = ""
        self.confidence = ""
        self.is_final = False

class VoiceConsumer(AsyncWebsocketConsumer):

    """
    WebSocket通信のハンドラ(非同期実装)
    """
    async def connect(self):
        #初期値(コンストラクタに設定したら、エラーになるため、ここに記載している。)
        self.frames = []
        self.silent_frames = []
        self.connectfg = True
        self.should_finish_stream = False
        self.recognition_result = False
        self.voice = []

        self.silent_decibel = 40 #40
        self.host = "speech.googleapis.com"
        self.ssl_port = 443
        self.deadline_seconds = 60*3+5
        self.audio_encoding = "LINEAR16"
        #self.sampling_rate = 16000
        self.sampling_rate = 48000
        self.lang_code = "ja-JP"
        self.frame_seconds = 0.1 #1frameに含まれているデータの時間(クライアントは4*1024にしていて、サンプリング時間が48000だから、0.1[s]にしている)
        self.speech_scope = "https://www.googleapis.com/auth/cloud-platform"
        self.max_silent_cnt = 4

        self.recognition_result = Result()

        print("connected")

        await self.accept()
        print("accepted")

        ##音声スレッドの開始
        self.listen_thread = threading.Thread(target=self.voice_thread)
        self.listen_thread.start();

    async def disconnect(self, close_code):
        print("disconnected")
        self.connectfg = False
        self.should_finish_stream = True

        #音声ファイルの書き出し(デバック用)
        if SAVE_VOICE_FG :
            PATH = 'output.wav'
            dat= np.array(self.voice)
            #write sound data
            SAMPLE_SIZE = 2
            SAMPLE_RATE = 48000

            with wave.open(PATH, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(SAMPLE_SIZE)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(dat.tobytes('C'))

        self.voice.clear()
        print("closed")

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        #text_data_json = json.loads(text_data)
        #message = text_data_json['message']
        assert isinstance(bytes_data, bytes)
        voice_data = np.frombuffer(bytes_data, dtype='float32')

        v = np.array(voice_data)
        v.flatten()
        # バイナリに16ビットの整数に変換して保存
        arr = (v * 32767).astype(np.int16)

        #voiceは録音用。npとして保存。
        if SAVE_VOICE_FG :
            self.voice.append(np.frombuffer(arr, dtype='int16'))

        #framesは音声解析用。bytesのリスト構造。リストの一つの要素には、int16型の複数データをbytesに変換したものを格納する。
        self.frames.append(arr.tobytes('C'));

    def make_channel(self, host, port):
        ssl_channel = implementations.ssl_channel_credentials(None, None, None)
        creds = get_credentials().create_scoped(self.speech_scope)
        auth_header = ("authorization", "Bearer " + creds.get_access_token().access_token)
        auth_plugin = implementations.metadata_call_credentials(lambda _, func: func([auth_header], None), name="google_creds")
        composite_channel = implementations.composite_channel_credentials(ssl_channel, auth_plugin)
        return implementations.secure_channel(host, port, composite_channel)

    def request_stream(self):
        recognition_config = cloud_speech_pb2.RecognitionConfig(
        encoding=self.audio_encoding,
        sample_rate=self.sampling_rate,
        language_code=self.lang_code,
        max_alternatives=1,
        )
        streaming_config = cloud_speech_pb2.StreamingRecognitionConfig(
            config=recognition_config,
            interim_results=True,
            single_utterance=True)

        yield cloud_speech_pb2.StreamingRecognizeRequest(streaming_config=streaming_config)

        silent_cnt=0
        while True:
            #print(sys._getframe().f_code.co_name,"1")
            time.sleep(self.frame_seconds / 4)
            #print("self.should_finish_stream", self.should_finish_stream, "len", len(frames))

            if self.should_finish_stream:
                return

            if len(self.frames) > 0:
                #音量チェック　連続して無音区間が続いたら処理を抜ける。

                data = self.frames[0]
                rms = audioop.rms(data, 2)
                decibel = 20 * math.log10(rms) if rms > 0 else 0

                if decibel < self.silent_decibel:
                    silent_cnt = silent_cnt+1
                else :
                    silent_cnt = 0

                if silent_cnt > self.max_silent_cnt :
                    print(sys._getframe().f_code.co_name, "find silent frames return")
                    return

            #print("request_stream2 3 framen len=", len(self.frames))
            if len(self.frames) > 0:
                #print(sys._getframe().f_code.co_name,"2", "framelen=",len(self.frames))
                #self.frames.pop(0)
                yield cloud_speech_pb2.StreamingRecognizeRequest(audio_content=self.frames.pop(0))

    def listen_loop(self, recognize_stream):
        #print("recognize_stream", recognize_stream)
        for resp in recognize_stream:
            #print("resp", resp)

            if resp.error.code != code_pb2.OK:
                raise RuntimeError(resp.error.message)

            for result in resp.results:
                #print("resut", result)
                for alt in result.alternatives:
                    self.recognition_result.transcription = alt.transcript
                    self.recognition_result.confidence = alt.confidence
                    self.recognition_result.stability = result.stability
                    printr(" ".join((alt.transcript, "    ", "stability: ", str(int(result.stability * 100)), "%")))

                if result.is_final:
                    self.recognition_result.is_final = True
                    #print("resut=final")

                    #このshould_finish_streamは、シーケンス制御で使わないうようにしたい。
                    #self.should_finish_stream = True
                    return

    def run_recognition_loop(self):
        print("===start recognition")
        #if len(self.silent_frames) > 4:
        #    self.silent_frames = self.silent_frames[-4:]

        #変換を依頼している時には、
        #while not self.is_recording:
        while not self.should_finish_stream :

            #print(sys._getframe().f_code.co_name)
            time.sleep(self.frame_seconds // 4)

            if len(self.frames) == 0 :
                continue

            #音が入ってくるまで、解析処理を行わないようにする。
            data = self.frames[0]
            rms = audioop.rms(data, 2)
            decibel = 20 * math.log10(rms) if rms > 0 else 0
            #print("decibel", decibel)

            #音が入ってくるまで、処理を行わない。
            if decibel < self.silent_decibel:
                #print("pre frame len",len(self.frames))
                if len(self.frames) > 0 :
                    self.frames.pop(0)
                continue

            print(sys._getframe().f_code.co_name, "get sound. decibel=",decibel)
            self.is_recording = True
            self.frames = self.silent_frames + self.frames

            with cloud_speech_pb2.beta_create_Speech_stub(self.make_channel(self.host, self.ssl_port)) as service:
                try:
                    self.listen_loop(service.StreamingRecognize(self.request_stream(), self.deadline_seconds))

                    #処理結果が終了した時だけ出力するようにした
                    if self.recognition_result.is_final :
                        printr(" ".join((bold(self.recognition_result.transcription), "    ", "confidence: ", str(int(self.recognition_result.confidence * 100)), "%")))
                        self.recognition_result.is_final = False

                    #with open('result.txt', 'w') as f:
                    #    f.write(recognition_result.transcription)
                except Exception as e:
                    print(str(e))

    def voice_thread(self):
        #return
        while True:
            if not self.connectfg :
                print("disconnected")
                return

            self.is_recording = False
            self.should_finish_stream = False
            print(sys._getframe().f_code.co_name)
            self.run_recognition_loop()
