#!/usr/bin/env python3
import wave
import pygame
from pygame.locals import *
import scipy.fftpack as spfft
import soundfile as sf
import pyaudio
import sys
import numpy as np

#import matplotlib.pyplot as plt


# --------------------------------------------------------------------
# パラメータ(グローバル変数)
# --------------------
# 計算用
CHUNK = 1024  # pyaudioでストリームにチャンク単位で出力(何故1024かはよく知らない)
start = 0  # サンプリング開始位置
N = 1024  # FFTのサンプル数
SHIFT = 1024  # 窓関数をずらすサンプル数
hammingWindow = np.hamming(N)  # 窓関数

# --------------------
# 描画用
fn = "sample.wav"  # 対象のwavファイル（ご自分でご用意ください）
SCREEN_SIZE = (854, 480)  # ディスプレイのサイズ
rectangle_list = []

# --------------------
# pygame画面初期設定
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Pygame Audio Visualizer")

# 背景画像の指定
bg = pygame.image.load("bede.png").convert_alpha()
rect_bg = bg.get_rect()
sw = pygame.image.load("main_sword-logo01.png").convert_alpha()
rect_sw = sw.get_rect()
rect_sw.center = (400, 150)
sh = pygame.image.load("main_shield-logo01.png").convert_alpha()
rect_sh = sh.get_rect()
rect_sh.center = (700, 150)
# 背景画像の指定ここまで

# --------------------------------------------------------------------
# wavファイルの情報を表示する関数


def wav_file_info(filename):
    try:
        wf = wave.open(filename, "r")
    except FileNotFoundError:  # ファイルが存在しなかった場合
        print("[Error 404] No such file or directory: " + filename)
        return 0

    # wavファイルの情報を取得
    # チャネル数：monoなら1，stereoなら2，5.1chなら6(?)
    nchannels = wf.getnchannels()

    # 音声データ1サンプルあたりのバイト数．2なら2bytes(16bit), 3なら24bitなど
    samplewidth = wf.getsampwidth()

    # サンプリング周波数．普通のCDなら44.1k
    framerate = wf.getframerate()

    # 音声のデータ点の数
    nframes = wf.getnframes()

    print("Channel num : ", nchannels)
    print("Sample width : ", samplewidth)
    print("Sampling rate : ", framerate)
    print("Frame num : ", nframes)

    wf.close()

    return nframes  # フレーム数をFFTをシフトするときの終了条件に使いたいので

# --------------------------------------------------------------------
# wavファイルを再生する関数


def play_wav_file(filename):
    try:
        wf = wave.open(filename, "r")
    except FileNotFoundError:  # ファイルが存在しなかった場合
        print("[Error 404] No such file or directory: " + filename)
        return 0

    # ストリームを開く
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # 音声を再生
    data = wf.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)
        redraw()
    stream.close()
    p.terminate()

# --------------------------------------------------------------------
# 「FFTかけて描画」を繰り返す．


def redraw():
    global start
    global screen
    global rectangle_list

    # --------------------
    # 対象サンプル点のブロックにFFTをかけて振幅スペクトルを計算する
    windowedData = hammingWindow * x[start:start + N]  # 窓関数をかけたデータブロック
    X = spfft.fft(windowedData)  # FFT
    amplitudeSpectrum = [np.sqrt(c.real ** 2 + c.imag ** 2)
                         for c in X]  # 振幅スペクトル

    # --------------------
    # Pygameでの描画

    screen.fill((240, 128, 128))  # 黒で初期化する
    screen.blit(bg, rect_bg)  # 背景画像の描画
    screen.blit(sw, rect_sw)  # ロゴとか表示してみたり
    screen.blit(sh, rect_sh)
    rectangle_list.clear()  # 四角形リスト初期化
    # スペクトル描画 数値は実行して調整しながら
    for i in range(86):
        rectangle_list.append(pygame.draw.line(screen, (102, 205, 170), (1+i * 10, 350 + amplitudeSpectrum[i] * 1),
                                               (1+i * 10, 350 - amplitudeSpectrum[i] * 1), 4))

    pygame.display.update(rectangle_list)  # ディスプレイ更新

    start += SHIFT  # 窓関数をかける範囲をずらす
    if start + N > nframes:
        sys.exit()

    for event in pygame.event.get():  # 終了処理
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()


# --------------------------------------------------------------------
if __name__ == "__main__":

    # --------------------
    # wavの波形分析
    data, fs = sf.read(fn)  # 今回ステレオなのでチャネル2つ(LとR)ある
    x = data[:, 0]  # この音源LR両方一緒なのでLだけに注目して処理することに(Rなら0->1)　足し算とかでも良さそう

    # --------------------
    # wav情報
    nframes = wav_file_info(fn)  # フレーム数取得　ついでに他の情報も表示
    #t = np.arange(0, nframes, 1)
    # print(t)

    #plt.plot(t, x)
    # plt.show()

    # --------------------
    # 再生と描画を開始
    play_wav_file(fn)


# "bede.wav"----------------------------------------------------------
# Channel num :  2
# Sample width :  2
# Sampling rate :  44100
# Frame num :  12844923
# --------------------------------------------------------------------
