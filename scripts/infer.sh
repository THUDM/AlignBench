# stage1 generate answers of target APIs
MODEL=do_nothing # TODO

python get_answers.py \
    --model $MODEL \
    --workers 2 \
    --question-file data/data_release.jsonl \
    --save-dir data/model_answer