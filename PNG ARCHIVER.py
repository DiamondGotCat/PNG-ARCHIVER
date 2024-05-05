import wave
import json
from PIL import Image

# エンコードモード
def encode(image_path, wav_path):
    # 1. カラー + アルファ PNG画像を行で分ける
    image = Image.open(image_path)
    width, height = image.size
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel = image.getpixel((x, y))
            row.append(pixel)
        rows.append(row)
    
    # 2. { "1-row": [0,0.25,1,0.75,0.5], "2-row": [] ... } のような辞書に変換
    encoded_dict = {}
    for i, row in enumerate(rows):
        key = f"{i+1}-row"
        encoded_dict[key] = [pixel for pixel in row]
    
    # 3. 1000ヘルツの音のwavに変換
    with wave.open(wav_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(1000)
        for row in rows:
            for pixel in row:
                # バイト型に変換して書き込む
                wav_file.writeframesraw(bytes(pixel))

    return encoded_dict

# デコードモード
def decode(wav_path, encoded_dict, output_image_path):
    # 1. wavを辞書に戻す
    decoded_rows = []
    with wave.open(wav_path, 'r') as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
        for i in range(0, len(frames), 2):
            pixel = int.from_bytes(frames[i:i+2], byteorder='little')
            decoded_rows.append(pixel)
    
    # 2. カラー + アルファ PNG画像に戻す
    height = len(encoded_dict)
    width = len(encoded_dict["1-row"])
    decoded_image = Image.new('RGBA', (width, height))
    for i, key in enumerate(encoded_dict.keys()):
        row = encoded_dict[key]
        for j, pixel in enumerate(row):
            # タプルまたは整数で色を指定する
            decoded_image.putpixel((j, i), tuple(pixel))
    
    decoded_image.save(output_image_path)

# 使用例
if __name__ == "__main__":

    mode = input("mode[encode|decode]: ")

    if mode == "encode":
        # エンコード
        encoded_dict = encode(input("path of png: "), "output_sound.prc")
        with open("encoded_dict.json", "w") as json_file:
            json.dump(encoded_dict, json_file)

    if mode == "decode":

        # デコード
        with open(input("path of json: "), "r") as json_file:
            encoded_dict = json.load(json_file)
        decode("output_sound.prc", encoded_dict, "decoded_image.png")
