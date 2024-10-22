# coding=utf-8
# Copyright (c) 2024, HUAWEI CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
from functools import wraps
import torch
from ..patchs.patch_utils import PatchManager

_ARGS = None


def get_modellink_args():
    """
    Get arguments of model-link and patch according to args.
    """
    from modellink.training.arguments import process_args

    global _ARGS
    if _ARGS is None:
        parser = argparse.ArgumentParser(description='ModelLink Arguments', allow_abbrev=False)
        _ARGS, _ = process_args(parser).parse_known_args()
    return _ARGS


def exec_adaptation():
    basic_adaptation()
    mcore_adaptation()
    legacy_adaptation()

    PatchManager.apply_patches()
    post_patch_application()


def apex_adaptation():
    """
        Adaptation for apex.
        Would be replaced with mindspeed-core implementation when its relevant API is provided!
    """

    from mindspeed.optimizer.adamw import AdamW
    from mindspeed.core.fusions.fused_layer_norm import fused_layer_norm_affine

    def multi_tensor_l2norm(overflow_buf, tensor_lists, per_parameter):
        total_norm = 0.0
        norm_type = 2.0
        ret_per_tensor = [] if per_parameter else None
        for grads_for_norm in tensor_lists:
            for grad in grads_for_norm:
                grad_norm = torch.norm(grad, norm_type)
                total_norm += grad_norm ** norm_type
            if per_parameter:
                ret_per_tensor.append(total_norm.clone())
        if not tensor_lists:
            grad_norm = torch.cuda.FloatTensor([0])
            total_norm = grad_norm ** norm_type
        return total_norm ** (1 / norm_type), ret_per_tensor

    def multi_tensor_scale(overflow_buf, tensor_lists, scale):
        if len(tensor_lists) != 2:
            raise AssertionError('The size of tensor list must be 2, but got {}'.format(len(tensor_lists)))
        if len(tensor_lists[0]) != len(tensor_lists[1]):
            raise AssertionError('The size of tensor list must be same, but got {} and {}'.format(len(tensor_lists[0]),
                                                                                                  len(tensor_lists[1])))

        with torch.no_grad():
            for i in range(len(tensor_lists[0])):
                tensor_lists[1][i].copy_(tensor_lists[0][i] * scale)

    def multi_tensor_applier(op, noop_flag_buffer, tensor_lists, *args):
        return op(noop_flag_buffer, tensor_lists, *args)

    PatchManager.register_patch('apex.optimizers.FusedAdam', AdamW, create_dummy=True)
    PatchManager.register_patch('amp_C.multi_tensor_l2norm', multi_tensor_l2norm, create_dummy=True)
    PatchManager.register_patch('amp_C.multi_tensor_scale', multi_tensor_scale, create_dummy=True)
    PatchManager.register_patch('fused_layer_norm_cuda', create_dummy=True)
    PatchManager.register_patch('apex.multi_tensor_apply.multi_tensor_applier', multi_tensor_applier, create_dummy=True)
    PatchManager.register_patch('apex.normalization.fused_layer_norm.fused_layer_norm_affine', fused_layer_norm_affine,
                        create_dummy=True)


def te_adaptation():
    """
        Adaptation for transformer-engine.
        Would be replaced with mindspeed-core implementation when its relevant API is provided!
    """
    def version_wrapper(fn):
        @wraps(fn)
        def wrapper(name, *args, **kwargs):
            if name == 'transformer-engine':
                return '0.0'
            res = fn(name, *args, **kwargs)
            return res

        return wrapper

    PatchManager.register_patch('importlib.metadata.version', version_wrapper)
    PatchManager.register_patch('transformer_engine.pytorch.LayerNormLinear', torch.nn.Module, create_dummy=True)
    PatchManager.register_patch('transformer_engine.pytorch.DotProductAttention', torch.nn.Module, create_dummy=True)
    PatchManager.register_patch('transformer_engine.pytorch.Linear', torch.nn.Module, create_dummy=True)
    PatchManager.register_patch('flash_attn.flash_attn_interface.flash_attn_unpadded_func', create_dummy=True)


