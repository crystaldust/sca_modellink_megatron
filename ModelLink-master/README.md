  <p align="center"> <img src="sources/images/logo.png" height="103px" width="700px"> </p>

<p align="center">
    <a href="https://gitee.com/ascend/MindSpeed/blob/master/LICENSE">
    <a href="https://gitee.com/ascend/MindSpeed/blob/master/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/huggingface/transformers.svg?color=blue">
    </a>
    <a href="https://gitee.com/ascend/MindSpeed">
        <img alt="Documentation" src="https://img.shields.io/website/http/huggingface.co/docs/transformers/index.svg?down_color=red&down_message=offline&up_message=online">
    </a>
    <a>
        <img src="https://app.codacy.com/project/badge/Grade/1710faac5e634acaabfc26b0a778cdde">
    </a>
</p>

ModelLink旨在为华为 [昇腾芯片](https://www.hiascend.com/) 上提供端到端的大语言模型方案, 包含模型，算法，以及下游任务。

---

## ModelLink大模型方案概览


当前ModelLink支撑大模型使用功能:
* 权重转换：[Huggingface与Megatron-LM权重转换](#huggingface与megatron-lm权重转换) 【昇腾】【OCK】【GTS】
* 数据集处理：[预训练数据集/指令微调数据集](./examples/README.md#数据集准备及处理) 【NAIE】【昇腾】
* 分布式预训练：[加速算法/融合算子/并行策略](#预训练加速算法与融合算子)【昇腾】【计算算法部】【计算研究部】
* 分布式指令微调：[Prompt模板/动态padding/多轮对话](#分布式指令微调)【NAIE】【昇腾】
* 分布式推理：[流式推理/人机对话](./examples/README.md#大模型分布式推理) 【NAIE】【昇腾】【GTS】
* 分布式评估：[MMLU/CEVAL/HumanEval/BBH/BoolQ/AGIEval](./examples/README.md#大模型分布式评估)【NAIE】
* 昇腾工具链：[Profiling采集](#基于昇腾芯片采集profiling数据)/[确定性计算](#基于昇腾芯片的确定性计算功能)/[高可用](#基于昇腾芯片的高可用特性)【昇腾】【计算研究部】

LoRA、DPO、奖励模型、PPO等特性即将上线

---


## ModelLink版本维护策略

ModelLink版本有以下五个维护阶段：

| **状态**            | **时间** | **说明**                                                               |
| ------------------- | -------- |----------------------------------------------------------------------|
| 计划                | 1—3 个月 | 计划特性                                                                 |
| 开发                | 3 个月   | 开发特性                                                                 |
| 维护                | 6-12 个月| 合入所有已解决的问题并发布版本，针对不同的ModelLink版本采取不同的维护策略，常规版本和长期支持版本维护周期分别为6个月和12个月 |
| 无维护              | 0—3 个月 | 合入所有已解决的问题，无专职维护人员，无版本发布                                             |
| 生命周期终止（EOL） | N/A      | 分支不再接受任何修改                                                           |


ModelLink已发布版本维护策略：

| **ModelLink版本** | **维护策略** | **当前状态** | **发布时间**   | **后续状态**         | **EOL日期** |
|-----------------|-----------|--------|------------|-----------------------|-----------|
| bk_origin_23    |  Demo     | EOL    | 2023       | 生命周期终止           | 2024/6/30 |
| 1.0.RC1         |  常规版本  | 维护   | 2024/03/30 | 预计2024/9/30起无维护  |           |
| 1.0.RC2         |  常规版本  | 维护   | 2024/06/30 | 预计2024/12/30起无维护 |           |
| 1.0.RC3         |  常规版本  | 维护   | 2024/09/30 | 预计2025/03/30起无维护 |           |

---

## 配套版本与支持模型

【版本配套环境】

|           软件            | [版本](https://www.hiascend.com/zh/) |
| :-----------------------: |:----------------------------------:|
|          Python           |                3.8                 |
|          Driver           |         在研版本          |
|         Firmware          |         在研版本          |
|           CANN            |             在研版本             |
|           Torch           |            2.1.0、2.2.0             |
|         Torch_npu         |           在研版本           |

【预训练集群性能与线性度】

ModelLink 通过模型并行与数据并行来训练大语言模型，为了演示如何使用多个昇腾芯片和模型大小进行扩展性训练，我们使用 `GPT3-175B` 稠密大模型，从128颗 NPU 扩展到 7968颗 NPU 进行实验，下图是实验数据：
<p align="center"> <img src="sources/images/linearity&mfu.png" height="485px" width="710px"> </p>
报告的吞吐量是针对端到端训练进行测量的，涵盖所有操作，包括数据加载、优化器步骤、通信，甚至日志记录。请注意，示例大模型没有训练至收敛。

图中呈现了对应集群规模下的 `MFU` 值与集群整体的 `线性度`情况. 计算公式已经放到社区，点击链接可进行参考：[MFU计算公式](https://gitee.com/ascend/ModelLink/wikis/%E6%9C%AF%E8%AF%AD%E5%AE%9A%E4%B9%89/%E5%A4%A7%E6%A8%A1%E5%9E%8B%20MFU%20%E8%AE%A1%E7%AE%97%E5%85%AC%E5%BC%8F)，[线性度计算公式](https://gitee.com/ascend/ModelLink/wikis/%E6%9C%AF%E8%AF%AD%E5%AE%9A%E4%B9%89/%E7%BA%BF%E6%80%A7%E5%BA%A6%E5%85%AC%E5%BC%8F)

下述列表中支持的模型，我们在[examples/README.md](./examples/README.md)中提供了相应的使用说明，里面有详细的模型训练、推理、评估流程

`参数`列中的超链接指向模型的预训练文件下载地址，`模型`列中的超链接指向更多的社区资源地址，包括Chat/Instruct权重等

`性能`的单位是tokens/p/s即每张卡每秒处理的token数【现版本实测性能（硬件信息：Atlas 900 A2 PODc）】

`性能2`的单位是tokens/p/s即每张卡每秒处理的token数【现版本实测性能（硬件信息：内部在研）】

`认证`【Pass】表示经过昇腾官方版本测试的模型，【Test】表示待测试模型

表中为开启 mc2 特性【内部在研特性】后预训练实测性能，该特性只在24RC2以上版本支持，本仓库代码层面默认关闭，若要使用，请参考[加速算法与融合算子](#jump2)章节

<table>
  <thead>
    <tr>
      <th>模型</th>
      <th>参数</th>
      <th>序列</th>
      <th>实现</th>
      <th>集群</th>
      <th>性能</th>
      <th>性能2</th>
      <th>参考</th>
      <th>贡献方</th>
      <th>认证</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="1"><a href="https://huggingface.co/collections/BAAI/aquila-6698657124de09d10cd7a83f">Aquila</a></td>
      <td><a href="https://huggingface.co/BAAI/Aquila-7B/tree/main">7B</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td> 1x8</td>
      <td> 2849 </td>
      <td> -- </td>
      <td> 2874 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/collections/BAAI/aquila-6698657124de09d10cd7a83f">Aquila2</a></td>
      <td><a href="https://huggingface.co/BAAI/Aquila2-7B/tree/main">7B</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td> 1x8</td>
      <td> 3323 </td>
      <td> -- </td>
      <td> 2673 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/BAAI/Aquila2-34B/tree/main">34B</a></td>
      <td>4K</td>
      <th>Legacy</th>
      <td> 2x8</td>
      <td> 854 </td>
      <td> -- </td>
      <td> 732 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/baichuan-inc">Baichuan</a></td>
      <td><a href="https://huggingface.co/baichuan-inc/Baichuan-7B/tree/main">7B</a></td>
      <td>4K</td>
      <th>Legacy</th>
      <td> 1x8</td>
      <td> 2685 </td>
      <td> -- </td>
      <td> 2036 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/baichuan-inc/Baichuan-13B-Base/tree/main">13B</a></td>
      <td>4K</td>
      <th>Legacy</th>
      <td> 1x8</td>
      <td> 1213 </td>
      <td> -- </td>
      <td> 862 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/baichuan-inc">Baichuan2</a></td>
      <td><a href="https://huggingface.co/baichuan-inc/Baichuan2-7B-Base/tree/main">7B</a></td>
      <td>4K</td>
      <th>Legacy</th>
      <td> 1x8</td>
      <td> 2664 </td>
      <td> -- </td>
      <td> 3969 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/baichuan-inc/Baichuan2-13B-Base/tree/main">13B</a></td>
      <td>4K</td>
      <th>Mcore</th>
      <td> 1x8</td>
      <td> 1754 </td>
      <td> -- </td>
      <td> 2062 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/bigscience">Bloom</a></td>
      <td><a href="https://huggingface.co/bigscience/bloom-7b1/tree/main">7B1</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td> 1x8</td>
      <td> 2034 </td>
      <td> -- </td>
      <td> 2525 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/bigscience/bloom/tree/main">176B</td>
      <td>2K</td>
      <th>Legacy</th>
      <td >12x8</td>
      <td> 100 </td>
      <td> -- </td>
      <td> 107 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="3"><a href="https://huggingface.co/THUDM">ChatGLM3</a></td>
      <td rowspan="3"><a href="https://huggingface.co/THUDM/chatglm3-6b-base/tree/main">6B</a></td>
      <td>8K</td>
      <th>Mcore</th>
      <td >1x8</td>
      <td> 4611 </td>
      <td> -- </td>
      <td> 4543 </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td>32K</td>
      <th>Mcore</th>
      <td >1x8</td>
      <td> 2650 </td>
      <td> -- </td>
      <td> 2887 </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td>64K</td>
      <th>Mcore</th>
      <td >2x8</td>
      <td> 1724 </td>
      <td> -- </td>
      <td> 2097 </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/THUDM">GLM4</a></td>
      <td rowspan="2"><a href="https://huggingface.co/THUDM/glm-4-9b">9B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 2221 </td>
      <td> -- </td>
      <td> 2708 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td> 32K </td>
      <th>Mcore</th>
      <td> 2x8 </td>
      <td> 1482 </td>
      <td> -- </td>
      <td> 1752 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="1"><a href="https://huggingface.co/codellama">CodeLlama</a></td>
      <td><a href="https://huggingface.co/codellama/CodeLlama-34b-hf/tree/main">34B</a></td>
      <td>4K</td>
      <th>Mcore</th>
      <td> 2x8</td>
      <td> 902 </td>
      <td> -- </td>
      <td> 762 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/internlm">InternLM</a></td>
      <td><a href="https://huggingface.co/internlm/internlm-7b/tree/main">7B</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td>1x8</td>
      <td> 2776 </td>
      <td> -- </td>
      <td> 2854 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td >65B</td>
      <td>2K</td>
      <th>Legacy</th>
      <td >4x8</td>
      <td> 341 </td>
      <td> -- </td>
      <td> 414 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="2"> <a href="https://huggingface.co/internlm">InternLM2</a> </td>
      <td rowspan="2"> <a href="https://huggingface.co/Internlm/Internlm2-chat-20b/tree/main">20B</a> </td>
      <td> 4K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 1141 </td>
      <td> -- </td>
      <td> 1348 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> 32K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 4982 </td>
      <td> -- </td>
      <td> 5476 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="4"><a href="https://huggingface.co/meta-llama">LLaMA</td>
      <td><a href="https://huggingface.co/ruibin-wang/llama-7b-hf/tree/main">7B</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td>1x8</td>
      <td> 3600 </td>
      <td> -- </td>
      <td> 3804 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/ruibin-wang/llama-13b-hf">13B</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td>1x8</td>
      <td> 1895 </td>
      <td> -- </td>
      <td> 2012 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/pinkmanlove/llama-33b-hf/tree/main">33B</a></td>
        <td>2K</td>
        <th>Legacy</th>
        <td>4x8</td>
        <td>621</td>
        <td> -- </td>
        <td>776</td>
        <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/pinkmanlove/llama-65b-hf">65B</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td>4x8</td>
      <td> 348 </td>
      <td> -- </td>
      <td> 426 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="4"><a href="https://huggingface.co/meta-llama">LLaMA2</td>
      <td><a href="https://huggingface.co/daryl149/llama-2-7b-hf/tree/main">7B</a></td>
      <td>4K</td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 4733 </td>
      <td> -- </td>
      <td> 3850 </td>
      <td>【NAIE】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/NousResearch/Llama-2-13b-hf/tree/main">13B</a></td>
      <td>4K</td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 2209 </td>
      <td> -- </td>
      <td> 1920 </td>
      <td>【NAIE】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/codellama/CodeLlama-34b-Instruct-hf/tree/main">34B</a></td>
      <td>4K</td>
      <th>Mcore</th>
      <td>2x8</td>
      <td> 810 </td>
      <td> -- </td>
      <td> 796 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/meta-llama/Llama-2-70b-hf">70B</a></td>
      <td>4K</td>
      <th>Mcore</th>
      <td>4x8</td>
      <td> 441 </td>
      <td> -- </td>
      <td> 430 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/meta-llama">LLaMA3</td>
      <td><a href="https://huggingface.co/unsloth/llama-3-8b/tree/main">8B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 2400 </td>
      <td> -- </td>
      <td> 2674 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/v2ray/Llama-3-70B/tree/main">70B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>8x8</td>
      <td> 353 </td>
      <td> -- </td>
      <td> 355 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="3"><a href="https://modelscope.cn/organization/LLM-Research">LLaMA3.1</td>
      <td rowspan="2"><a href="https://modelscope.cn/models/LLM-Research/Meta-Llama-3.1-8B">8B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 2280 </td>
      <td> -- </td>
      <td> 2520 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td>128K</td>
      <th>Mcore</th>
      <td>4x8</td>
      <td> 1297 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td><a href="https://modelscope.cn/models/LLM-Research/Meta-Llama-3.1-70B">70B</a></td>
      <td>8K</td>
      <th>Mcore</th>
      <td>4x8</td>
      <td> 399 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://modelscope.cn/organization/LLM-Research">LLaMA3.2</a></td>
      <td rowspan="1"><a href="https://modelscope.cn/models/LLM-Research/Llama-3.2-1B">1B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 15408 </td>
      <td> -- </td>
      <td> 18941 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="1"><a href="https://modelscope.cn/models/LLM-Research/Llama-3.2-3B">3B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 6290 </td>
      <td> -- </td>
      <td> 6386 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="3"><a href="https://huggingface.co/Qwen">Qwen</a></td>
      <td><a href="https://huggingface.co/Qwen/Qwen-7B/tree/main">7B</a></td>
      <td> 8K </td>
      <th>Legacy</th>
      <td>1x8</td>
      <td> 2499 </td>
      <td> -- </td>
      <td> 2867 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/Qwen/Qwen-14B/tree/main">14B</a></td>
      <td>2K</td>
      <th>Legacy</th>
      <td>1x8</td>
      <td> 1560 </td>
      <td> -- </td>
      <td> 1578 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/Qwen/Qwen-72B/tree/main">72B</a></td>
      <td> 8K </td>
      <th>Legacy</th>
      <td>16x8</td>
      <td> 285 </td>
      <td> -- </td>
      <td> 345 </td>
      <td>【GTS】</td>
      <td>【Pass】</td>
    </tr>
    </tr>
       <tr>
      <td rowspan="8"><a href="https://huggingface.co/Qwen">Qwen1.5</a></td>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-0.5B/tree/main">0.5B</a> </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 23239 </td>
      <td> -- </td>
      <td> 25306 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-1.8B/tree/main">1.8B</a> </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 12603 </td>
      <td> -- </td>
      <td> 12181 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-4B/tree/main">4B</a> </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 5221 </td>
      <td> -- </td>
      <td> 5328 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-7B/tree/main">7B</a> </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 2951 </td>
      <td> -- </td>
      <td> 2621 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-14B/tree/main">14B</a> </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 1760 </td>
      <td> -- </td>
      <td> 1702 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-32B/tree/main">32B</a> </td>
      <td> 8K </td>
      <th> Mcore </th>
      <td> 4x8 </td>
      <td> 768 </td>
      <td> -- </td>
      <td> 708 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-72B/tree/main">72B</a> </td>
      <td> 8K </td>
      <th> Mcore </th>
      <td> 8x8 </td>
      <td> 339 </td>
      <td> -- </td>
      <td> 317 </td>
      <td>【GTS】</td>    
      <td>【Test】</td>
      <tr>
      <td> <a href="https://huggingface.co/Qwen/Qwen1.5-110B/tree/main">110B</a> </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 8x8 </td>
      <td> 223 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【GTS】</td>    
      <td>【Test】</td>
    </tr>
    </tr>
      <td rowspan="1"><a href="https://huggingface.co/Qwen">CodeQwen1.5</a></td>
      <td> <a href="https://huggingface.co/Qwen/CodeQwen1.5-7B">7B</a> </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 3146 </td>
      <td> -- </td>
      <td> 3866 </td>
      <td>【GTS】</td>    
      <td>【Test】</td>
    </tr>
    </tr>
       <tr>
       <td rowspan="8"><a href="https://huggingface.co/Qwen">Qwen2</a></td>
      <td rowspan="2"> <a href="https://huggingface.co/Qwen/Qwen2-0.5B/tree/main">0.5B</a> </td>
      <td> 4K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 28618 </td>
      <td> -- </td>
      <td> 34859 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> 32K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 11338 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td rowspan="2"> <a href="https://huggingface.co/Qwen/Qwen2-1.5B/tree/main">1.5B</a> </td>
      <td> 4K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 15456 </td>
      <td> -- </td>
      <td> 15603 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> 32K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 7281 </td>
      <td> -- </td>
      <td> 8538 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td rowspan="2"><a href="https://huggingface.co/Qwen/Qwen2-7B/tree/main">7B</a></td>
      <td> 4K</td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 4034 </td>
      <td> -- </td>
      <td>4241 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td> 32K</td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 2040 </td>
      <td> -- </td>
      <td>2045 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td><a href="https://huggingface.co/Qwen/Qwen2-57B-A14B/tree/main">57B-A14B</a></td>
      <td> 4K</td>
      <th>Mcore</th>
      <td>8x8</td>
      <td> 416 </td>
      <td> -- </td>
      <td>-- </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td><a href="https://huggingface.co/Qwen/Qwen2-72B/tree/main">72B</a></td>
      <td> 4K</td>
      <th>Mcore</th>
      <td>4x8</td>
      <td> 368 </td>
      <td> -- </td>
      <td>-- </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="4"><a href="https://huggingface.co/Qwen/Qwen2.5-7B">Qwen2.5</a></td>
      <td> <a href="https://huggingface.co/Qwen/Qwen2.5-3B/tree/main">3B</a> </td>
      <td> 32K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 3704 </td>
      <td> -- </td>
      <td> 4045 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
      <tr>
      <td><a href="https://huggingface.co/Qwen/Qwen2.5-7B/tree/main">7B</a></td>
      <td> 32K</td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 2177 </td>
      <td> -- </td>
      <td> 2501 </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
      <tr>
      <td><a href="https://huggingface.co/Qwen/Qwen2.5-14B/tree/main">14B</a></td>
      <td> 32K </td>
      <th> Mcore </th>
      <td> 2x8 </td>
      <td> 1061 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
      <td><a href="https://huggingface.co/Qwen/Qwen2.5-32B/tree/main">32B</a></td>
      <td> 32K </td>
      <th> Mcore </th>
      <td> 4x8 </td>
      <td> 407 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="1"><a href="https://huggingface.co/01-ai">Yi</a></td>
      <td><a href="https://huggingface.co/01-ai/Yi-34B/tree/main">34B</a></td>
      <td> 4K</td>
      <th>Mcore</th>
      <td>2x8</td>
      <td> 855 </td>
      <td> -- </td>
      <td> 730 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="3"><a href="https://huggingface.co/mistralai">Mixtral</a></td>
      <td><a href="https://huggingface.co/mistralai/Mixtral-8x7B-v0.1/tree/main">8x7B</a></td>
      <td> 32K</td>
      <th>Mcore</th>
      <td>8x8</td>
      <td> 706 </td>
      <td> -- </td>
      <td> 837 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/mistralai/Mixtral-8x22B-v0.1/tree/main">8x22B</a></td>
      <td> 32K</td>
      <th>Mcore</th>
      <td>8x8</td>
      <td> 239 </td>
      <td> 254 </td>
      <td> -- </td>
      <td>【NAIE】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td> 64K</td>
      <th>Mcore</th>
      <td>8x8</td>
      <td> -- </td>
      <td> 215 </td>
      <td> -- </td>
      <td>【NAIE】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="1"><a href="https://huggingface.co/mistralai">Mistral</a></td>
      <td><a href="https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2/tree/main">7B</a></td>
      <td> 32K</td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 2900 </td>
      <td> -- </td>
      <td> 2734 </td>
      <td>【NAIE】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/google">Gemma</a></td>
      <td><a href="https://huggingface.co/google/gemma-2b/tree/main">2B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 7067 </td>
      <td> -- </td>
      <td> 7602 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/google/gemma-7b">7B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 2939 </td>
      <td> -- </td>
      <td> 2607 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://huggingface.co/google">Gemma2</a></td>
      <td><a href="https://huggingface.co/google/gemma-2-9b/tree/main">9B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>1x8</td>
      <td> 1713 </td>
      <td> -- </td>
      <td> 1595 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td><a href="https://huggingface.co/google/gemma-2-27b/tree/main">27B</a></td>
      <td> 8K </td>
      <th>Mcore</th>
      <td>2x8</td>
      <td> 827 </td>
      <td> -- </td>
      <td> 800 </td>
      <td>【GTS】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2">GPT3</td>
      <td>175B</td>
      <td> 2K </td>
      <th>Legacy</th>
      <td> 16x8 </td>
      <td> 153 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td>15B</td>
      <td> 2K </td>
      <th>Legacy</th>
      <td> 1x8 </td>
      <td> 1890 </td>
      <td> -- </td>
      <td> 1840 </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2">GPT4</td>
      <td> 4x13B </td>
      <td> 128K </td>
      <th> Mcore </th>
      <td> 8x8 </td>
      <td> 424 </td>
      <td> 1066 </td>
      <td> -- </td>
      <td>【NAIE】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td> 4x16B </td>
      <td> 128K </td>
      <th>Mcore</th>
      <td> 8x8 </td>
      <td> 351 </td>
      <td> 918 </td>
      <td> -- </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="1"><a href="https://github.com/xai-org/grok-1">Grok1</a></td>
      <td>8x5B</td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 4x8 </td>
      <td> 1082 </td>
      <td> -- </td>
      <td> 993 </td>
      <td>【昇腾】</td>
      <td>【Pass】</td>
    </tr>
    <tr>
      <td rowspan="1"><a href="https://huggingface.co/deepseek-ai/DeepSeek-V2">DeepSeek-V2</a></td>
      <td> 60B </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 4x8 </td>
      <td> 1083 </td>
      <td> -- </td>
      <td> 1343 </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="1"><a href="https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite">DeepSeek-V2-Lite</a></td>
      <td> 16B </td>
      <td> 8K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 2830 </td>
      <td> -- </td>
      <td> -- </td>
      <td>【昇腾】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td rowspan="2"><a href="https://github.com/OpenBMB/MiniCPM">MiniCPM</a></td>
      <td> <a href="https://huggingface.co/openbmb/MiniCPM-2B-sft-bf16/tree/main">2B</a> </td>
      <td> 4K </td>
      <th> Mcore </th>
      <td> 1x8 </td>
      <td> 7314 </td>
      <td> -- </td>
      <td> 7953 </td>
      <td>【NAIE】</td>
      <td>【Test】</td>
    </tr>
    <tr>
      <td> <a href="https://huggingface.co/openbmb/MiniCPM-MoE-8x2B/tree/main">8x2B</a> </td>
      <td> 4K </td>
      <th>Mcore</th>
      <td> 1x8 </td>
      <td> 2981 </td>
      <td> -- </td>
      <td> 3172 </td>
      <td>【NAIE】</td>
      <td>【Test】</td>
    </tr>
  </tbody>
</table>

---

## <span id="jump1"> Huggingface与Megatron-LM权重转换

ModelLink支持Huggingface、Megatron-Legacy以及Megatron-Core之间的权重格式互转，具体功能列表如下：


<table>
  <thead>
    <tr>
      <th>源格式</th>
      <th>目标格式</th>
      <th>支持特性</th>
      <th>特性入参</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="12">HuggingFace </td>
      <td rowspan="4">Megatron-Legacy</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行动态划分</td>
      <td>--num-layer-list</td>
    </tr>
    <tr>
      <td>虚拟流水并行</td>
      <td>--num-layers-per-virtual-pipeline-stage</td>
    </tr>
    <tr>
      <td rowspan="8">Megatron-Core</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行动态划分</td>
      <td>--num-layer-list</td>
    </tr>
    <tr>
      <td>虚拟流水并行</td>
      <td>--num-layers-per-virtual-pipeline-stage</td>
    </tr>
    <tr>
      <td>专家并行</td>
      <td>--expert-model-parallel-size</td>
    </tr>
  </tbody>
  <tbody>
    <tr>
      <td rowspan="20">Megatron-Legacy </td>
      <td rowspan="6">Huggingface</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td>LoRA训练模块</td>
      <td>--lora-target-modules</td>
    </tr>
    <tr>
      <td>LoRA权重</td>
      <td>--lora-load</td>
    </tr>
    <tr>
      <td>LoRA r</td>
      <td>--lora-r</td>
    </tr>
    <tr>
      <td>LoRA alpa</td>
      <td>--lora-alpha</td>
    </tr>
    <tr>
      <td rowspan="4">Megatron-Core</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行动态划分</td>
      <td>--num-layer-list</td>
    </tr>
    <tr>
      <td>虚拟流水并行</td>
      <td>--num-layers-per-virtual-pipeline-stage</td>
    </tr>
    <tr>
      <td rowspan="6">Megatron-Legacy</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td>LoRA训练模块</td>
      <td>--lora-target-modules</td>
    </tr>
    <tr>
      <td>LoRA权重</td>
      <td>--lora-load</td>
    </tr>
    <tr>
      <td>LoRA r</td>
      <td>--lora-r</td>
    </tr>
    <tr>
      <td>LoRA alpa</td>
      <td>--lora-alpha</td>
    </tr>
  </tbody>
  <tbody>
    <tr>
      <td rowspan="13">Megatron-Core </td>
      <td rowspan="2">Huggingface</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td rowspan="4">Megatron-Legacy</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行动态划分</td>
      <td>--num-layer-list</td>
    </tr>
    <tr>
      <td>虚拟流水并行</td>
      <td>--num-layers-per-virtual-pipeline-stage</td>
    </tr>
    <tr>
      <td rowspan="5">Megatron-Core</td>
      <td>张量并行</td>
      <td>--target-tensor-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行</td>
      <td>--target-pipeline-parallel-size</td>
    </tr>
    <tr>
      <td>专家并行</td>
      <td>--expert-model-parallel-size</td>
    </tr>
    <tr>
      <td>流水并行动态划分</td>
      <td>--num-layer-list</td>
    </tr>
    <tr>
      <td>虚拟流水并行</td>
      <td>--num-layers-per-virtual-pipeline-stage</td>
    </tr>
  </tbody>
</table>

具体的权重转换功能命令介绍见[examples/README.md](./examples/README.md#2-权重转换)

---

## <span id="jump2"> 预训练加速算法与融合算子

ModelLink预训练支持张量并行、流水线并行等多种加速算法和融合算子，下表为各种加速特性对应的使能开关：

<table><thead>
  <tr>
    <th>使用场景</th>
    <th>特性名称</th>
    <th>具体参数</th>
    <th>Mcore</th>
    <th>Legacy</th>
  </tr></thead>
<tbody>
  <tr>
    <td rowspan="6">PTD并行</td>
    <td>张量并行</td>
    <td>--tensor-model-parallel-size</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>流水线并行</td>
    <td>--pipeline-model-parallel-size</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>流水线并行动态划分</td>
    <td>--num-layer-list</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>虚拟流水并行</td>
    <td>--num-layers-per-virtual-pipeline-stage</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>序列并行</td>
    <td>--sequence-parallel</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>分布式优化器</td>
    <td>--use-distributed-optimizer</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td rowspan="4">长序列并行</td>
    <td>长序列并行</td>
    <td>--context-parallel-size</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td>多并行方案</td>
    <td>--context-parallel-algo</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td>Send/recv掩盖加速</td>
    <td>--use-cp-send-recv-overlap</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td>Fused Ring Attention Update</td>
    <td>--use-fused-ring-attention-update</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td rowspan="3">MOE</td>
    <td>MOE专家并行</td>
    <td>--expert-model-parallel-size</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td>MOE重排通信优化</td>
    <td>--moe-permutation-async-comm</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td>GEMM</td>
    <td>--moe-grouped-gemm</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td rowspan="7">显存优化</td>
    <td>参数副本复用</td>
    <td>--reuse-fp32-param</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>激活函数重计算</td>
    <td>--recompute-activation-function</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
 <tr>
    <td>Swap Attention</td>
    <td>--swap-attention</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>重计算程度</td>
    <td>--recompute-granularity</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>重计算层数</td>
    <td>--recompute-num-layers</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>重计算方法</td>
    <td>--recompute-method</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>PP-Stage重计算</td>
    <td>--enable-recompute-layers-per-pp-rank</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td rowspan="5">融合算子</td>
    <td>Flash attention</td>
    <td>--use-flash-attn</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>Fused rmsnorm</td>
    <td>--use-fused-rmsnorm</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>Fused swiglu</td>
    <td>--use-fused-swiglu</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>Fused rotary position embedding</td>
    <td>--use-fused-rotary-pos-emb</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>Sliding window attention</td>
    <td>--sliding-window</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td rowspan="3">通信</td>
    <td>梯度reduce通算掩盖</td>
    <td>--overlap-grad-reduce</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>权重all-gather通算掩盖</td>
    <td>--overlap-param-gather</td>
    <td>Yes</td>
    <td>No</td>
  </tr>
  <tr>
    <td>MC2</td>
    <td>--use-mc2</td>
    <td>Yes</td>
    <td>Yes</td>
  </tr>
</tbody></table>


**注意事项**
1. 具体的预训练方法见[examples/README.md](./examples/README.md#大模型分布式预训练)
2. 如果需要开启MC2，需将 `modellink\training\arguments.py` 文件下，`validate_args_decorator`函数中的`args.use_mc2 = False`语句注释掉
3. Legacy结构模型不支持MOE和长序列特性，可以在Mcore结构模型上使能MOE和长序列特性




---

## <span id="jump3"> 分布式指令微调
ModelLink支持指令微调，方案与<a href="https://github.com/hiyouga/LLaMA-Factory/tree/main">DeepSpeed</a>统一，在微调效果保持一致的前提下，ModelLink可以表现出优异性能

【与<a href="https://github.com/hiyouga/LLaMA-Factory/tree/main">DeepSpeed</a>微调Loss对比】
<table>
<tr>
<th rowspan="1">Llama2-7b模型与<a href="https://github.com/hiyouga/LLaMA-Factory/tree/main">DeepSpeed</a>微调5个epoch后的loss对比图
<p align="center"> <img src="sources/images/tune_llama2_7b_ModelLink_DeepSpeed_compare.png" height="270px" width="500px"> </p>
</th>
<th>
<th rowspan="1">Qwen-7b模型与<a href="https://github.com/hiyouga/LLaMA-Factory/tree/main">DeepSpeed</a>微调4个epoch后的loss对比图
<p align="center"> <img src="sources/images/tune_qwen_7b_ModelLink_DeepSpeed_compare.png" height="270px" width="500px"> </p>
</tr>
</table>


【Llama2-7b微调后对话效果对比】
<table>
    <tr>
        <th rowspan="1">Question</th>
        <th rowspan="1">ModelLink</th>
        <th colspan="1"><a href="https://github.com/hiyouga/LLaMA-Factory/tree/main">DeepSpeed</a></th>
    </tr>
    <tr>
        <th>What is the product of 6 and 2?</th>
        <th>The product of 6 and 2 is 12.</th>
        <th>The product of 6 and 2 is 12.</th>
    </tr>
    <tr>
        <th>Look up the boiling point of water.</th>
        <th>The boiling point of water is 100°C (212°F)..</th>
        <th>The boiling point of water is 100 degrees Celsius (212 degrees Fahrenheit).</th>
    </tr>
    <tr>
        <th>Generate a poem that expresses joy.</th>
        <th>I open my arms and accept life's challenge, 

Embracing all of life's uncertainty. 

A future of promise awaits,

One that I can find in my fate. 

A journey full of hope and discovery,

A journey that will never end in disappointment. 

For I have found the strength to keep going,

Researching and learning, ever knowing. 

The future is mine, and mine alone,

A future that I have to own,

And I will never be alone,

For I will have the courage to face all of my fears,

And the joy of life will be mine forever.</th>
        <th>I am so happy, so thankful and blessed,

To have a heart that's full of cheer,

My soul is on fire, my spirit runs free,

My love is warm, my courage is high,

My world is bright and my outlook is clear,

My heart is light, my spirit runs free.

I take each day with a positive outlook,

My energy is so high, I can't be beat,

My joy is real, my emotions run deep,

My soul is full and my heart does soep.

I am thankful for everything I have,

My life is precious and my values ​​true,

My hope is high and my spirit runs free,

My soul is full and my heart does soep.</th>
    </tr>
</table>

【现版本实测性能、显存（硬件信息：Atlas 900 A2 PODc）】

下述列表中的模型，我们在[examples/README.md](./examples/README.md#大模型分布式指令微调)中提供了相应的使用说明，里面有详细的模型微调、推理、评估流程.
其中性能的单位是samples/s

<table>
    <tr>
        <th rowspan="2">模型</th>
        <th rowspan="2">--prompt-type</th>
        <th colspan="2">ModelLink + NPU</th>
        <th colspan="2"><a href="https://github.com/hiyouga/LLaMA-Factory/tree/main">DeepSpeed</a> + NPU</th>
        <th colspan="2"><a href="https://github.com/hiyouga/LLaMA-Factory/tree/main">DeepSpeed</a> + 参考</th>
    </tr>
    <tr>
        <th>序列长度</th>
        <th>性能</th>
        <th>序列长度</th>
        <th>性能</th>
        <th>序列长度</th>
        <th>性能</th>
    </tr>
    <tr>
        <td rowspan="1">llama2-7b</td>
        <td rowspan="1">llama2</td>
        <th>dynamic</th>
        <th>45.7</th>
        <th>dynamic</th>
        <th>40.4</th>
        <th>dynamic</th>
        <th>46.5</th>
    </tr>
    <tr>
        <td rowspan="1">llama2-13b</td>
        <td rowspan="1">llama2</td>
        <th>dynamic</th>
        <th>28.4</th>
        <th>dynamic</th>
        <th>17.8</th>
        <th>dynamic</th>
        <th>24.9</th>
    </tr>
</table>

上述列表中的数据均为实测数据，且具体微调的数据集均保持一致

【指令微调特性】

<table>
    <tr>
        <th></th>
        <th>特性名称</th>
        <th>特性入参</th>
    </tr>
    <tr>
        <td rowspan="1">支持数据集格式</td>
        <td colspan="2">Alpaca风格、Sharegpt风格</td>
    </tr>
    <tr>
        <td rowspan="4">微调数据预处理特性</td>
        <td>数据集字段映射</td>
        <td>--map-keys</td>
    </tr>
    <tr>
        <td>prompt模板</td>
        <td>--prompt-type</td>
    </tr>
    <tr>
        <td>数据集处理器</td>
        <td>--handler-name</td>
    </tr>
    <tr>
        <td>多样本pack</td>
        <td>--pack</td>
    </tr>
    <tr>
        <td rowspan="3">微调特性</td>
        <td>动态padding</td>
        <td>--variable-seq-lengths</td>
    </tr>
    <tr>
        <td>prompt模板</td>
        <td>--prompt-type</td>
    </tr>
    <tr>
        <td>多样本pack</td>
        <td>--reset-position-ids</td>
    </tr>
    <tr>
        <td rowspan="3">微调后推理对话特性</td>
        <td>历史对话记录轮数</td>
        <td>--history-turns</td>
    </tr>
    <tr>
        <td>hf对话模板</td>
        <td>--hf-chat-template</td>
    </tr>
    <tr>
        <td>prompt模板</td>
        <td>--prompt-type</td>
    </tr>
    <tr>
        <td rowspan="3">微调后评估特性</td>
        <td>评估数据集语言</td>
        <td>--eval-language</td>
    </tr>
        <td>hf对话模板</td>
        <td>--hf-chat-template</td>
    <tr>
        <td>prompt模板</td>
        <td>--prompt-type</td>
    </tr>
    <tr>
        <td>指令微调模板支持列表</td>
        <td  colspan="2">['empty', 'default', 'chatglm3_system', 'chatml', 'qwen', 'llama2', 'llama3', 'mixtral', 'alpaca', 'deepseek2', 'deepseek2-lite']</td>
    </tr>

</table>

---


## <span id="jump4"> 大模型Benchmark基线评估

ModelLink支持大模型在公开基准数据集上进行准确率评估，当前支持的Benchmark如下：

| Benchmark | 下载链接                                                                                     | 验证集  | ModelLink                                                            | OpenCompass                                                      |
|-----------|------------------------------------------------------------------------------------------|------|----------------------------------------------------------------------|------------------------------------------------------------------|
| MMLU      | [GitHub](https://people.eecs.berkeley.edu/~hendrycks/data.tar)                           | test | [45.73%](./examples/mcore/llama2/evaluate_llama2_7b_mmlu_ptd.sh)     | [45.3%](https://hub.opencompass.org.cn/dataset-detail/MMLU)      |
| CEval     | [HuggingFace](https://huggingface.co/datasets/ceval/ceval-exam/blob/main/ceval-exam.zip) | val  | [33.87%](./examples/mcore/llama2/evaluate_llama2_7b_ceval_ptd.sh)    | [32.5%](https://hub.opencompass.org.cn/dataset-detail/C-Eval)    |
| BoolQ     | [Juhe](https://www.juhe.cn/market/product/id/10243)                                      | dev  | [75.44%](./examples/mcore/llama2/evaluate_llama2_7b_boolq_ptd.sh)    | [74.9%](https://hub.opencompass.org.cn/dataset-detail/BoolQ)     |
| BBH       | [GitHub](https://github.com/suzgunmirac/BIG-Bench-Hard/tree/main/bbh)                    | test | [34.4%](./examples/mcore/llama2/evaluate_llama2_7b_bbh_ptd.sh)       | [32.5%](https://hub.opencompass.org.cn/dataset-detail/BBH)       |
| AGIEval   | [GitHub](https://github.com/ruixiangcui/AGIEval/tree/main)                               | test | [20.6%](./examples/mcore/llama2/evaluate_llama2_7b_agieval_ptd.sh)   | [20.6%](https://hub.opencompass.org.cn/dataset-detail/AGIEval)   |
| HumanEval | [GitHub](https://github.com/openai/human-eval/tree/master/data)                          | test | [12.8%](./examples/mcore/llama2/evaluate_llama2_7b_humaneval_ptd.sh) | [12.2%](https://hub.opencompass.org.cn/dataset-detail/HumanEval) |

ModelLink已支持模型的评估数据统计如下：

| 模型            | 任务     | ModelLink | 社区                                                                    | 模型               | 任务     | ModelLink | 社区                                                                                |
|---------------|--------|-----------|-----------------------------------------------------------------------|------------------|--------|-----------|-----------------------------------------------------------------------------------|
| Aquila-7B     | BoolQ  | 77.3%     | --                                                                    | Aquila2-7B       | BoolQ  | 77.8%     | --                                                                                |
| Aquila2-34B   | BoolQ  | 88.0%     | --                                                                    | Baichuan-7B      | BoolQ  | 69.0%     | [67.0%](https://hub.opencompass.org.cn/dataset-detail/BoolQ)                      |
| Baichuan-13B  | BoolQ  | 74.7%     | [73.6%](https://hub.opencompass.org.cn/dataset-detail/BoolQ)          | Baichuan2-7B     | BoolQ  | 70.0%     | [63.2%](https://hub.opencompass.org.cn/dataset-detail/BoolQ)                      |
| Baichuan2-13B | BoolQ  | 78.0%     | [67.0%](https://hub.opencompass.org.cn/dataset-detail/BoolQ)          | Bloom-7B         | MMLU   | 25.1%     | --                                                                                |
| Bloom-176B    | BoolQ  | 64.5%     | --                                                                    | ChatGLM3-6B      | MMLU   | 61.5%     | --                                                                                |
| GLM4-9B       | MMLU   | 74.5%     | [74.7%](https://huggingface.co/THUDM/glm-4-9b)                        | CodeQwen1.5-7B   | Human. | 54.8%     | [51.8%](https://qwenlm.github.io/zh/blog/codeqwen1.5/)                            |
| CodeLLaMA-34B | Human. | 48.8%     | [48.8%](https://paperswithcode.com/sota/code-generation-on-humaneval) | Gemma-2B         | MMLU   | 39.6%     | --                                                                                |
| Gemma-7B      | MMLU   | 52.2%     | --                                                                   | InternLM-7B      | MMLU   | 48.7%     | [51.0%](https://huggingface.co/internlm/internlm-7b)                              |
| Gemma2-9B     | MMLU   | 70.7%     | [71.3%](https://huggingface.co/google/gemma-2-9b)                    | Gemma2-27B       | MMLU   | 75.5%     | [75.2%](https://huggingface.co/google/gemma-2-27b)                                |
| LLaMA-7B      | BoolQ  | 74.6%     | [75.4%](https://hub.opencompass.org.cn/dataset-detail/BoolQ)         | LLaMA-13B        | BoolQ  | 79.6%     | [78.7%](https://hub.opencompass.org.cn/dataset-detail/BoolQ)                      |
| LLaMA-33B     | BoolQ  | 83.2%     | [83.1%](https://paperswithcode.com/sota/question-answering-on-boolq) | LLaMA-65B        | BoolQ  | 85.7%     | [86.6%](https://paperswithcode.com/sota/question-answering-on-boolq)              |
| LLaMA2-7B     | MMLU   | 45.7%     | --                                                                   | LLaMA2-13B       | BoolQ  | 82.2%     | [81.7%](https://paperswithcode.com/sota/question-answering-on-boolq)              |
| LLaMA2-34B    | BoolQ  | 82.0%     | --                                                                   | LLaMA2-70B       | BoolQ  | 86.4%     | --                                                                                |
| LLaMA3-8B     | MMLU   | 65.2%     | --                                                                   | LLaMA3-70B       | BoolQ  | 78.4%     | --                                                                                |
| LLaMA3.1-8B   | MMLU   | 65.3%     | --                                                                   | LLaMA3.1-70B     | MMLU   | 81.8%     | --                                                                                |
| LLaMA3.2-1B   | MMLU   | 31.8%     | [32.2%](https://modelscope.cn/models/LLM-Research/Llama-3.2-1B)      | LLaMA3.2-3B      | MMLU   | 56.3%     | [58.0%](https://modelscope.cn/models/LLM-Research/Llama-3.2-3B)                   |
| Mistral-7B    | MMLU   | 56.3%     | --                                                                   | Mixtral-8x7B     | MMLU   | 69.9%     | [70.6%](https://paperswithcode.com/sota/multi-task-language-understanding-on-mmlu) |
| Mistral-8x22B | MMLU   | 77%       | [77.8%](https://mistral.ai/news/mixtral-8x22b/)                      | MiniCPM-MoE-8x2B | BoolQ  | 83.9%     | --                                                                                |
| QWen-7B       | MMLU   | 58.1%     | [58.2%](https://huggingface.co/Qwen/Qwen-7B)                         | Qwen-14B         | MMLU   | 65.3%     | [66.3%](https://huggingface.co/Qwen/Qwen-14B)                                     |
| QWen-72B      | MMLU   | 74.6%     | [77.4%](https://huggingface.co/Qwen/Qwen-72B)                        | QWen1.5-0.5B     | MMLU   | 39.1%     | --                                                                                |
| QWen1.5-1.8b  | MMLU   | 46.2%     | [46.8%](https://qwenlm.github.io/zh/blog/qwen1.5/)                   | QWen1.5-4B       | MMLU   | 59.0%     | [56.1%](https://qwenlm.github.io/zh/blog/qwen1.5)                                 |
| QWen1.5-7B    | MMLU   | 60.3%     | [61.0%](https://qwenlm.github.io/zh/blog/qwen1.5/)                   | QWen1.5-14B      | MMLU   | 67.3%     | [67.6%](https://qwenlm.github.io/zh/blog/qwen1.5)                                 |
| QWen1.5-32B   | MMLU   | 72.5%     | [73.4%](https://huggingface.co/Qwen/Qwen-72B)                        | QWen1.5-72B      | MMLU   | 76.4%     | [77.5%](https://qwenlm.github.io/zh/blog/qwen1.5)                                 |
| Qwen1.5-110B  | MMLU   | 80.4%     | [80.4%](https://qwenlm.github.io/zh/blog/qwen1.5-110b/)              | Yi-34B           | MMLU   | 76.3%     | [75.8%](https://hub.opencompass.org.cn/dataset-detail/MMLU)                       |
| QWen2-0.5B    | MMLU   | 44.6%     | [45.4%](https://qwenlm.github.io/zh/blog/qwen2/)                     | QWen2-1.5B       | MMLU   | 54.7%     | [56.5%](https://qwenlm.github.io/zh/blog/qwen2/)                                  |
| QWen2-7B      | MMLU   | 70.3%     | [70.3%](https://qwenlm.github.io/zh/blog/qwen2/)                     | QWen2-57B-A14B   |MMLU|75.6% | [76.5%](https://qwenlm.github.io/zh/blog/qwen2/)|
| QWen2-72B     | MMLU   | 83.6%     | [84.2%](https://qwenlm.github.io/zh/blog/qwen2/)| MiniCPM-2B       | MMLU   | 51.6%     | [53.4%](https://github.com/OpenBMB/MiniCPM?tab=readme-ov-file#3)     |                                                                               
| DeepSeek-V2-Lite-16B   | MMLU   | 57.4%     | [58.3%](https://huggingface.co/deepseek-ai/DeepSeek-V2-Lite)      |
| QWen2.5-3B            | MMLU   | 65.6%     | [65.6%](https://qwenlm.github.io/blog/qwen2.5-llm/)                   | QWen2.5-7B      | MMLU   | 73.8%     | [74.2%](https://qwenlm.github.io/blog/qwen2.5-llm/)                     | 
| QWen2.5-14B           | MMLU   | 79.4%   | [79.7%](https://qwenlm.github.io/blog/qwen2.5-llm/)                   | QWen2.5-32B      | MMLU   | 82.8%     | [83.3%](https://qwenlm.github.io/blog/qwen2.5-llm/)                                |


具体的评估功能命令介绍见[examples/README.md](./examples/README.md#大模型分布式评估)

---


## <span id="jump5"> 基于昇腾芯片采集Profiling数据
Modellink支持基于昇腾芯片采集profiling数据，以提供对模型运行情况的分析，主要API如下：


```bash
--profile                        # 打开profiling采集数据开关
--profile-step-start  5          # 指定开启采集数据的步骤
--profile-step-end 6             # 指定结束采集数据的步骤，实际采集步数为 end-start，不包含end
--profile-ranks 0 1 2 3 4        # 指定采集数据的卡号，默认为-1，表示采集所有rank的profiling数据，可以设置为 0 1 2 3 4 5 6 7 8 9 列表指定全局卡号
--profile-level level2           # 数据采集水平，level0, 1, 2, 级别越高采集信息越多，默认为level0
--profile-with-cpu               # 是否采集CPU数据，加入参数采集
--profile-with-stack             # 采集指令运行堆栈，加入参数采集
--profile-with-memory            # 是否采集内存，加入参数采集
--profile-record-shapes          # 是否采集计算shape，加入参数采集
--profile-save-path ./profile_dir    # profiling数据采集保存路径
```

---

## <span id="jump6"> 基于昇腾芯片的确定性计算功能
昇腾芯片默认采用了不确定计算加速模型训练，有时为了重复实验与对比实验需要确定性的计算结果，ModelLink使能确定性计算的开关如下：

- 启动命令中加入开关
```shell
--use-deter-comp
```
- 环境变量中加入开关
```shell
export HCCL_DETERMINISTIC=True
```

---


## <span id="jump7"> 基于昇腾芯片的高可用特性
分布式优化器的思想是通过将优化器状态均匀地分布在数据并行组中来节省内存。基于该思想，设计了将数据并行组切分成两个副本数据并行组的方案，副本优化器将优化器状态均匀分布在副本数据并行组，实现优化器状态均有备份。结合华为自研的高可用框架，可实现以下功能：
1. 训练过程中，支持故障场景保存临终checkpoint，训练结果0损失。
2. 训练过程中，支持HBM的UCE故障检测，并完成在线修复，达到Step级重计算。

开启高可用特性时，副本优化器使用的静态内存有所增加，每个参数的理论字节数为（其中“d”是数据并行大小）：

|                                  | Non-distributed optim | Distributed optim | Replica optim |
|----------------------------------| ------ | ------ |---------------|
| fp16/bf16 param, fp16/bf16 grads | 20 | 4 + 16/d | 4 + 32/d       |
| fp16/bf16 param, fp32 grads      | 18 | 6 + 12/d | Supporting      |
| fp32 param, fp32 grads           | 16 | 8 + 8/d  | Supporting      |


- 启动命令中加入开关，并安装华为自研高可用框架mindio_ttp.whl
- mindio_ttp相关说明：https://www.hiascend.com/document/detail/zh/mindx-dl/60rc1/mindio/mindiottp
```shell
--enable-high-availability           #使能高可用特性的总开关
--enable-optimizer-state-local-copy  #使能保存上一步优化器状态，内存会进一步增加，默认可关闭
```

---

## 致谢

ModelLink由华为公司的下列部门联合贡献 ：
- 昇腾计算产品部
- 计算算法部
- 计算研究部
- 开源计算工具部: OCK
- 公共开发部：NAIE
- 全球技术服务部：GTS

感谢来自社区的每一个PR，欢迎贡献 ModelLink

---

## 安全声明

[ModelLink安全声明](https://gitee.com/ascend/ModelLink/wikis/%E5%AE%89%E5%85%A8%E7%9B%B8%E5%85%B3/%E5%AE%89%E5%85%A8%E5%A3%B0%E6%98%8E)
