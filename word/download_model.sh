#!/bin/bash
#
# モデルデータをダウンロードします。

DST_DIR=word_to_similarity/model
mkdir -p $DST_DIR
wget http://public.shiroyagi.s3.amazonaws.com/latest-ja-word2vec-gensim-model.zip -O $DST_DIR/model.zip
pushd $DST_DIR
unzip model.zip
popd