def torch_adaptation():
    """
        Would be replaced with mindspeed-core implementation when its relevant API is provided!
    """
    from torch.distributed import all_gather_into_tensor, reduce_scatter_tensor

    def type_wrapper(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            res = fn(*args, **kwargs)
            if isinstance(res, str):
                res = res.replace('npu', 'cuda')
            return res

        return wrapper

    def ensure_contiguous_wrapper(fn):
        """
        Patch view method to ensure tensor is contiguous before performing view.
        """
        def wrapper(tensor, *args, **kwargs):
            if not tensor.is_contiguous():
                tensor = tensor.contiguous()
            return fn(tensor, *args, **kwargs)

        return wrapper

    def repeat_interleave(inputs, repeats, dim):
        shape = inputs.shape
        new_shape = shape[:dim + 1] + (repeats,) + shape[dim + 1:]
        out_shape = shape[:dim] + (shape[dim] * repeats,) + shape[dim + 1:]
        return inputs.unsqueeze(dim + 1).expand(new_shape).reshape(out_shape)

    PatchManager.register_patch('torch.nn.parameter.Parameter.type', type_wrapper)
    PatchManager.register_patch('torch.Tensor.type', type_wrapper)
    PatchManager.register_patch('torch.Tensor.view', ensure_contiguous_wrapper)
    PatchManager.register_patch('torch.distributed._all_gather_base', all_gather_into_tensor)
    PatchManager.register_patch('torch.distributed._reduce_scatter_base', reduce_scatter_tensor)

    torch.Tensor.repeat_interleave = repeat_interleave  # replace npu implementation of torch.repeat_interleave
    torch.compile = torch.jit.script


def post_patch_application():
    """
    Adaptations that should execute after patch manager.
    """

    from ..core import build_layers_wrapper
    from megatron.core.tensor_parallel import ColumnParallelLinear, RowParallelLinear
    from megatron.core.transformer.transformer_block import TransformerBlock
    # For MOE + Ascend MC2, here we can only execute this after _transformer_block_build_layers takes effect.
    TransformerBlock._build_layers = build_layers_wrapper(TransformerBlock._build_layers,
                                                          ColumnParallelLinear.forward,
                                                          RowParallelLinear.forward)


def basic_adaptation():
    """
        Fundamental and necessary adaptation to support LLM Task running in NPU.
    """
    te_adaptation()
    apex_adaptation()
    torch_adaptation()

    # transformer_engine modules should be replaced before importing megatron
    PatchManager.apply_patches()


def mcore_adaptation():
    # 获取参数，提供core models入参
    patch_fusions()
    patch_core_models()
    patch_core_transformers()
    patch_pipeline_parallel()
    patch_tensor_parallel()
    patch_parallel_state()
    patch_datasets()
    patch_utils()


def legacy_adaptation():
    patch_miscellaneous()
    patch_model()
    patch_initialize()
    patch_training()
    patch_log_handler()
    patch_high_availability_feature()
    patch_optimizer()


def patch_fusions():
    from mindspeed.core.fusions.fused_layer_norm import (FusedLayerNormAffineFunction, FastLayerNormFN)
    from mindspeed.core.fusions.fused_softmax import (is_kernel_available, ScaledUpperTriangMaskedSoftmax,
                                                      ScaledMaskedSoftmax, ScaledSoftmax, forward_fused_softmax)
    from mindspeed.core.fusions.fused_bias_swiglu import SwiGLUFunction, BiasSwiGLUFunction

    # use torch-npu fused layer norm
    PatchManager.register_patch('megatron.core.fusions.fused_layer_norm.FusedLayerNormAffineFunction', FusedLayerNormAffineFunction)
    # use torch-npu fused layer norm
    PatchManager.register_patch('megatron.core.fusions.fused_layer_norm.FastLayerNormFN', FastLayerNormFN)
    # use torch-npu npu_scaled_masked_softmax
    PatchManager.register_patch('megatron.core.fusions.fused_softmax.ScaledUpperTriangMaskedSoftmax', ScaledUpperTriangMaskedSoftmax)
    PatchManager.register_patch('megatron.core.fusions.fused_softmax.ScaledMaskedSoftmax', ScaledMaskedSoftmax)  # use torch-npu npu_scaled_masked_softmax
    PatchManager.register_patch('megatron.core.fusions.fused_softmax.ScaledSoftmax', ScaledSoftmax)  # use torch-npu npu_scaled_masked_softmax
    PatchManager.register_patch('megatron.core.fusions.fused_softmax.FusedScaleMaskSoftmax.is_kernel_available', is_kernel_available)  # replace kernel check
    PatchManager.register_patch('megatron.core.fusions.fused_softmax.FusedScaleMaskSoftmax.forward_fused_softmax', forward_fused_softmax)
    PatchManager.register_patch('megatron.core.fusions.fused_bias_swiglu.SwiGLUFunction', SwiGLUFunction)
    PatchManager.register_patch('megatron.core.fusions.fused_bias_swiglu.BiasSwiGLUFunction', BiasSwiGLUFunction)


def patch_core_models():
    from megatron.core.models.gpt.gpt_layer_specs import get_gpt_layer_local_spec
    from mindspeed.core.models.common.embeddings.rotary_pos_embedding import get_pos_emb_on_this_cp_rank
    from ..training.utils import get_batch_on_this_cp_rank, get_batch_on_this_tp_rank, get_device_wrapper
    from ..core import rotary_embedding_forward, apply_rotary_pos_emb_bshd
    from ..core.models.gpt.gpt_layer_specs import get_gpt_layer_local_spec_wrapper
    from ..core.transformer.dot_product_attention import dot_product_attention_init_wrapper, \
        dot_product_attention_forward_wrapper, ulysses_context_parallel_forward_wrapper
    from ..core.transformer.attention import attention_init_wrapper
    from ..core.models.gpt.gpt_model import gpt_model_init_wrapper
    from ..core import rotary_embedding_init_wrapper, gpt_model_forward

    # Embedding
    PatchManager.register_patch('megatron.core.models.common.embeddings.rotary_pos_embedding.get_pos_emb_on_this_cp_rank', get_pos_emb_on_this_cp_rank)
    # rotary support for Megatron-LM core 0.6.0
    PatchManager.register_patch('megatron.core.models.common.embeddings.rotary_pos_embedding.apply_rotary_pos_emb_bshd', apply_rotary_pos_emb_bshd)
    PatchManager.register_patch('megatron.core.models.common.embeddings.rotary_pos_embedding.RotaryEmbedding.forward', rotary_embedding_forward)
    PatchManager.register_patch('megatron.core.models.common.embeddings.rotary_pos_embedding.RotaryEmbedding.__init__', rotary_embedding_init_wrapper)

    # Attention
    PatchManager.register_patch('megatron.core.transformer.attention.Attention.__init__', attention_init_wrapper)
    PatchManager.register_patch('megatron.core.transformer.dot_product_attention.DotProductAttention.__init__', dot_product_attention_init_wrapper)
    PatchManager.register_patch('megatron.core.transformer.dot_product_attention.DotProductAttention.forward', dot_product_attention_forward_wrapper)
    PatchManager.register_patch('megatron.core.transformer.custom_layers.transformer_engine.TEDotProductAttention.__init__', dot_product_attention_init_wrapper)
    PatchManager.register_patch('megatron.core.transformer.custom_layers.transformer_engine.TEDotProductAttention.forward', dot_product_attention_forward_wrapper)
    # For GQA in ulysses and hybrid
    PatchManager.register_patch('mindspeed.core.context_parallel.ulysses_context_parallel.UlyssesContextAttention.forward', ulysses_context_parallel_forward_wrapper)

    # Layer Definition
    # For NPU, we use local-mcore-structrue in te layer.
    PatchManager.register_patch('megatron.core.models.gpt.gpt_layer_specs.get_gpt_layer_with_transformer_engine_spec', get_gpt_layer_local_spec)
    PatchManager.register_patch('megatron.core.models.gpt.gpt_layer_specs.get_gpt_layer_local_spec', get_gpt_layer_local_spec_wrapper)

    PatchManager.register_patch('megatron.training.utils.get_batch_on_this_cp_rank', get_batch_on_this_cp_rank)
    PatchManager.register_patch('megatron.training.utils.get_batch_on_this_tp_rank', get_batch_on_this_tp_rank)
    PatchManager.register_patch('megatron.training.dist_signal_handler.get_device', get_device_wrapper)
    PatchManager.register_patch('megatron.core.models.gpt.gpt_model.GPTModel.forward', gpt_model_forward)
    PatchManager.register_patch('megatron.core.models.gpt.gpt_model.GPTModel.__init__', gpt_model_init_wrapper)

    # For recomputation
    from ..core.transformer.transformer_block import transformer_block_checkpointed_forward_wrapper
    PatchManager.register_patch('megatron.core.transformer.transformer_block.TransformerBlock._checkpointed_forward', transformer_block_checkpointed_forward_wrapper)


def patch_core_transformers():
    from mindspeed.core.transformer.moe.router import aux_loss_load_balancing
    from mindspeed.core.transformer.moe.token_dispatcher import allgather_token_permutation, \
        allgather_token_unpermutation
    from mindspeed.core.transformer.moe.grouped_gemm_util import Ops, grouped_gemm_is_available, get_device_capability
    from mindspeed.core.transformer.transformer import core_mlp_forward_wrapper

    from ..core.transformer.moe.moe_layer import moe_layer_init_wrapper, moe_layer_forward
    from ..core.transformer.transformer_block import _transformer_block_build_layers
    from ..core.transformer.transformer_layer import transformer_layer_init_wrapper
    from ..core import (PTNorm, topk_router_forward, topk_router_routing, z_loss_func,
                        TransformerLayerSubmodules,
                        transformer_layer_forward, get_num_layers_to_build_wrapper,
                        transformer_block_init_wrapper, transformer_block_forward, core_mlp_init)
    PatchManager.register_patch('torch.cuda.get_device_capability', get_device_capability)
    PatchManager.register_patch('megatron.core.transformer.transformer_block.TENorm', PTNorm)
    PatchManager.register_patch('megatron.core.transformer.moe.router.TopKRouter.routing', topk_router_routing)
    PatchManager.register_patch('megatron.core.transformer.moe.router.TopKRouter.forward', topk_router_forward)
    PatchManager.register_patch('megatron.core.transformer.transformer_layer.TransformerLayerSubmodules', TransformerLayerSubmodules)
    PatchManager.register_patch('megatron.core.transformer.transformer_layer.TransformerLayer.__init__', transformer_layer_init_wrapper)
    PatchManager.register_patch('megatron.core.transformer.transformer_layer.TransformerLayer.forward', transformer_layer_forward)
    PatchManager.register_patch('megatron.core.transformer.moe.router.z_loss_func', z_loss_func)
    PatchManager.register_patch('megatron.core.transformer.transformer_block.get_num_layers_to_build',
                                get_num_layers_to_build_wrapper)
    PatchManager.register_patch('megatron.core.transformer.moe.grouped_gemm_util.ops', Ops)
    PatchManager.register_patch('megatron.core.transformer.moe.grouped_gemm_util.grouped_gemm_is_available',
                                grouped_gemm_is_available)

    # Transformer block
    PatchManager.register_patch('megatron.core.transformer.transformer_block.TransformerBlock.__init__',
                                transformer_block_init_wrapper)
    PatchManager.register_patch('megatron.core.transformer.transformer_block.TransformerBlock.forward',
                                transformer_block_forward)
    PatchManager.register_patch('megatron.core.transformer.transformer_block.TransformerBlock._build_layers',
                                _transformer_block_build_layers)
    PatchManager.register_patch('megatron.core.transformer.mlp.MLP.__init__', core_mlp_init)
    PatchManager.register_patch('megatron.core.transformer.mlp.MLP.forward', core_mlp_forward_wrapper)

    # For mcore moe
    PatchManager.register_patch('megatron.core.transformer.moe.moe_layer.MoELayer.__init__', moe_layer_init_wrapper)
    PatchManager.register_patch('megatron.core.transformer.moe.moe_layer.MoELayer.forward', moe_layer_forward)

    args = get_modellink_args()
    if args.moe_permutation_async_comm and args.moe_token_dispatcher_type == 'allgather':
        PatchManager.register_patch('megatron.core.transformer.moe.token_dispatcher.MoEAllGatherTokenDispatcher.token_permutation', allgather_token_permutation)
        PatchManager.register_patch('megatron.core.transformer.moe.token_dispatcher.MoEAllGatherTokenDispatcher.token_unpermutation', allgather_token_unpermutation)
        PatchManager.register_patch('megatron.core.transformer.moe.router.TopKRouter.aux_loss_load_balancing', aux_loss_load_balancing)

    # For drop and pad feature in all2all dispatcher
    if args.moe_expert_capacity_factor:
        from ..core.transformer.moe.router import aux_loss_load_balancing, apply_load_balancing_loss
        from ..core.transformer.moe.moe_utils import topk_softmax_with_capacity
        # balancing strategy relies on moe_expert_capacity_factor
        PatchManager.register_patch('megatron.core.transformer.moe.router.TopKRouter.aux_loss_load_balancing', aux_loss_load_balancing)
        PatchManager.register_patch('megatron.core.transformer.moe.router.TopKRouter.apply_load_balancing_loss', apply_load_balancing_loss)
        PatchManager.register_patch('megatron.core.transformer.moe.moe_utils.topk_softmax_with_capacity', topk_softmax_with_capacity)

        if args.moe_token_dispatcher_type == 'alltoall':
            from ..core.transformer.moe.token_dispatcher import MoEAlltoAllTokenDispatcher
            PatchManager.register_patch('megatron.core.transformer.moe.token_dispatcher.MoEAlltoAllTokenDispatcher', MoEAlltoAllTokenDispatcher)

    # For groupMLP especially deepseek
    from mindspeed.core.transformer.moe.experts import groupedmlp_init_wrapper, groupedmlp_forward_wrapper
    PatchManager.register_patch('megatron.core.transformer.moe.experts.GroupedMLP.__init__', groupedmlp_init_wrapper)
    PatchManager.register_patch('megatron.core.transformer.moe.experts.GroupedMLP.forward', groupedmlp_forward_wrapper)


def patch_pipeline_parallel():
    from ..core.pipeline_parallel.p2p_communication import _batched_p2p_ops

    # solve send recv bug
    PatchManager.register_patch('megatron.core.pipeline_parallel.p2p_communication._batched_p2p_ops', _batched_p2p_ops)

    # dpo relative, we need to change the recv/send shape when using PP, then deal with it by ourselves.
    from modellink.tasks.rl.utils import get_tensor_shapes_decorator
    PatchManager.register_patch(
        'megatron.core.pipeline_parallel.schedules.get_tensor_shapes',
        get_tensor_shapes_decorator
    )


def patch_tensor_parallel():
    from mindspeed.core.tensor_parallel.layers import vocab_parallel_embedding_forward
    from mindspeed.core.tensor_parallel.random import _set_cuda_rng_state
    from mindspeed.core.tensor_parallel.cross_entropy import vocab_parallel_cross_entropy_forward
    from ..core import vocab_embedding_forward_wrapper, vocab_embedding_init_wrapper

    # default_generators need replace after set_device
    PatchManager.register_patch('megatron.core.tensor_parallel.random._set_cuda_rng_state', _set_cuda_rng_state)
    # change masked_target for better performance
    PatchManager.register_patch('megatron.core.tensor_parallel.cross_entropy._VocabParallelCrossEntropy.forward', vocab_parallel_cross_entropy_forward)
    PatchManager.register_patch('megatron.core.tensor_parallel.layers.VocabParallelEmbedding.forward', vocab_parallel_embedding_forward)
    PatchManager.register_patch('megatron.core.tensor_parallel.layers.VocabParallelEmbedding.forward', vocab_embedding_forward_wrapper)
    PatchManager.register_patch('megatron.core.tensor_parallel.layers.VocabParallelEmbedding.__init__', vocab_embedding_init_wrapper)


def patch_parallel_state():
    import megatron
    from mindspeed.core.parallel_state import (initialize_model_parallel, destroy_model_parallel_wrapper, \
                                               get_context_parallel_group_for_send_recv_overlap)
    from ..core import initialize_model_parallel_decorator
    from ..core import destroy_model_parallel_decorator
    from ..core.transformer.transformer_block import get_layer_offset_wrapper

    # Bugfix for Megatron-LM core 0.6.0, to be removed for next version.
    PatchManager.register_patch('megatron.core.parallel_state.initialize_model_parallel', initialize_model_parallel)
    PatchManager.register_patch('megatron.core.parallel_state.initialize_model_parallel', initialize_model_parallel_decorator)

    # For MoE
    PatchManager.register_patch('megatron.core.parallel_state.destroy_model_parallel', destroy_model_parallel_decorator)

    # For cp parallel state destroy
    PatchManager.register_patch('megatron.core.parallel_state.destroy_model_parallel', destroy_model_parallel_wrapper)
    PatchManager.register_patch('megatron.core.parallel_state.get_context_parallel_group_for_send_recv_overlap', get_context_parallel_group_for_send_recv_overlap)
    PatchManager.register_patch('megatron.core.mpu', megatron.core.parallel_state)
    PatchManager.register_patch('megatron.core.transformer.transformer_layer.TransformerLayer._get_layer_offset', get_layer_offset_wrapper)


def patch_model():
    from mindspeed.core.fusions.fused_layer_norm import (FusedLayerNormAffineFunction, FastLayerNormFN)
    from mindspeed.core.fusions.fused_softmax import (is_kernel_available, ScaledUpperTriangMaskedSoftmax,
                                                      ScaledMaskedSoftmax, ScaledSoftmax, forward_fused_softmax)
    from mindspeed.core.fusions.fused_layer_norm import fused_layer_norm_affine

    from ..legacy.model.transformer import parallel_transformer_layer_init_wrapper
    from ..legacy.model.transformer import parallel_mlp_forward_wrapper
    from ..legacy.model import (
        GPTModel, parallel_transformer_init, transformer_language_model_forward_wrapper,
        state_dict_for_save_checkpoint_wrapper,
        core_attention_wrapper, core_attention_forward, FlashSelfAttention,
        ParallelAttention_wrapper, ParallelAttentionForward,
        parallel_transformer_forward, parallel_mlp_init_wrapper,
        rms_norm_init_wrapper, rms_norm_forward, post_language_model_processing
    )
    from ..training.checkpointing import load_args_from_checkpoint_wrapper

    # patch_fused_layer_norm
    PatchManager.register_patch('megatron.legacy.model.fused_layer_norm.FusedLayerNormAffineFunction', FusedLayerNormAffineFunction)  # use torch-npu fused layer norm
    PatchManager.register_patch('megatron.legacy.model.fused_layer_norm.FastLayerNormFN', FastLayerNormFN)  # use torch-npu fused layer norm
    PatchManager.register_patch('megatron.legacy.model.fused_layer_norm.fused_layer_norm_affine', fused_layer_norm_affine)  # use torch-npu fused layer norm

    # patch_fused_softmax
    PatchManager.register_patch('megatron.legacy.model.fused_softmax.ScaledUpperTriangMaskedSoftmax', ScaledUpperTriangMaskedSoftmax)  # use torch-npu npu_scaled_masked_softmax
    PatchManager.register_patch('megatron.legacy.model.fused_softmax.ScaledMaskedSoftmax', ScaledMaskedSoftmax)  # use torch-npu npu_scaled_masked_softmax
    PatchManager.register_patch('megatron.legacy.model.fused_softmax.ScaledSoftmax', ScaledSoftmax)  # use torch-npu npu_scaled_masked_softmax
    PatchManager.register_patch('megatron.legacy.model.fused_softmax.FusedScaleMaskSoftmax.is_kernel_available', is_kernel_available)  # replace kernel check
    PatchManager.register_patch('megatron.legacy.model.fused_softmax.FusedScaleMaskSoftmax.forward_fused_softmax', forward_fused_softmax)

    # patch_rms_norm
    PatchManager.register_patch('megatron.legacy.model.rms_norm.RMSNorm.__init__', rms_norm_init_wrapper)
    PatchManager.register_patch('megatron.legacy.model.rms_norm.RMSNorm.forward', rms_norm_forward)

    # patch_transformer
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelMLP.__init__', parallel_mlp_init_wrapper)
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelMLP.forward', parallel_mlp_forward_wrapper)
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelTransformerLayer.__init__', parallel_transformer_layer_init_wrapper)
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelTransformer.__init__', parallel_transformer_init)
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelTransformer.forward', parallel_transformer_forward)
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelTransformer.state_dict_for_save_checkpoint',
                                state_dict_for_save_checkpoint_wrapper)
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelAttention.__init__', ParallelAttention_wrapper)
    PatchManager.register_patch('megatron.legacy.model.transformer.ParallelAttention.forward', ParallelAttentionForward)
    PatchManager.register_patch('megatron.legacy.model.transformer.CoreAttention.__init__', core_attention_wrapper)
    PatchManager.register_patch('megatron.legacy.model.transformer.CoreAttention.forward', core_attention_forward)
    PatchManager.register_patch('megatron.legacy.model.transformer.FlashSelfAttention', FlashSelfAttention)

    # patch gptmodel
    PatchManager.register_patch('megatron.legacy.model.GPTModel', GPTModel)
    PatchManager.register_patch('megatron.legacy.model.gpt_model.post_language_model_processing', post_language_model_processing)
    # patch language model
    PatchManager.register_patch('megatron.legacy.model.language_model.TransformerLanguageModel.forward', transformer_language_model_forward_wrapper)
    PatchManager.register_patch('megatron.training.checkpointing.load_args_from_checkpoint', load_args_from_checkpoint_wrapper)


