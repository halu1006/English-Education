# 英語学習支援ツール

## 概要

このプロジェクトは、英語学習を支援するツール群を提供します。

## 機能

- **英文解析:** 入力された英文を形態素解析し、単語の品詞や依存関係を表示します。
- **発音チェック:** 入力された英文を読み上げ、正しい発音と比較できます。
- **文誤り検出:** 入力された英文の文法的な誤りを検出し、修正候補を提案します。

## インストール

1. このリポジトリをクローンします。

   ```bash
   git clone git@github.com:shimomaes/English-Project.git
   ```

2. プロジェクトディレクトリに移動します。

   ```bash
   cd English-Project
   ```

3. 仮想環境を作成し、有効化します。

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. 必要な依存関係をインストールします。

   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. アプリケーションを起動します。

   ```bash
   flask run
   ```

2. Web ブラウザで `http://127.0.0.1:5000/` にアクセスします。
