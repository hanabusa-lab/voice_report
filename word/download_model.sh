#!/bin/bash
#
# モデルデータをダウンロードします。

wget http://public.shiroyagi.s3.amazonaws.com/latest-ja-word2vec-gensim-model.zip -o model/model.zip
pushd model
unzip model.zip
popd

