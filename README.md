# voice_report
* 概要：ブラウザから入力された音声をテキスト変換するプログラム
* 使い方：
  - 1: クライアントの環境においてGCPの認証を済ませる。そして、認証情報が記載された場所(例えば、~/.config)をdocker-compose.ymlの以下の場所に反映する。
    ~~~
    volumes:  
      - ~/.config:/root/.config
    ~~~
  - 2: 以下のコマンドで、docker環境を構築する。
      ~~~
      docker-compose up  --force-recreate --build
      ~~~
  - 3: ブラウザから以下のサイトにアクセスする。
      http://localhost:3000/voice_report/ 
  - 4: 画面上の"connect"ボタンを押して話すと、音声解析されたテキストの内容が、手順2で利用したターミナルに表示されます。
      
* 注意：
 - 本プログラムは、有料のGoogle Speech To Textを利用しています。本プログラムを動作させる際には、自身のGCPの設定が施されたフォルダ(config)を指定する必要があります。
 - ブラウザからマイク音源を取得するためには、ブラウザがChrome、また、サーバがhttpsである必要があります。httpのサーバにアクセスする場合には、以下のようなオプションでブラウザを起動してください。
  ~~~
  open -a “/Applications/Google Chrome.app” --args --unsafely-treat-insecure-origin-as-secure=“http://localhost”
  ~~~ 