def patch_initialize():
    from mindspeed.initialize import _compile_dependencies
    from ..training.initialize import initialize_megatron

    PatchManager.register_patch('megatron.training.initialize._compile_dependencies', _compile_dependencies)  # remove cuda kernel compile
    PatchManager.register_patch('megatron.training.initialize.initialize_megatron', initialize_megatron)


def patch_training():
    from ..training import get_model_wrapper, train
    from ..training.checkpointing import load_checkpoint_wrapper
    from ..legacy.data import build_pretraining_data_loader

    PatchManager.register_patch('megatron.training.training.get_model', get_model_wrapper)
    PatchManager.register_patch('megatron.training.training.build_pretraining_data_loader', build_pretraining_data_loader)
    PatchManager.register_patch('megatron.training.training.train', train)
    PatchManager.register_patch('megatron.training.training.load_checkpoint', load_checkpoint_wrapper)


def patch_miscellaneous():
    from modellink.training.utils import print_args_wrapper
    from modellink.training.arguments import validate_args_decorator
    from modellink.training.arguments import core_transformer_config_from_args_wrapper
    from ..training.checkpointing import _load_base_checkpoint_wrapper
    from ..training.tokenizer import build_tokenizer
    from ..training.arguments import parse_args_decorator

    PatchManager.register_patch('megatron.training.arguments.parse_args', parse_args_decorator)
    PatchManager.register_patch('megatron.training.arguments.validate_args', validate_args_decorator)
    # After validating arguments, do arguments printing.
    PatchManager.register_patch('megatron.training.arguments._print_args', print_args_wrapper)
    PatchManager.register_patch('megatron.training.global_vars.build_tokenizer', build_tokenizer)
    PatchManager.register_patch('megatron.training.checkpointing._load_base_checkpoint', _load_base_checkpoint_wrapper)

    # For transformer layer configuration
    PatchManager.register_patch('megatron.training.arguments.core_transformer_config_from_args', core_transformer_config_from_args_wrapper)


