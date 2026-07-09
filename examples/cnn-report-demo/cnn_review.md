中文摘要

卷积神经网络（Convolutional Neural Network, CNN）是深度学习在计算机视觉领域的核心模型。本文回顾 CNN 的基本原理与代表性架构演进：从局部连接、权值共享与池化等归纳偏置出发，梳理由 LeNet 到 AlexNet、VGG、GoogLeNet 与 ResNet 的发展脉络，并结合 ILSVRC 公开赛果分析深度增加与错误率下降的关系。进而总结批归一化、Dropout、残差连接与数据增强等关键训练技术，讨论 CNN 在图像分类、检测与分割中的应用，最后指出模型效率、可解释性与在 Transformer 冲击下的定位等挑战。综述表明，结构先验与可训练性的持续改进，是 CNN 性能跃升的主线。

关键词：卷积神经网络；深度学习；计算机视觉；残差网络；图像分类

Abstract

The Convolutional Neural Network (CNN) is the core model of deep learning in computer vision. This paper reviews the fundamentals and representative architectures of CNNs. Starting from inductive biases such as local connectivity, weight sharing and pooling, it traces the evolution from LeNet to AlexNet, VGG, GoogLeNet and ResNet, and analyses the relationship between increasing depth and decreasing error using public ILSVRC results. Key training techniques including batch normalization, dropout, residual connections and data augmentation are summarized, followed by applications in classification, detection and segmentation. Open challenges in efficiency, interpretability and the positioning of CNNs against Transformers are discussed.

Keywords: convolutional neural network; deep learning; computer vision; residual network; image classification

# 1 引言

计算机视觉的核心难题在于从高维像素中提取对平移、尺度与形变鲁棒的特征。传统方法依赖人工设计的特征算子，泛化能力受限。卷积神经网络通过端到端学习分层特征，将特征提取与分类统一到同一可微框架内，自 2012 年起在大规模图像识别上取得突破，成为视觉领域的主导范式。

本文的组织如下：第 2 节阐述 CNN 的基本原理与核心组件；第 3 节梳理代表性架构的演进并结合公开赛果分析其规律；第 4 节总结关键训练技术；第 5 节概述典型应用；第 6 节讨论挑战与展望。

# 2 基本原理与核心组件

CNN 的有效性源于三个结构先验：局部连接、权值共享与下采样。它们大幅降低参数量，并赋予模型对局部模式的平移等变性。

## 2.1 卷积层

卷积层以可学习的卷积核在输入特征图上滑动，计算局部加权和，提取边缘、纹理等局部模式。同一卷积核在空间上共享权值，使得对某一位置学到的特征可迁移到其他位置。多个卷积核并行输出多个通道，逐层堆叠后感受野扩大，特征由低级到高级逐步抽象。

## 2.2 池化层

池化对特征图做局部下采样（如最大池化取邻域最大值），在降低分辨率与计算量的同时增强对小幅平移与形变的不变性。近年部分架构以带步长的卷积替代显式池化，以保留更多可学习性。

## 2.3 激活与全连接

非线性激活函数是网络表达能力的来源。修正线性单元（ReLU）以其计算简单、缓解梯度消失的特性，取代早期的 Sigmoid 成为主流。网络末端通常接全连接层或全局平均池化，将空间特征汇聚为类别得分。

# 3 代表性架构的演进

CNN 的性能提升与网络深度的增加高度相关。表 1 汇总了若干里程碑架构在 ILSVRC 上的表现。

表1 代表性 CNN 架构对比（数据为公开发表 / 赛果，供参照）

| 架构 | 年份 | 层数 | top-5 错误率 | 核心贡献 |
|---|---|---|---|---|
| AlexNet | 2012 | 8 | 16.4% | ReLU、Dropout、GPU 训练 |
| VGG | 2014 | 19 | 7.3% | 小卷积核深层堆叠 |
| GoogLeNet | 2014 | 22 | 6.7% | Inception 多尺度模块 |
| ResNet | 2015 | 152 | 3.57% | 残差连接、可训练极深网络 |

