from flask import Flask, render_template, request
import stanza
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag

nltk.download('punkt')
# Flask アプリケーションの設定
app = Flask(__name__)
stanza.download("en")
nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')


def analyze_and_mask(text, pos_to_mask):
    """英文を解析し、指定された品詞をマスクします。"""
    doc = nlp(text)
    masked_sentence = []
    answer_key = {}  # 穴抜きの番号と単語の対応を格納する辞書
    counter = 1

    # 短縮形のリスト（'nt'を含むものも含む）
    contractions = [
        "can't", "won't", "wouldn't", "shouldn't", "mustn't", "couldn't",
        "didn't", "isn't", "aren't", "wasn't", "weren't", "haven't",
        "hasn't", "hadn't", "won't", "it's", "that's", "they're",
        "you're", "we're", "I'll", "he'll", "she'll", "you'll", "they'll",
        "n't"  # 'nt'を含む短縮形
    ]

    for sentence in doc.sentences:
        for word in sentence.words:
            # 助動詞または短縮形をマスク
            if word.upos in pos_to_mask or word.text in contractions:
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
            dependencies.append({
                'text': word.text,
                'dep': word.deprel,
                'head': sentence.words[word.head-1].text if word.head > 0 else None
            })
    return dependencies


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_text = request.form.get("input_text", "")
        pos_to_mask = request.form.getlist("pos_checkbox")  # チェックされた品詞を取得

        if input_text and pos_to_mask:
            # Stanza の品詞タグを使用する
            pos_to_mask_stanza = {
                'ADJ': 'ADJ',        # 形容詞
                'ADP': 'ADP',        # 前置詞
                'ADV': 'ADV',        # 副詞
                'AUX': 'AUX',        # 助動詞
                'CCONJ': 'CCONJ',    # 等位接続詞
                'DET': 'DET',        # 限定詞
                'NOUN': 'NOUN',      # 名詞
                'NUM': 'NUM',        # 数詞
                'PRON': 'PRON',      # 代名詞
                'PROPN': 'PROPN',    # 固有名詞
                'VERB': 'VERB',      # 動詞
                'PUNCT': 'PUNCT',    # 句読点
                'SCONJ': 'SCONJ',    # 接続詞
                'SYM': 'SYM',        # 記号
                'verb, base form': 'VB',  # 動詞基本形(原型)
                'verb, 3rd person singular present': 'VBZ'  # be動詞(三人称単数現在)
            }

            # マスキング対象品詞を Stanza タグと一致
            pos_to_mask = [
                tag for tag in pos_to_mask if tag in pos_to_mask_stanza.keys()]

            # マスキング処理
            masked_sentence, answer_key = analyze_and_mask(
                input_text, pos_to_mask)

            # NLTK 処理
            nltk_tags = analyze_with_nltk(input_text)

            # 依存関係解析
            dependencies = analyze_dependencies(input_text)

            return render_template(
                "index.html",
                input_text=input_text,
                masked_sentence=masked_sentence,
                answer_key=answer_key,  # 辞書をテンプレートに渡す
                nltk_tags=nltk_tags,
                dependencies=dependencies
            )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # ポート5001(仮)
