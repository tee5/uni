#!/usr/bin/env python
# coding: utf-8

import time
from xml.etree import ElementTree

DEFAULT_VOICE_FONT = "Microsoft Server Speech Text to Speech Voice (ja-JP, Ayumi, Apollo)"
#DEFAULT_VOICE_FONT = "Microsoft Server Speech Text to Speech Voice (ja-JP, Ichiro, Apollo)"
#DEFAULT_VOICE_FONT = "Microsoft Server Speech Text to Speech Voice (ja-JP, HarukaRUS)"

def make_ssml(text, voice_font=DEFAULT_VOICE_FONT):
    """
    引数をもとにSSML(音声合成マークアップ言語)を生成し、文字列で返す

    Parameters
    ----------
    text: int
        音声合成で読み上げるテキスト本文

    Returns
    -------
    body : int
        XML文字列
    """
    xml_body = ElementTree.Element("speak", version="1.0")
    xml_body.set("{http://www.w3.org/XML/1998/namespace}lang", "JA-JP")
    voice = ElementTree.SubElement(xml_body, "voice")
    voice.set("{http://www.w3.org/XML/1998/namespace}lang", "JA-JP")
    voice.set("name", voice_font)
    voice.text = text
    body = ElementTree.tostring(xml_body)
    return body

def main():
    ssml = make_ssml("this is test message.")
    print(ssml)

if __name__ == "__main__":
    main()
