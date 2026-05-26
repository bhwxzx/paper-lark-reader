import os

sections = [
"""<!-- PAGE 1 START -->
DreamWaQ: Learning Robust Quadrupedal Locomotion With Implicit
Terrain Imagination via Deep Reinforcement Learning
I Made Aswin Nahrendra1, Byeongho Yu1, and Hyun Myung1∗, Senior Member, IEEE
""",
"""# Abstract
四足机器人类似于腿足动物在非结构化地形中行走的物理能力。然而，由于功能复杂性并需要适应各种地形，为四足机器人设计控制器提出了重大挑战。最近，受腿足动物从经验中学习行走方式的启发，深度强化学习已被用于合成自然的四足运动。然而，最先进的方法严重依赖于复杂且可靠的感知框架。此外，仅依赖本体感觉的先前工作在克服具有挑战性的地形（特别是长距离地形）方面的实证表现有限。这项工作提出了一种新颖的四足运动学习框架，允许四足机器人穿过具有挑战性的地形，即使感知模态有限。所提出的框架在真实世界的户外环境中得到了验证，并且在单次长距离运行中涵盖了不同条件。

图 1：DreamWaQ 概览。通过在仿真中学习运动策略，机器人可以在零样本仿真到现实（Zero-shot sim-to-real）的情况下走过楼梯等具有挑战性的地形。
""",
"""# I. Introduction
近年来，四足机器人在工业检查和探索等各种应用中发挥了重要作用 **[1]**–**[6]**。与轮式移动机器人不同，四足机器人可以穿越非结构化地形，但相对较难控制。传统的基于模型的控制器通常需要一个复杂的流程，包括状态估计、轨迹优化、步态优化和执行器控制 **[1]**–**[3]**, **[7]**–**[11]**。这种复杂的基于模型的流程需要大量的人工努力来进行精确的建模和严格的参数调整。此外，线性化的四足模型常常限制了其性能，阻碍了其充分发挥能力。

腿足动物可以通过视觉感知周围的地形来有效地规划其步态。这种自然机制启发了许多通过深度强化学习 (Reinforcement Learning) 训练感知运动策略的工作，使得四足机器人能够穿越非结构化地形 **[12]**–**[15]**。在这些前沿工作中，机器人配备了外部感受传感器（如相机或 LiDAR）来观测其周围环境。随后，外部感知被用于与控制器一起规划机器人的轨迹和步态，以安全地穿过环境。

然而，外部感知并不总是可靠的。相机可能会在恶劣的天气和光照条件下发生故障，虽然 3D LiDAR 可用于区分地面和可通行区域，但准确估计地形的物理特性仍然具有挑战性 **[16]**–**[18]**。例如，雪可能看起来像是坚固且可通行的表面，但它实际上是柔软且可塑的。此外，对相机来说看似无法通行的高草仍然可以被腿足机器人轻松穿越。

与此同时，本体感受传感器，如惯性测量单元 (IMU) 和关节编码器，与外部感受传感器相比，相对较轻且鲁棒性强。最近的工作表明，通过结合不同的本体感受模态，四足机器人可以学习估计其周围地形 **[19]**–**[23]** 和身体状态 **[24]**。然而，这些工作在具有多种挑战性地形的长距离操作方面的实证展示有限，而在这些地形中，由于高度的不确定性和估计误差，腿足机器人可能会失败。

在学习运动策略的同时通过本体感知估计周围地形的属性需要一个迭代过程 **[19]**, **[20]**, **[23]**。策略需要理解地形属性以学习鲁棒的行为。然而，为了充分学习地形属性，机器人应该能够相应地行走并探索广泛的地形属性谱系。这种困境通常被称为表征学习瓶颈（representation learning bottleneck）**[25]**，它可能会阻碍最优的策略学习。因此，需要一种能够联合学习鲁棒策略和精确环境表征的学习框架。

在本文中，我们提出了一个称为 DreamWaQ（Dream Walking for Quadrupedal Robots）的框架，该框架通过深度强化学习算法，仅利用本体感知训练用于四足机器人的鲁棒运动策略。
<!-- PAGE 1 END -->
""",
"""<!-- PAGE 2 START -->
DreamWaQ 训练运动策略以隐式推断地形属性，如高度图、摩擦力、恢复系数和障碍物。因此，机器人可以调整其步态以安全地穿过各种地形。我们在 Unitree A1 **[26]** 机器人上部署了 DreamWaQ，使其能够鲁棒地穿过具有挑战性的自然和人造环境。

总结来说，这项工作的贡献有以下三个方面：
1) 提出了一种基于非对称 actor-critic 架构的新颖运动学习框架，仅使用本体感知来隐式地想象地形属性。
2) 提出了一种上下文辅助估计器网络（Context-aided Estimator Network），以联合估计身体状态和环境上下文。与策略相结合，我们的方法优于现有的基于学习的方法。
3) 通过在多样化的户外环境中行走，对真实世界中学到的策略进行了鲁棒性和持久性评估。据我们所知，这是首次展示体积明显小于 ANYmal 的 Unitree A1 机器人能够持续行走在山丘和庭院等具有挑战性的地形上。

本文的其余部分组织如下。第二章（Section II）详细讨论了我们提出的方法。第三章（Section III）介绍了实验设置、结果以及对所提出方法与基线方法的深度比较分析。最后，第四章（Section IV）对本工作进行总结并简要探讨未来的工作方向。
""",
"""# II. DreamWaQ

## A. Preliminaries
在这项工作中，环境被建模为一个无限范围的部分可观测马尔可夫决策过程 (POMDP)，由元组 $M = (S,O,A,d_0,p,r,\gamma)$ 定义。完整状态、部分观测和动作是连续的，分别由 $s \in S$, $o \in O$, 和 $a \in A$ 定义。环境以初始状态分布 $d_0(s_0)$ 开始；并以状态转移概率 $p(s_{t+1}|s_t,a_t)$ 推进；每次转移由奖励函数 $r: S \times A \rightarrow \mathbb{R}$ 赋予奖励。折扣因子定义为 $\gamma \in [0,1)$。此外，在本文中，我们将过去 $H$ 次测量的时刻 $t$ 的时间观测定义为 $o^H_t = [o_t, o_{t-1}, ..., o_{t-H}]^T$。我们还定义了一个上下文向量 $z_t$，它包含世界状态的潜在表征。上下文向量是使用将在 Section II-C 中讨论的方法推断出来的。

## B. Implicit Terrain Imagination
最近的工作利用了师生训练范式 **[27]**。尽管实证表明学生策略与教师策略一样好，但行为克隆 (BC) 将学生策略的性能限制在教师策略的水平 **[19]**, **[20]**, **[23]**。此外，顺序训练教师和学生网络会导致数据效率低下 **[24]**。学生策略可能无法探索教师策略在强化学习早期阶段学到的失败状态。这种限制是因为，在行为克隆期间，学生策略仅能获得教师策略提供的良好动作监督。

为了学习隐式地形想象，我们采用了非对称 actor-critic 架构 **[28]**。我们发现，在 actor-critic 算法中，策略与价值网络之间的交互足以学习出一个鲁棒的运动策略，该策略能够在给定部分时间观测的情况下隐式地想象特权观测。在 DreamWaQ 中，策略（actor）接收部分时间观测 $o^H_t$ 作为输入，而价值网络（critic）接收完整状态 $s_t$，见图 1。在这项工作中，我们设置 $H = 5$。因此，由于只需要一个训练阶段，训练期间的数据效率显著提高。此外，策略在训练期间能够探索所有可能的轨迹，通过泛化提高其鲁棒性。在这项工作中，策略通过近端策略优化 (PPO) 算法进行优化 **[29]**。

**1) Policy Network:** 策略 $\pi_\phi(a_t|o_t, v_t, z_t)$ 是一个由 $\phi$ 参数化的神经网络，它在给定本体感觉观测 $o_t$、机身速度 $v_t$ 以及潜在状态 $z_t$ 的情况下推断动作 $a_t$。$o_t$ 是通过关节编码器和 IMU 直接测量的，而 $v_t$ 和 $z_t$ 是由上下文辅助估计器网络 (CENet) 估计的，这将在 Section II-C 中讨论。$o_t$ 是一个 $n \times 1$ 的向量，定义如下：
$$o_t = [\omega_t, g_t, c_t, \theta_t, \dot{\theta}_t, a_{t-1}]^T$$
其中，$\omega_t, g_t, c_t, \theta_t, \dot{\theta}_t$, 和 $a_{t-1}$ 分别是机身角速度、机身坐标系中的重力向量、机身速度命令、关节角度、关节角速度和先前的动作。

**2) Value Network:** 价值网络被训练来输出状态值的估计 $V(s_t)$。与策略不同，价值网络接收特权观测 $s_t$，其定义如下：
$$s_t = [o_t, v_t, d_t, h_t]^T$$
其中 $d_t$ 是随机施加在机器人机身上的扰动力，$h_t$ 是机器人周围环境的高度图扫描，作为价值网络的外部感知线索。在所提出的 DreamWaQ 中，策略网络被训练为从本体感觉中隐式地推断 $d_t$ 和 $h_t$。

**3) Action Space:** 动作空间是一个 $12 \times 1$ 的向量 $a_t$，对应于机器人的期望关节角度。为了促进学习，我们训练策略来推断机器人静止站立姿态 $\theta_{stand}$ 附近的期望关节角度。因此，机器人的期望关节角度定义为：
$$\theta_{des} = \theta_{stand} + a_t$$
期望关节角度通过每个关节的比例-微分 (PD) 控制器进行跟踪。

**4) Reward Function:** 我们的奖励函数密切遵循其他工作 **[12]**, **[19]**, **[20]**, **[22]**, **[24]**, **[30]**，以突出 DreamWaQ 组成部分的效果，而不是调整奖励。奖励函数由用于跟踪的速度指令奖励和稳定性奖励组成，以产生稳定且自然的运动行为。奖励函数的详细信息见表 I。策略在每个状态下采取动作的总奖励为：
$$r_t(s_t, a_t) = \sum r_i w_i$$
其中 $i$ 是表 I 中所示的每个奖励的索引。

学习运动策略的复杂奖励函数通常包括一个电机功率最小化项。然而，该奖励是在不考虑每个电机功率使用平衡的情况下将总功率最小化。因此，从长远来看，某些电机可能会比其他电机更快过热。因此，我们引入了一种功率分配奖励，通过惩罚机器上所有使用的电机之间具有高方差的电机功率，从而在现实世界中减少电机过热现象。

**5) Curriculum Learning:** 我们利用了受游戏启发的课程 **[12]**，以确保在困难地形上的渐进式运动策略学习。地形由平滑、粗糙、离散以及楼梯地形组成，具有 [0°, 22°] 范围内 10 个倾斜级别。此外，我们发现，对于低速运动，使用网格自适应课程 **[23]** 能够实现更好且更稳定的转向，从而防止脚部绊倒。
<!-- PAGE 2 END -->
""",
"""<!-- PAGE 3 START -->
表 I：奖励函数元素。$\exp(\cdot)$ 和 $\text{var}(\cdot)$ 分别是指数量和方差算符。$(\cdot)_{des}$ 和 $(\cdot)_{cmd}$ 分别表示期望值和指令值。$x, y, z$ 定义在机器人机身坐标系下，$v_{xy}$ 代表 $xy$ 平面内的线速度。

| 奖励项 | 公式 $r_i$ | 权重 $w_i$ |
| --- | --- | --- |
| 线速度跟踪 | $\exp( -4(v_{cmd,xy} - v_{xy})^2 )$ | 1.0 |
| 角速度跟踪 | $\exp( -4(\omega_{cmd,yaw} - \omega_{yaw})^2 )$ | 0.5 |
| 线速度(z) | $v_z^2$ | -2.0 |
| 角速度(xy) | $\omega_{xy}^2$ | -0.05 |
| 方向 | $\|g\|^2$ | -0.2 |
| 关节加速度 | $\ddot{\theta}^2$ | -2.5×10^-7 |
| 关节功率 | $\|\tau\| \|\dot{\theta}\|$ | -2×10^-5 |
| 机身高度 | $(h_{des} - h)^2$ | -1.0 |
| 落脚高度间隙 | $(p_{des,f,z,k} - p_{f,z,k})^2 \cdot v_{f,xy,k}$ | -0.01 |
| 动作速率 | $(a_t - a_{t-1})^2$ | -0.01 |
| 平滑度 | $(a_t - 2a_{t-1} + a_{t-2})^2$ | -0.01 |
| 功率分配 | $\text{var}(\tau \cdot \dot{\theta})^2$ | -10^-5 |

图 2：CENet 的架构包含一个机身速度估计模型和一个共享统一编码器的自编码器模型。共享编码器被训练为联合提供鲁棒的机身状态和上下文估计。

## C. Context-Aided Estimator Network
在 Section II-B 中描述的方法训练的策略需要 $v_t$ 和 $z_t$ 作为输入，这可以从本体感觉中估计。先前的工作估计 $z_t$ 作为理解地形属性的潜在变量 **[20]**, **[21]**, **[23]**。此外，使用学习到的网络估计 $v_t$ 通过消除累积估计漂移显著提高了运动策略的鲁棒性 **[24]**。

受到这些先前工作的启发，我们发现地形和机身状态估计之间的相互作用显著提高了机身状态估计的准确性。不同于仅显式估计机器人状态，我们提出了一种上下文辅助估计器网络（CENet）架构，以联合学习估计和推断环境的潜在表征。提出的 CENet 的优点包括：
1) 借助共享编码器架构，网络架构显著简化，并且在推理期间同步运行；
2) 编码器网络可以通过自编码机制联合学习机器人的前向和后向动力学，从而提高其准确性。

CENet 由单一编码器和多头解码器架构组成，如图 2 所示。编码器网络将 $o^H_t$ 编码为 $v_t$ 和 $z_t$。第一个头估计 $v_t$，而第二个头重构 $o_{t+1}$。我们利用了一个 $\beta$-变分自编码器 ($\beta$-VAE) **[31]**–**[33]** 作为自编码器架构。CENet 使用混合损失函数进行优化，定义如下：
$$L_{CE} = L_{est} + L_{VAE}$$
其中 $L_{est}$ 和 $L_{VAE}$ 分别是机身速度估计损失和 VAE 损失。对于显式状态估计，我们在估计的机身速度 $\tilde{v}_t$ 与来自仿真器的真实值 $v_t$ 之间采用了均方误差 (MSE) 损失，如下所示：
$$L_{est} = \text{MSE}(\tilde{v}_t, v_t)$$

VAE 网络使用标准的 $\beta$-VAE 损失进行训练，其中包括重构损失和潜变量损失。我们采用 MSE 作为重构损失，并采用 Kullback-Leibler (KL) 散度 **[34]** 作为潜变量损失。VAE 损失制定为：
$$L_{VAE} = \text{MSE}(\tilde{o}_{t+1}, o_{t+1}) + \beta D_{KL}(q(z_t | o^H_t) \| p(z_t))$$
其中 $\tilde{o}_{t+1}$ 是重构的下一步观测，$q(z_t | o^H_t)$ 是在给定 $o^H_t$ 的情况下 $z_t$ 的后验分布。$p(z_t)$ 是由高斯分布参数化的上下文先验分布。我们选择标准正态分布作为先验分布，因为所有观测都被归一化为零均值和单位方差。

此外，在策略网络训练期间从估计器网络进行自举 (bootstrapping) 可能会提高学到的策略的仿真到现实（sim-to-real）鲁棒性 **[24]**。然而，我们发现自举也可能会由于在学习初期存在巨大的学习噪声而损害策略的性能。因此，我们提出了一种自适应自举 (AdaBoot) 方法，该方法在训练期间自适应调整自举概率。AdaBoot 受变异系数 (CV) 的控制，即 $m$ 个经过域随机化的环境中回合奖励的标准差与均值之比。核心思想是，当 $m$ 个智能体奖励的 CV 较小时需要进行自举，使策略对不准确的估计具有更高的鲁棒性。然而，当智能体尚未充分学习时（表现为其奖励中存在较大的 CV），则不应该进行自举。我们将每次学习迭代的自举概率定义如下：
$$p_{boot} = 1 - \tanh(\text{CV}(R))$$
其中 $p_{boot} \in [0,1]$ 是自举概率，$R$ 是来自 $m$ 个域随机化环境的回合奖励的 $m \times 1$ 向量。$\text{CV}(\cdot)$ 和 $\tanh(\cdot)$ 分别是变异系数和双曲正切操作。$\tanh$ 用于将 $\text{CV}(R)$ 平滑地限制在 1 以下。
<!-- PAGE 3 END -->
""",
"""<!-- PAGE 4 START -->
表 II：仿真中应用的域随机化范围。

| 参数 | 随机化范围 | 单位 |
| --- | --- | --- |
| 负载 | [-1, 2] | kg |
| Kp 因子 | [0.9, 1.1] | Nm/rad |
| Kd 因子 | [0.9, 1.1] | Nms/rad |
| 电机强度因子 | [0.9, 1.1] | Nm |
| 质心偏移 | [-50, 50] | mm |
| 摩擦系数 | [0.2, 1.25] | - |
| 系统延迟 | [0.0, 15.0] | ms |

图 3：不同算法的学习曲线。显示的结果来自十个不同的随机种子。曲线和阴影区域分别表示在十个不同种子下的奖励的均值和标准差。Oracle 策略能够像 **[12]** 中那样获取机器人周围环境的高度图测量值。

# III. Experiments

## A. Compared Methods
为了进行比较评估，我们比较了以下仅使用本体感觉的算法：
1) **Baseline** **[12]**：在没有任何自适应机制的情况下训练的策略。
2) **AdaptationNet** **[20]**, **[21]**：策略通过师生训练框架以及一个隐式的环境因素编码器进行训练。策略网络由一维卷积神经网络 (CNN) 层和多层感知器 (MLP) 层组成。
3) **EstimatorNet** **[24]**：策略与显式估计身体状态且无上下文估计的估计器网络同时训练。
4) **DreamWaQ w/o AdaBoot**：不带自适应自举的本提议方法。
5) **DreamWaQ w/ AdaBoot**：带自适应自举的本提议方法。

所有上述方法均采用 Section II 中详细描述的课程策略和奖励函数进行训练。为了公平比较，我们对所有方法使用了相同的网络架构并固定了初始随机种子。所有网络在隐藏层中均使用指数线性单元 (ELU) **[35]** 作为激活函数。

## B. Simulation
我们使用基于 **[12]** 开源实现的 Isaac Gym 仿真器 **[36]** 同步训练策略、价值和 CENet 网络，共进行了 1,000 次迭代。我们并行训练了 4,096 个经过域随机化的智能体。随机化参数的详细信息列于表 II。对于所有算法，策略网络采用 PPO 算法进行训练，剪裁范围、广义优势估计因子和折扣因子分别设为 0.2、0.95 和 0.99。网络使用 Adam 优化器 **[37]** 进行优化，学习率为 $10^{-3}$。
所有训练都在一台配备 Intel Core i7-8700 CPU @ 3.20 GHz、32 GB RAM 和一块 NVIDIA RTX 3060Ti GPU 的台式 PC 上进行。算法花费大约一小时即可生成相当于在现实世界中 46 天的训练数据。

图 3 比较了 DreamWaQ 与其他所有方法在学习 Unitree A1 机器人的运动策略方面的学习曲线。可以看出，即使 EstimatorNet 最初具有比 AdaptationNet 更高的平均回合奖励，但其性能在多次迭代后由于遇到了更困难的地形而骤降。相反，DreamWaQ 始终优于所有其他方法。此外，尽管在没有外部感受的情况下行走，DreamWaQ 的表现几乎与直接获取周围地形高度图的 Oracle 策略一样好。

## C. Real-World Experimental Setup
真实世界的实验是使用 Unitree A1 **[26]** 机器人进行的。所有的估计和控制过程都在安装在机器人顶部的 Intel NUC 上运行，我们使用了 **[38]** 中提供的 PyBind 接口将关节角度命令发送给机器人。一个额外的带有电池的车载 PC 使得机器人的有效载荷增加了大约 500 克。在推理过程中，策略与 CENet 能够以 50 Hz 同步运行。所需的关节角度通过每个关节的 PD 控制器以 200 Hz 进行跟踪，比例和微分增益分别为 $K_p = 28$ 和 $K_d = 0.7$。

## D. Command Tracking
我们在 Gazebo 仿真中评估了指令跟踪性能以获取准确的真实值。机器人接受了十分钟的随机指令，这些指令每隔十秒在 $[-1.0, 1.0]$ 中均匀采样。为了进行公平对比，每个控制器使用相同的随机种子生成随机指令。每个控制器使用不同的随机种子运行五次，以验证可重复性。我们将绝对跟踪误差 (ATE) 作为性能指标，并构建了一个如图 4 所示的条形图。DreamWaQ 相比其他方法的显著改进通过成对 t 检验测量得出，如图 4 所示，表明 DreamWaQ 始终优于基准线。此外，所提出的 AdaBoot 方法由于其在训练过程中的统计自举策略，同样显著改善了 DreamWaQ。
<!-- PAGE 4 END -->
""",
"""<!-- PAGE 5 START -->
表 III：鲁棒性测试。加粗的值表示鲁棒性最强的结果。

| 算法 | 最大推力 (m/s) | 存活率 (%) |
| --- | --- | --- |
| Baseline | 0.511 ± 0.053 | 20.51 ± 6.44 |
| AdaptationNet | 0.714 ± 0.096 | 82.37 ± 2.49 |
| EstimatorNet | 0.871 ± 0.124 | 80.92 ± 5.73 |
| DreamWaQ w/o AdaBoot | 1.015 ± 0.121 | 90.71 ± 1.25 |
| DreamWaQ w/ AdaBoot | 1.121 ± 0.164 | 95.23 ± 1.61 |

图 4：以箱线图表示的指令跟踪误差。$v_{x}^e$ 和 $v_{y}^e$ 分别是前向和侧向速度跟踪误差，以 m/s 为单位测量。$\omega_{z}^e$ 是偏航率跟踪误差，以 rad/s 为单位测量。$****$ 注释表示 P 值 $< 10^{-4}$ 的测量。

图 5：CENet 与 EstimatorNet 的估计误差。当机器人的脚被楼梯绊倒时，CENet 的优越性得到了突出。

## E. Explicit Estimation Comparison
我们在机器人在楼梯环境行走的仿真中，在平方估计误差方面比较了 CENet 和 EstimatorNet，如图 5 所示。在正常行走条件下，得益于 VAE 的自编码机制支持的前向-后向动力学学习，CENet 在平坦地形上展现出了小误差。

当机器人在楼梯上绊倒时，CENet 的优势变得突出，因为在这种情况下 EstimatorNet 无法准确估计机身速度。在严重情况下，不准确的估计会导致灾难性故障。相反，CENet 能够准确地估计机身速度，从而使得机器人能够安全地爬楼梯。我们假设这得益于两个因素：1) 前向-后向动力学学习在所有地形中提供了更准确的估计；2) 使用 DreamWaQ 时，编码器被联合训练以预测地形属性；因此，它可以隐式地推理出地形属性，这有助于对显式估计进行调节。

## F. Robustness Analysis
为了测试所学策略的鲁棒性，我们在仿真中用随机推力干扰机器人。该推力是在机器人机身坐标系的 $x, y, z$ 轴上沿着随机方向以一秒的间隔施加随机速度，直到其摔倒。随机推力速度从 $[-v_{push}^{max}, v_{push}^{max}]$ 均匀采样，其中 $v_{push}^{max} \ge 0$ 为最大推力速度。我们还测量了存活率，即机器人在 30 分钟的随机行走中保持存活的时间百分比。鲁棒性测试的结果汇总于表 III。

在所有方法中，当命令向量发生显著变化，要求机器人快速刹车并改变动作时，机器人大都会摔倒。然而，DreamWaQ 显著比所有其他方法更加鲁棒，其能够承受的最大推力和高存活率通过定量数据得到了证实。这得益于 DreamWaQ 准确估计与鲁棒策略学习之间的相互作用。此外，所提出的 AdaBoot 方法还在不牺牲基础性能的情况下提高了鲁棒性。

在现实世界中，DreamWaQ 的策略对非结构化地形具备鲁棒性。图 6 展示了当机器人面临脚步绊倒和滑倒时的反射反应。机器人可以立即调整其步态并稳定其姿势。由于岑确切鲁棒的 CENet，机器人在机身速度估计方面没有任何问题，能够毫无性能下降地继续前进。

在图 6(a) 中，机器人展示了上下楼梯的不同步态。下楼梯时，机器人倾向于将其身体压近地面并使前脚远离身体，这是快速找到稳定落脚点的关键步态模式。同时，机器人通过显著增加其步长调整了其上楼梯的步态。这种步态是必要的，这样它的脚就可以安全地跨过楼梯并在攀爬时找到一个稳定的落脚点。此外，图 6(b) 展示了对滑倒的适应，机器人可以立即检测到不规则的立足点并调整其步态模式。随后，机器人尝试恢复其正常模式并继续行走。

## G. Long-Distance Walk
我们在两个具有挑战性的户外赛道上部署了机器人，以展示 DreamWaQ 的鲁棒性。赛道 A 是一个校园内的庭院，包含许多斜坡和可变形的地形。赛道 B 是一个校园内的山丘，海拔上升高达 22 米。赛道 A 和 B 的总长度分别为 430 米和 465 米。赛道的细节展示在图 7 中。机器人的轨迹是使用安装在其顶部的频率为 10 Hz 的实时动态 (RTK) GPS **[39]** 测量的。有关完整的实验视频，请参阅项目网站。
<!-- PAGE 5 END -->
""",
"""<!-- PAGE 6 START -->
图 6：应对在非结构化地形中遇到的 (a) 绊倒和 (b) 滑倒导致的不确定性的脚部反射反应。可以获取在线的实时实验视频。

图 7：用于测试 DreamWaQ 策略性能的户外轨迹是使用安装在机器人上的 RTK-GPS 记录的。赛道 A 包含庭院中的许多非结构化自然地形，而赛道 B 则是一条徒步赛道。这两个赛道相对于起点的海拔高度（单位为 m）在彩色条中显示。

**1) Course A:** 在该赛道中，机器人在包含各种斜坡的非结构化自然轨迹中受到了挑战。机器人还遇到了可能会困住其腿部的厚密植被。然而，机器人通过增加关节动力克服了阻碍，并成功地调整了其速度。
该赛道中最具挑战性的部分是穿越楼梯和可变形斜坡。由于 DreamWaQ 策略的鲁棒性和估计的准确性，机器人可以安全地穿过楼梯和斜坡。
我们不仅在干燥的条件下，而且在降雨后潮湿的地形中也进行了实验。在下楼梯时，机器人面临着湿滑的楼梯。此外，由于泥土，机器人的脚在斜坡上陷得更深。尽管如此，由 DreamWaQ 控制的我们的机器人毫无困难地穿过了潮湿的地形。

**2) Course B:** 赛道 B 挑战了机器人爬上一座中等高度的山丘。这条徒步轨迹包含人造柏油地形、碎石和斜坡。实验在夏季进行，电机很快发热。因此，为了减少所需的力矩，我们命令机器人缓慢移动。由于攀爬操作，前腿电机容易过热并进入过热保护模式。尽管如此，使用 DreamWaQ，我们的机器人能够爬上山丘，在 10 分钟内完成了一条 465 米的轨迹，并到达山顶。

# IV. Conclusion
在这项工作中，我们介绍了 DreamWaQ，这是一个鲁棒的四足运动框架，该框架使得四足机器人可以仅依靠本体感觉穿越非结构化地形。与现有的基于学习的控制器相比，DreamWaQ 表现出了改进的性能，并在一台在山丘和非结构化庭院行走了约十分钟的 Unitree A1 机器人上展示了其鲁棒性。DreamWaQ 的局限性在于其自适应机制，即它必须首先用腿触碰障碍物。应对更复杂的结构，比如高楼梯，是我们未来工作的一部分，这需要将外部感受融入运动系统，以便在接触障碍物之前进行改进的步态规划。
<!-- PAGE 6 END -->
""",
"""
# References
[1] M. Hutter, C. Gehring, D. Jud, A. Lauber, C. D. Bellicoso, V. Tsounis, J. Hwangbo, K. Bodie, P. Fankhauser, M. Bloesch, et al., “ANYmal – A highly mobile and dynamic quadrupedal robot,” in Proc. IEEE/RSJ international Conference on Intelligent Robots and Systems (IROS), 2016, pp. 38–44.
[2] B. Katz, J. Di Carlo, and S. Kim, “Mini cheetah: A platform for pushing the limits of dynamic quadruped control,” in Proc. IEEE International Conference on Robotics and Automation (ICRA), 2019, pp. 6295–6301.
[3] Y.-H. Shin, S. Hong, S. Woo, J. Choe, H. Son, G. Kim, J.-H. Kim, K. Lee, J. Hwangbo, and H.-W. Park, “Design of KAIST HOUND, a quadruped robot platform for fast and efficient locomotion with mixed-integer nonlinear optimization of a gear train,” in Proc. International Conference on Robotics and Automation (ICRA), 2022, pp. 6614–6620.
[4] C. Gehring, P. Fankhauser, L. Isler, R. Diethelm, S. Bachmann, M. Potz, L. Gerstenberg, and M. Hutter, “ANYmal in the field: Solving industrial inspection of an offshore HVDC platform with a quadrupedal robot,” in Field and Service Robotics, G. Ishigami and K. Yoshida, Eds. Singapore: Springer, 2021, ch. 16, pp. 247–260.
[5] M. Tranzatto, T. Miki, M. Dharmadhikari, L. Bernreiter, M. Kulkarni, F. Mascarich, O. Andersson, S. Khattak, M. Hutter, R. Siegwart, et al., “CERBERUS in the DARPA subterranean challenge,” Science Robotics, vol. 7, no. 66, p. eabp9742, 2022.
[6] E. M. Lee, D. Seo, J. Jeon, and H. Myung, “QR-SCAN: Traversable region scan for quadruped robot exploration using lightweight precomputed trajectory,” in Proc. 21st International Conference on Control, Automation and Systems (ICCAS), 2021, pp. 957–961.
[7] Y. Kim, B. Yu, E. M. Lee, J.-H. Kim, H.-W. Park, and H. Myung, “STEP: State estimator for legged robots using a preintegrated foot velocity factor,” IEEE Robotics and Automation Letters, vol. 7, no. 2, pp. 4456–4463, 2022.
[8] M. Bloesch, C. Gehring, P. Fankhauser, M. Hutter, M. A. Hoepflinger, and R. Siegwart, “State estimation for legged robots on unstable and slippery terrain,” in Proc. IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2013, pp. 6058–6064.
[9] C. Gehring, C. D. Bellicoso, P. Fankhauser, S. Coros, and M. Hutter, “Quadrupedal locomotion using trajectory optimization and hierarchical whole body control,” in Proc. IEEE International Conference on Robotics and Automation (ICRA), 2017, pp. 4788–4794.
[10] C. D. Bellicoso, F. Jenelten, P. Fankhauser, C. Gehring, J. Hwangbo, and M. Hutter, “Dynamic locomotion and whole-body control for quadrupedal robots,” in Proc. IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2017, pp. 3359–3365.
[11] F. Jenelten, R. Grandia, F. Farshidian, and M. Hutter, “TAMOLS: Terrain-aware motion optimization for legged systems,” IEEE Transactions on Robotics, 2022, doi: 10.1109/TRO.2022.3186804.
[12] N. Rudin, D. Hoeller, P. Reist, and M. Hutter, “Learning to walk in minutes using massively parallel deep reinforcement learning,” in Proc. Conference on Robot Learning (CoRL), 2022, pp. 91–100.
[13] T. Miki, J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, “Learning robust perceptive locomotion for quadrupedal robots in the wild,” Science Robotics, vol. 7, no. 62, p. eabk2822, 2022.
[14] Z. Fu, A. Kumar, A. Agarwal, H. Qi, J. Malik, and D. Pathak, “Coupling vision and proprioception for navigation of legged robots,” in Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, pp. 17273–17283.
[15] W. Yu, D. Jain, A. Escontrela, A. Iscen, P. Xu, E. Coumans, S. Ha, J. Tan, and T. Zhang, “Visual-locomotion: Learning to walk on complex terrains with vision,” in Proc. Conference on Robot Learning (CoRL), 2021, pp. 1291–1302.
[16] H. Lim, M. Oh, and H. Myung, “Patchwork: concentric zone-based region-wise ground segmentation with ground likelihood estimation using a 3D LiDAR sensor,” IEEE Robotics and Automation Letters, vol. 6, no. 4, pp. 6458–6465, 2021.
[17] M. Oh, E. Jung, H. Lim, W. Song, S. Hu, E. M. Lee, J. Park, J. Kim, J. Lee, and H. Myung, “TRAVEL: Traversable ground and aboveground object segmentation using graph representation of 3D LiDAR scans,” IEEE Robotics and Automation Letters, vol. 7, no. 3, pp. 7255–7262, 2022.
[18] S. Lee, H. Lim, and H. Myung, “Patchwork++: Fast and robust ground segmentation solving partial under-segmentation using 3D point cloud,” arXiv:2207.11919, 2022.
[19] J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, “Learning quadrupedal locomotion over challenging terrain,” Science Robotics, vol. 5, no. 47, p. eabc5986, 2020.
[20] A. Kumar, Z. Fu, D. Pathak, and J. Malik, “RMA: Rapid motor adaptation for legged robots,” in Proc. Robotics: Science and Systems, 2021.
[21] Z. Fu, A. Kumar, J. Malik, and D. Pathak, “Minimizing energy consumption leads to the emergence of gaits in legged robots,” in Proc. Conference on Robot Learning (CoRL), 2021, pp. 928–937.
[22] A. Escontrela, X. B. Peng, W. Yu, T. Zhang, A. Iscen, K. Goldberg, and P. Abbeel, “Adversarial motion priors make good substitutes for complex reward functions,” arXiv:2203.15103, 2022.
[23] G. B. Margolis, G. Yang, K. Paigwar, T. Chen, and P. Agrawal, “Rapid locomotion via reinforcement learning,” in Proc. Robotics: Science and Systems, 2022.
[24] G. Ji, J. Mun, H. Kim, and J. Hwangbo, “Concurrent training of a control policy and a state estimator for dynamic and robust legged locomotion,” IEEE Robotics and Automation Letters, vol. 7, no. 2, pp. 4630–4637, 2022.
[25] A. Zhang, R. McAllister, R. Calandra, Y. Gal, and S. Levine, “Learning invariant representations for reinforcement learning without reconstruction,” in Proc. International Conference on Learning Representations (ICLR), 2021.
[26] “Unitree A1,” accessed on 2022.08.24. [Online]. Available: https://m.unitree.com/products/a1
[27] D. Chen, B. Zhou, V. Koltun, and P. Krähenbühl, “Learning by cheating,” in Proc. Conference on Robot Learning (CoRL), 2020, pp. 66–75.
[28] L. Pinto, M. Andrychowicz, P. Welinder, W. Zaremba, and P. Abbeel, “Asymmetric actor critic for image-based robot learning,” in Proc. Robotics: Science and Systems, 2018.
[29] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, “Proximal policy optimization algorithms,” arXiv:1707.06347, 2017.
[30] J. Hwangbo, J. Lee, A. Dosovitskiy, D. Bellicoso, V. Tsounis, V. Koltun, and M. Hutter, “Learning agile and dynamic motor skills for legged robots,” Science Robotics, vol. 4, no. 26, p. eaau5872, 2019.
[31] D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” arXiv:1312.6114, 2013.
[32] I. Higgins, L. Matthey, A. Pal, C. Burgess, X. Glorot, M. Botvinick, S. Mohamed, and A. Lerchner, “β–VAE: Learning basic visual concepts with a constrained variational framework,” in Proc. International Conference on Learning Representations (ICLR), 2017.
[33] C. P. Burgess, I. Higgins, A. Pal, L. Matthey, N. Watters, G. Desjardins, and A. Lerchner, “Understanding disentangling in β–VAE,” Advances in Neural Information Processing (NeurIPS) Workshop on Learning Disentangled Representations, 2017.
[34] S. Kullback and R. A. Leibler, “On information and sufficiency,” The Annals of Mathematical Statistics, vol. 22, no. 1, pp. 79–86, 1951.
[35] D.-A. Clevert, T. Unterthiner, and S. Hochreiter, “Fast and accurate deep network learning by exponential linear units (ELUs),” in Proc. International Conference on Learning Representations (ICLR), 2016.
[36] V. Makoviychuk, L. Wawrzyniak, Y. Guo, M. Lu, K. Storey, M. Macklin, D. Hoeller, N. Rudin, A. Allshire, A. Handa, et al., “Isaac Gym: High performance GPU-based physics simulation for robot learning,” Advances in Neural Information Processing Systems, Track on Datasets and Benchmarks, 2021.
[37] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,” in Proc. International Conference on Learning Representations (ICLR), 2015.
[38] X. B. Peng, E. Coumans, T. Zhang, T.-W. E. Lee, J. Tan, and S. Levine, “Learning agile robotic locomotion skills by imitating animals,” in Robotics: Science and Systems, 07 2020.
[39] “H-RTK F9P Helical GPS,” accessed on 2022.09.02. [Online]. Available: http://www.holybro.com/product/h-rtk-f9p/
"""
]

file_path = r"c:\Users\Administrator.DESKTOP-VDO7G6M\Desktop\paper_read\papers\translation\DreamWaq：Learning Robust Quadrupedal Locomotion With Implict Terrain Imagination via Deep Reinforcement Learning_translated.md"

with open(file_path, 'a', encoding='utf-8') as f:
    for text in sections:
        f.write(text + "\\n")
