volume=30
crossings=40
python train.phrases.py \
    --phrase='background' \
    --json-file=background.json \
    --length=3 \
    --find-noise-level \
    --max-bg-start-volume=$volume \
    --max-bg-start-crossings=$crossings
