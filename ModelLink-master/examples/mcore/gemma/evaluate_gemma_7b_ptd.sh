#!/bin/bash
export CUDA_DEVICE_MAX_CONNECTIONS=1

# distributed config
MASTER_ADDR=localhost
MASTER_PORT=6000
NNODES=1
NODE_RANK=0
NPUS_PER_NODE=8

# modify script model path and tokenizer path
TOKENIZER_PATH="your tokenizer directory path"
CHECKPOINT="your model directory path"

# configure task and data path
DATA_PATH="./mmlu/test/"
TASK="mmlu"

DISTRIBUTED_ARGS="--nproc_per_node $NPUS_PER_NODE --nnodes $NNODES --node_rank $NODE_RANK --master_addr $MASTER_ADDR --master_port $MASTER_PORT"

# configure generation parameters
torchrun $DISTRIBUTED_ARGS evaluation.py \
       --task-data-path ${DATA_PATH} \
       --task ${TASK} \
       --load ${CHECKPOINT} \
       --use-mcore-models \
       --tensor-model-parallel-size 8 \
       --pipeline-model-parallel-size 1 \
       --num-layers 28 \
       --hidden-size 3072 \
       --ffn-hidden-size 24576 \
       --num-attention-heads 16 \
       --kv-channels 256 \
       --max-position-embeddings 8192 \
       --seq-length 8192 \
       --max-new-tokens 1 \
       --geglu \
       --position-embedding-type rope \
       --disable-bias-linear \
       --normalization RMSNorm \
       --add-rmsnorm-offset \
       --input-embeds-norm \
       --tokenizer-type PretrainedFromHF \
       --tokenizer-name-or-path ${TOKENIZER_PATH} \
       --tokenizer-not-use-fast \
       --norm-epsilon 1e-06 \
       --evaluation-batch-size 1 \
       --micro-batch-size 1  \
       --use-fused-rmsnorm \
       --no-masked-softmax-fusion \
       --exit-on-missing-checkpoint \
       --no-load-rng \
       --no-load-optim \
       --vocab-size 256000 \
       --make-vocab-size-divisible-by 1 \
       --bf16 \
       --seed 42 | tee logs/evaluation_gemma_7b_mcore_${TASK}.log