如图 1，ILSVRC 冠军的 top-5 错误率在五年内从 AlexNet 的 16.4% 降至 ResNet 的 3.57%，并首次越过约 5.1% 的人类参考水平；图 2 显示同期网络深度从 8 层增至 152 层，二者呈明显的协同关系。

![](fig1-ilsvrc.png)

图1 五年内 ImageNet 错误率显著下降（ILSVRC 公开赛果）

![](fig2-depth.png)

图2 代表性架构的网络深度增长（公开发表结果）

## 3.1 LeNet 与早期探索

LeNet 确立了"卷积—池化—全连接"的经典范式，并成功应用于手写数字识别，但受限于当时的算力与数据规模，未能在更复杂任务上普及。

## 3.2 AlexNet 与深度学习复兴

AlexNet 在 2012 年 ILSVRC 上以显著优势夺冠，重新点燃了深度学习热潮。其关键在于用 ReLU 加速训练、以 Dropout 抑制过拟合，并借助 GPU 完成大规模训练。

## 3.3 VGG 与 GoogLeNet

VGG 证明了以多个 3×3 小卷积核堆叠替代大卷积核，可在相同感受野下加深网络并减少参数。GoogLeNet 则提出 Inception 模块并行多种尺度的卷积，在控制计算量的同时提升表达能力。

## 3.4 ResNet 与残差学习

随着深度增加，梯度消失与退化问题使极深网络难以训练。ResNet 引入残差连接（跳跃连接），令网络学习相对于恒等映射的残差，从而稳定训练上百层的网络，将错误率进一步压低，并成为后续众多架构的基础。

# 4 关键训练技术

架构之外，训练技术的进步同样关键。批归一化（Batch Normalization）通过规范化层输入分布，加速收敛并允许更大学习率；Dropout 以随机失活缓解过拟合；残差连接改善了深层网络的梯度流动；数据增强（翻转、裁剪、色彩扰动等）在不增加标注成本的前提下扩充样本分布，提升泛化。

# 5 应用领域

CNN 从图像分类扩展到更广的视觉任务：在目标检测中作为骨干网络提取特征，配合区域建议或单阶段检测头定位物体；在语义与实例分割中，全卷积结构实现像素级预测；此外在人脸识别、医学影像分析与视频理解等领域均有广泛应用。

# 6 挑战与展望

尽管成效显著，CNN 仍面临若干挑战：其一，深层模型参数与算力开销大，轻量化与模型压缩是落地关键；其二，决策过程的可解释性不足，限制了在高风险场景的应用；其三，随着 Vision Transformer 的兴起，纯卷积结构的主导地位受到冲击，卷积与自注意力的融合成为新的研究方向。总体而言，将有效的结构先验与更强的可训练性相结合，仍是视觉模型演进的主线。

# 参考文献

[1] LeCun Y, Bottou L, Bengio Y, et al. Gradient-based learning applied to document recognition[J]. Proceedings of the IEEE, 1998, 86(11): 2278-2324.
[2] Krizhevsky A, Sutskever I, Hinton G E. ImageNet classification with deep convolutional neural networks[C]// Advances in Neural Information Processing Systems. 2012: 1097-1105.
[3] Simonyan K, Zisserman A. Very deep convolutional networks for large-scale image recognition[C]// International Conference on Learning Representations. 2015.
[4] Szegedy C, Liu W, Jia Y, et al. Going deeper with convolutions[C]// IEEE Conference on Computer Vision and Pattern Recognition. 2015: 1-9.
[5] He K, Zhang X, Ren S, et al. Deep residual learning for image recognition[C]// IEEE Conference on Computer Vision and Pattern Recognition. 2016: 770-778.
[6] Ioffe S, Szegedy C. Batch normalization: accelerating deep network training by reducing internal covariate shift[C]// International Conference on Machine Learning. 2015: 448-456.
