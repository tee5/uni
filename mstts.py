#!/usr/bin/env python
# coding: utf-8

import os
import requests
import time
import ssml

class TextToSpeech(object):
    def __init__(self, subscription_key):
        self.subscription_key = subscription_key
        self.access_token = None

    def get_token(self):
        """
        TTS APIのアクセストークンを取得する。
        未取得の場合に暗黙的に呼ばれるため、通常は明示的に呼び出す必要はない。
        """
        fetch_token_url = "https://japaneast.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = { "Ocp-Apim-Subscription-Key": self.subscription_key }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self, text, voice_font):
        """
        Parameters
        ----------
        text : str
            読み上げ対象のテキスト本文
        Returns
        -------
        wav_filename : str
            生成したオーディオファイルのファイル名
        """

        if self.access_token is None:
            self.get_token()
        base_url = "https://japaneast.tts.speech.microsoft.com/"
        path = "cognitiveservices/v1"
        constructed_url = base_url + path
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
            "User-Agent": "TTS"
        }
        body = ssml.make_ssml(text, voice_font)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        wav_filename = timestr + "-" + text + ".wav"

        # TODO: I/Oエラー処理いれる
        f = open(wav_filename.replace(".wav", ".xml"), "w", encoding="utf-8")
        f.write(body.decode("utf-8"))
        f.close()

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            with open(wav_filename, 'wb') as audio:
                audio.write(response.content)
            return wav_filename
        else:
            print(response.status_code, response.text)
            return ""

def main():
    # デバッグ用
    subscription_key = "xxx"
    ts = TextToSpeech(subscription_key)
    ts.save_audio("It's fine today.")

if __name__ == "__main__":
    main()