def patch_datasets():
    from megatron.core.datasets.blended_megatron_dataset_builder import BlendedMegatronDatasetBuilder
    from megatron.core.datasets.gpt_dataset import GPTDataset
    from ..core import (build_generic_dataset, _build_document_sample_shuffle_indices,
                        indexed_dataset_builder_init_wrapper, add_item_wrapper, finalize_wrapper)

    # change attributions
    GPTDataset._build_document_sample_shuffle_indices = _build_document_sample_shuffle_indices
    BlendedMegatronDatasetBuilder.build_generic_dataset = build_generic_dataset
    PatchManager.register_patch('megatron.core.datasets.indexed_dataset.IndexedDatasetBuilder.__init__', indexed_dataset_builder_init_wrapper)
    PatchManager.register_patch('megatron.core.datasets.indexed_dataset.IndexedDatasetBuilder.add_item', add_item_wrapper)
    PatchManager.register_patch('megatron.core.datasets.indexed_dataset.IndexedDatasetBuilder.finalize', finalize_wrapper)


def patch_log_handler():
    from megatron.training.log_handler import CustomHandler
    from modellink.training.utils import emit
    CustomHandler.emit = emit


def patch_utils():
    from modellink.training.utils import unwrap_model_wrapper
    PatchManager.register_patch('megatron.training.checkpointing.unwrap_model', unwrap_model_wrapper)
    PatchManager.register_patch('megatron.training.training.unwrap_model', unwrap_model_wrapper)


