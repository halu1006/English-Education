from flask import Flask, render_template, request, jsonify
import stanza
import nltk
import whisper
import tempfile
import os
import re
import json  # json.loads() を使うためにインポート
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# nltk.download() は起動時に毎回実行する必要がない
nltk.download("punkt")

# Flask アプリケーションの設定
app = Flask(__name__)
# stanza.download() も起動時に毎回実行する必要がない
stanza.download("en")
nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse")

# nltk.download("all") は起動時に毎回実行する必要がない
nltk.download("all")

# whisper モデルの読み込み
model = whisper.load_model("large")


def analyze_and_mask(text, pos_to_mask):
    """英文を解析し、指定された品詞をマスクします。"""
    doc = nlp(text)
    masked_sentence = []
    answer_key = {}  # 穴抜きの番号と単語の対応を格納する辞書
    counter = 1

    for sentence in doc.sentences:
        for word in sentence.words:
            if word.upos in pos_to_mask:
                masked_sentence.append(f"({counter})")
                answer_key[counter] = word.text  # 辞書に番号と単語を登録
                counter += 1
            else:
                masked_sentence.append(word.text)

    return " ".join(masked_sentence), answer_key


def analyze_with_nltk(text):
    """NLTK を使用してトークン化と品詞タグ付けを行う。"""
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    return tagged


def analyze_dependencies(text):
    """依存関係解析を行う。"""
    doc = nlp(text)
    dependencies = []
    for sentence in doc.sentences:
        for word in sentence.words:
            dependencies.append(
                {
                    "text": word.text,
                    "dep": word.deprel,
                    "head": (
                        sentence.words[word.head - 1].text if word.head > 0 else None
                    ),
                }
            )
    return dependencies


@app.route("/", methods=["GET", "POST"])
def index():
    # 文全体の正誤判定の初期値を「判定中」にする
    is_correct = "判定中"
    masked_sentence = ""  # 初期化
    answer_key = {}  # 初期化
    nltk_tags = []  # 初期化
    dependencies = []  # 初期化

    if request.method == "POST":
        input_text = request.form.get("input_text", "")
        pos_to_mask = request.form.getlist("pos_checkbox")
        transcription_text = request.form.get("transcription_text", "")

        if input_text and pos_to_mask:
            # Stanza の品詞タグを使用する
            pos_to_mask_stanza = {
                "ADJ": "ADJ",  # 形容詞
                "ADP": "ADP",  # 前置詞
                "ADV": "ADV",  # 副詞
                "AUX": "AUX",  # 助動詞
                "CCONJ": "CCONJ",  # 等位接続詞
                "DET": "DET",  # 限定詞
                "NOUN": "NOUN",  # 名詞
                "NUM": "NUM",  # 数詞
                "PRON": "PRON",  # 代名詞
                "PROPN": "PROPN",  # 固有名詞
                "VERB": "VERB",  # 動詞
                "PUNCT": "PUNCT",  # 句読点
                "SCONJ": "SCONJ",  # 接続詞
                "SYM": "SYM",  # 記号
            }

            # マスキング対象品詞を Stanza タグと一致
            pos_to_mask = [
                tag for tag in pos_to_mask if tag in pos_to_mask_stanza.keys()
            ]

            # マスキング処理
            masked_sentence, answer_key = analyze_and_mask(input_text, pos_to_mask)

            # NLTK 処理
            nltk_tags = analyze_with_nltk(input_text)

            # 依存関係解析
            dependencies = analyze_dependencies(input_text)

            # 文全体の正誤判定 (音声認識結果がある場合のみ)
            if transcription_text:
                is_correct = input_text.strip() == transcription_text.strip()

        return render_template(
            "index.html",
            input_text=input_text,
            masked_sentence=masked_sentence,
            answer_key=answer_key,
            nltk_tags=nltk_tags,
            dependencies=dependencies,
            transcription_text=transcription_text,  # 認識結果を渡す
            is_correct=is_correct,  # 正誤判定結果を渡す
        )

    return render_template("index.html", is_correct=is_correct)  # 初期値を渡す


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        audio_file.save(temp_audio.name)
        audio_path = temp_audio.name

    try:
        result = model.transcribe(audio_path, language="en")
        # 音声認識処理が成功した場合のみファイルを削除
        os.remove(audio_path)
        return jsonify({"text": result["text"]})
    except Exception as e:
        # エラーが発生した場合でもファイルを削除
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return jsonify({"error": str(e)}), 500


@app.route("/judge", methods=["POST"])
def judge():
    transcription_text = request.form.get("transcription_text", "")
    answer_key_json = request.form.get(
        "answer_key", "{}"
    )  # answer_key がない場合は空の辞書を設定
    answer_key = json.loads(answer_key_json)
    input_text = request.form.get("input_text", "")
    pos_to_mask = request.form.getlist("pos_checkbox")

    # ここに正誤判定のロジックを追加

    is_correct = input_text.strip() == transcription_text.strip()

    return jsonify({"is_correct": is_correct})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