def patch_high_availability_feature():
    from ..training import setup_model_and_optimizer_wrapper
    from ..core import (get_megatron_optimizer_wrapper, clip_grad_norm_fp32_wrapper, distributed_optimizer_init_wrapper,
                        start_grad_sync_wrapper, distributed_data_parallel_init_wrapper)

    PatchManager.register_patch('megatron.core.distributed.distributed_data_parallel.DistributedDataParallel.__init__', distributed_data_parallel_init_wrapper)
    PatchManager.register_patch('megatron.core.distributed.param_and_grad_buffer.Bucket.start_grad_sync', start_grad_sync_wrapper)
    PatchManager.register_patch('megatron.training.training.get_megatron_optimizer', get_megatron_optimizer_wrapper)
    PatchManager.register_patch('megatron.core.optimizer.optimizer.clip_grad_norm_fp32', clip_grad_norm_fp32_wrapper)
    PatchManager.register_patch('megatron.core.optimizer.distrib_optimizer.DistributedOptimizer.__init__', distributed_optimizer_init_wrapper)
    PatchManager.register_patch('megatron.training.training.setup_model_and_optimizer', setup_model_and_optimizer_wrapper)


def patch_optimizer():
    args = get_modellink_args()
    if args.reuse_fp32_param:
        from mindspeed.optimizer.optimizer import mixed_precision_optimizer_step, reuse_fp32_param_init_wrapper, \
            optimizer_config_init_wrapper
        from mindspeed.optimizer.distrib_optimizer import reuse_fp32_param_distrib_optimizer_init_wrapper
        PatchManager.register_patch('megatron.core.optimizer.optimizer.MixedPrecisionOptimizer.step', mixed_precision_optimizer_step)
        PatchManager.register_patch('megatron.core.optimizer.optimizer.Float16OptimizerWithFloat16Params.__init__', reuse_fp32_param_init_wrapper)
        PatchManager.register_patch('megatron.core.optimizer.optimizer_config.OptimizerConfig.__init__', optimizer_config_init_wrapper)
        PatchManager.register_patch('megatron.core.optimizer.distrib_optimizer.DistributedOptimizer.__init__', reuse_fp32_param_distrib_optimizer_init_wrapper)

    if args.swap_attention:
        from mindspeed.core.memory.adaptive_recomputing.adaptive_recompute import allowed_recomputing_module_wrapper
        from mindspeed.core.memory.adaptive_recomputing.adaptive_recompute import setup_model_and_optimizer_wrapper
        from megatron.legacy.model.transformer import ParallelTransformerLayer
        from megatron.core.transformer.transformer_layer import TransformerLayer
        if hasattr(args, "use_mcore_models") and args.use_mcore_models:
            allowed_recomputing_module_wrapper(TransformerLayer)
        else:
            allowed_recomputing_module_wrapper(ParallelTransformerLayer)
        PatchManager.register_patch('megatron.training.training.setup_model_and_optimizer', setup_model_and_optimizer_wrapper)
