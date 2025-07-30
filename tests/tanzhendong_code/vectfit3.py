#comment: 导入 NumPy 库，并创建一个别名 np，用于处理数组和矩阵运算。
import numpy as np
#comment: 为 np.newaxis 创建一个更短的别名 nax，用于在数组操作中增加维度。
nax = np.newaxis

#comment: 定义了一个名为 vectfit3 的函数，它实现了快速松弛向量拟合算法。
#comment: f: 待拟合的频率响应函数（或向量），维度为 (Nc, Ns)，其中 Nc 是向量元素的数量，Ns 是频率样本的数量。
#comment: s: 频率点向量 [rad/sec]，维度为 (Ns)。
#comment: poles: 初始极点向量 [rad/sec]，维度为 (N)。
#comment: weight: 用于加权系统矩阵行的数组，维度可以是 (1, Ns) 或 (Nc, Ns)。
#comment: opts: 包含拟合选项的字典，默认为 None。
def vectfit3(f, s, poles, weight, opts=None):
	'''===========================================================
	   =   Fast Relaxed Vector Fitting                           =
	   =   Version 1.0                                           =
	   =   Last revised: 08.08.2008                              =
	   =   Written by: Bjorn Gustavsen                           =
	   =   SINTEF Energy Research, N-7465 Trondheim, NORWAY      =
	   =   bjorn.gustavsen@sintef.no                             =
	   =   http://www.energy.sintef.no/Produkt/VECTFIT/index.asp =
	   =   Note: RESTRICTED to NON-COMMERCIAL use                =
	   =   Translated to python by Simon De Ridder               =
	   ===========================================================
	PURPOSE: Approximate f(s) with a state-space model
	             f(s)=C*(s*I-A)^(-1)*B +D +s*E
	         where f(s) is a singe element or a vector of elements.
	         When f(s) is a vector, all elements become fitted with a common pole set.

	INPUT:
	f(s): function (vector) to be fitted.
	      dimension : (Nc,Ns)
	          Nc: number of elements in vector
	          Ns: number of frequency samples

	s: vector of frequency points [rad/sec]
	       dimension : (Ns)

	poles: vector of initial poles [rad/sec]
	       dimension : (N)

	weight: the rows in the system matrix are weighted using this array. Can be used  for achieving
	        higher accuracy at desired frequency samples.
	        If no weighting is desired, use unitary weights: weight=np.ones((1,Ns)).
	        Two dimensions are allowed:
	            dimension : (1,Ns) --> Common weighting for all vector elements.
	            dimension : (Nc,Ns)--> Individual weighting for vector elements.

	opts: dict containing fit options:
		opts['relax']: True:  Use relaxed nontriviality constraint
		               False: Use nontriviality constraint of "standard" vector fitting

		opts['stable']: True:  unstable poles are kept unchanged
		                False: unstable poles are made stable by 'flipping' them into the left
		                       half-plane

		opts['asymp']: 0: Fitting with D=0,  E=0
		               1: Fitting with D!=0, E=0
		               2: Fitting with D!=0, E~=0

		opts['skip_pole']: True: The pole identification part is skipped, i.e (C,D,E)  are
		                         identified using the initial poles (A) as final poles.

		opts['skip_res']: True: The residue identification part is skipped, i.e. only the poles (A)
		                        are identified while C,D,E are returned as zero.

		opts['cmplx_ss']: True:  The returned state-space model has real and complex conjugate
		                         parameters. Output variable A is diagonal (and sparse). 
		                  False: The returned state-space model has real parameters only. Output
		                         variable A is square with 2x2 blocks (and sparse).

		opts['spy1']: True: Plotting, after pole identification (A)
		                    magnitude functions
		                    cyan trace:  (sigma*f)fit
		                    red trace:   (sigma)fit
		                    green trace: f*(sigma)fit - (sigma*f)fit

		opts['spy2']: True: Plotting, after residue identification (C,D,E)
		                    1) magnitude functions
		                    2) phase angles

		opts['logx']: True: Plotting using logarithmic absissa axis

		opts['logy']: True: Plotting using logarithmic ordinate axis

		opts['errplot']: True: Include deviation in magnitude plot

		opts['phaseplot']: True: Show plot also for phase angle

		opts['legend']: True: Include legend in plots

		opts['block']: True: Block on plots (must be closed before computation continues)

	OUTPUT :

		fit(s) = C*(s*I-A)^(-1)*B + D + s*E

	SER['A'] (N,N): A-matrix (sparse). If opts['cmplx_ss']==True: Diagonal and complex. Otherwise,
	                square and real with 2x2 blocks.
	SER['B'] (N): B-matrix. If opts['cmplx_ss']==True:  Column of 1's. 
	                        If opts['cmplx_ss']==False: contains 0's, 1's and 2's
	SER['C'] (Nc,N): C-matrix. If opts['cmplx_ss']==True:  complex
	                           If opts['cmplx_ss']==False: real-only
	SER['D'] (Nc): constant term (real). Is not None if opts['asymp']==1 or 2.
	SER['E'] (Nc): proportional term (real). Is not None if opts['asymp']==2.

	poles (N): new poles

	rmserr (1): root-mean-square error of approximation for f(s).
	            (0 is returned if opts['skip_res']==True)

	fit(Nc,Ns): Rational approximation at samples. (None is returned if opts['skip_res']==True).

	APPROACH:
	The identification is done using the pole relocating method known as Vector Fitting [1],
	with relaxed non-triviality constraint for faster convergence and smaller fitting errors [2],
	and utilization of matrix structure for fast solution of the pole identifion step [3].

	***********************************************************************************************
	NOTE: The use of this program is limited to NON-COMMERCIAL usage only.
	If the program code (or a modified version) is used in a scientific work,
	then reference should be made to the following

	[1] B. Gustavsen and A. Semlyen, "Rational approximation of frequency domain responses by
	    Vector Fitting", IEEE Trans. Power Delivery, vol. 14, no. 3, pp. 1052-1061, July 1999.

	[2] B. Gustavsen, "Improving the pole relocating properties of vector fitting",
	    IEEE Trans. Power Delivery, vol. 21, no. 3, pp. 1587-1592, July 2006.

	[3] D. Deschrijver, M. Mrozowski, T. Dhaene, and D. De Zutter, "Macromodeling of Multiport
	    Systems Using a Fast Implementation of the Vector Fitting Method",
	    IEEE Microwave and Wireless Components Letters, vol. 18, no. 6, pp. 383-385, June 2008.
	***********************************************************************************************
	Last revised: 08.08.2008.
	Created by:   Bjorn Gustavsen.
	Translated by: Simon De Ridder                                                              '''

	#comment: 定义一个字典 options，用于存储算法的默认配置选项。
	options = {}
	#comment: relaxed non-triviality constraint，启用松弛非平凡性约束。
	options['relax']     = True
	#comment: Enforce stable poles，强制极点稳定。
	options['stable']    = True
	#comment: Include only D in fitting (not E)，拟合中只包含 D 项（不包含 E 项）。
	options['asymp']     = 1
	#comment: Do NOT skip pole identification，不跳过极点识别部分。
	options['skip_pole'] = False
	#comment: Do NOT skip identification of residues (C,D,E)，不跳过残差 (C, D, E) 识别部分。
	options['skip_res']  = False
	#comment: Create complex state space model，创建复数状态空间模型。
	options['cmplx_ss']  = True
	#comment: No plotting for first stage of vector fitting，在向量拟合的第一阶段不进行绘图。
	options['spy1']      = False
	#comment: Do NOT Create magnitude plot for fitting of f(s)，不为 f(s) 的拟合创建幅值图。
	options['spy2']      = False
	#comment: Use logarithmic abscissa axis，使用对数横坐标轴。
	options['logx']      = True
	#comment: Use logarithmic ordinate axis，使用对数纵坐标轴。
	options['logy']      = True
	#comment: Include deviation in magnitude plot，在幅值图中包含偏差。
	options['errplot']   = True
	#comment: exclude plot of phase angle (in addition to magnitiude)，排除相位角图（除了幅值图）。
	options['phaseplot'] = False
	#comment: Do include legends in plots，在图中包含图例。
	options['legend']    = True
	#comment: Do NOT block on plots，绘图时不阻塞。
	options['block']     = False
	#comment: 如果 opts 参数不为空，即用户提供了自定义选项，则使用 update 方法将这些选项合并到默认的 options 字典中。
	if not opts is None:
		#comment: 将用户定义的选项更新到默认选项字典中。
		options.update(opts);

	#comment: 定义用于松弛向量拟合的下限容差值。
	TOLlow  = 1e-18
	#comment: 定义用于松弛向量拟合的上限容差值。
	TOLhigh = 1e18

	#comment: 检查 options['relax'] 是否是一个标量布尔值。
	if (not np.isscalar(options['relax'])) or (not isinstance(options['relax'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['relax'] must be a scalar boolean")
	#comment: 检查 options['stable'] 是否是一个标量布尔值。
	if (not np.isscalar(options['stable'])) or (not isinstance(options['stable'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['stable'] must be a scalar boolean")
	#comment: 检查 options['asymp'] 是否是一个标量整数。
	if (not np.isscalar(options['asymp'])) or (not isinstance(options['asymp'], int)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['asymp'] must be a scalar integer")
	#comment: 检查 options['asymp'] 的值是否在 0、1 或 2 的范围内。
	if options['asymp']<0 or options['asymp']>2:
		#comment: 如果不在有效范围内，则抛出 ValueError。
		raise ValueError("options['asymp'] must be 0, 1 or 2, not "+str(options['asymp']))
	#comment: 检查 options['skip_pole'] 是否是一个标量布尔值。
	if (not np.isscalar(options['skip_pole'])) or (not isinstance(options['skip_pole'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['skip_pole'] must be a scalar boolean")
	#comment: 检查 options['skip_res] 是否是一个标量布尔值。
	if (not np.isscalar(options['skip_res'])) or (not isinstance(options['skip_res'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['skip_res] must be a scalar boolean")
	#comment: 检查 options['cmplx_ss'] 是否是一个标量布尔值。
	if (not np.isscalar(options['cmplx_ss'])) or (not isinstance(options['cmplx_ss'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['cmplx_ss'] must be a scalar boolean")
	#comment: 检查 options['spy1'] 是否是一个标量布尔值。
	if (not np.isscalar(options['spy1'])) or (not isinstance(options['spy1'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['spy1'] must be a scalar boolean")
	#comment: 检查 options['spy2'] 是否是一个标量布尔值。
	if (not np.isscalar(options['spy2'])) or (not isinstance(options['spy2'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['spy2'] must be a scalar boolean")
	#comment: 检查 options['logx'] 是否是一个标量布尔值。
	if (not np.isscalar(options['logx'])) or (not isinstance(options['logx'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['logx'] must be a scalar boolean")
	#comment: 检查 options['logy'] 是否是一个标量布尔值。
	if (not np.isscalar(options['logy'])) or (not isinstance(options['logy'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['logy'] must be a scalar boolean")
	#comment: 检查 options['errplot'] 是否是一个标量布尔值。
	if (not np.isscalar(options['errplot'])) or (not isinstance(options['errplot'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['errplot'] must be a scalar boolean")
	#comment: 检查 options['phaseplot'] 是否是一个标量布尔值。
	if (not np.isscalar(options['phaseplot'])) or (not isinstance(options['phaseplot'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['phaseplot'] must be a scalar boolean")
	#comment: 检查 options['legend'] 是否是一个标量布尔值。
	if (not np.isscalar(options['legend'])) or (not isinstance(options['legend'], bool)):
		#comment: 如果不是，则抛出 TypeError。
		raise TypeError("options['legend'] must be a scalar boolean")

	#comment: 检查输入参数 s 是否为 NumPy 数组且维度不超过1 (即一维或零维)。
	if (not isinstance(s, np.ndarray)) or len(s.shape)>1:
		#comment: 如果不满足条件，则抛出 TypeError 异常。
		raise TypeError('s must be a one-dimensional numpy ndarray')
	#comment: 获取 s 数组的长度（频率样本的数量），并存储在变量 Ns 中。
	Ns = s.shape[0]

	#comment: 检查输入参数 f 是否为 NumPy 数组且维度为2。
	if (not isinstance(f, np.ndarray)) or len(f.shape)!=2:
		#comment: 如果不满足条件，则抛出 TypeError 异常。
		raise TypeError('f must be a two-dimensional numpy ndarray')
	#comment: 检查 f 数组的第二维度（频率样本数）是否与 Ns (由 s 确定) 匹配。
	if f.shape[1] != Ns:
		#comment: 如果不匹配，则抛出 ValueError 异常。
		raise ValueError('Second dimension of f does not match length of s')
	#comment: 获取 f 数组的第一维度（向量元素的数量），并存储在变量 Nc 中。
	Nc = f.shape[0]

	#comment: 检查输入参数 poles 是否为 NumPy 数组且维度为1。
	if (not isinstance(poles, np.ndarray)) or len(poles.shape)>1:
		#comment: 如果不满足条件，则抛出 TypeError 异常。
		raise TypeError('poles must be a one-dimensional numpy ndarray')
	#comment: 检查如果 s 的第一个元素为0。由于s[0]=0可能导致后续计算中的不确定性（例如除以零），这里进行特殊处理。
	if s[0]==0:
		#comment: 如果poles[0]和poles[1]中只有一个是0，则将为0的那个极点设为-1。
		if poles[0]==0 and poles[1]!=0:
			poles[0] = -1
		elif poles[1]==0 and poles[0]!=0:
			poles[1] = -1
		#comment: 如果poles[0]和poles[1]都是0，则将它们设置为一对复共轭极点，避免不确定性。
		elif poles[0]==0 and poles[1]==0:
			poles[0] = -1 + 1j*10
			poles[1] = -1 - 1j*10
	#comment: 获取极点的数量N。
	N = poles.shape[0]

	#comment: 检查输入参数 weight 是否为 NumPy 数组且维度为2。
	if (not isinstance(weight, np.ndarray)) or len(weight.shape)!=2:
		#comment: 如果不满足条件，则抛出 TypeError 异常。
		raise TypeError('weight must be a two-dimensional numpy ndarray')
	#comment: 检查 weight 数组的第一维度是否为 1 或者与 Nc (f 的第一维度) 匹配。
	if weight.shape[0] != 1 and weight.shape[0] !=Nc:
		#comment: 如果不匹配，则抛出 ValueError 异常。
		raise ValueError('First dimension of weight is neither 1 nor matches first dimension of f.')
	#comment: 检查 weight 数组的第二维度是否与 Ns (s 的长度) 匹配。
	if weight.shape[1] != Ns:
		#comment: 如果不匹配，则抛出 ValueError 异常。
		raise ValueError('Second dimension of weight does not match length of s.')
	#comment: 判断权重是否是公共的 (即所有向量元素使用相同的权重)。如果是，则 common_weight 为 True，否则为 False。
	common_weight = (weight.shape[0] == 1)

	#comment: 根据绘图选项是否启用，决定是否导入 matplotlib.pyplot。
	if ((not options['skip_pole']) and options['spy1']) or\
	   ((not options['skip_res'])  and options['spy2']):
		#comment: 导入 matplotlib.pyplot 模块，并通常约定使用别名 plt。
		import matplotlib.pyplot as plt

	#comment: 初始化一个 NumPy 数组 cindex，维度为 (N)，数据类型为整数。
	#comment: 这个数组将用于标记极点是否是复共轭对的一部分 (cindex[m]=1表示复共轭对的第一个极点，cindex[m]=2表示第二个)。
	cindex = np.zeros((N), dtype=np.int_)
	#comment: 初始化一个计数器 m，用于遍历极点。
	m = 0
	#comment: 循环遍历所有极点，直到 m 达到 N。
	while m < N:
		#comment: 检查当前极点 poles[m] 的虚部是否不为零。不为零说明是复数极点。
		if poles[m].imag != 0:
			#comment: 如果当前极点是复数，则它应该与下一个极点构成一对复共轭极点。
			#comment: 这里检查 poles[m].real 是否与 poles[m+1].real 相等，以及 poles[m].imag 是否与 -poles[m+1].imag 相等。
			if poles[m].real!=poles[m+1].real or poles[m].imag!=-poles[m+1].imag:
				#comment: 如果不满足复共轭条件，则抛出 ValueError 异常，指示相邻极点不是复共轭对。
				raise ValueError('Initial poles '+str(m)+' and '+str(m+1)\
				                 +' are subsequent but not complex conjugate.')
			#comment: 如果满足复共轭条件，则将 poles[m] 的 cindex 标记为 1 (表示复共轭对的第一个)。
			cindex[m]   = 1
			#comment: 将 poles[m+1] 的 cindex 标记为 2 (表示复共轭对的第二个)。
			cindex[m+1] = 2
			#comment: 由于处理了一对极点，将 m 增加 1，跳过下一个极点。
			m += 1
		#comment: 无论当前极点是否为复数，都将 m 增加 1，以便处理下一个极点。
		m += 1


	#comment: 极点重新定位阶段
	#==========================
	#=    POLE RELOCATION:    =
	#==========================

	#comment: 检查是否需要跳过极点识别阶段。如果 options['skip_pole'] 为 False，则执行以下极点识别逻辑。
	if not options['skip_pole']:
		#comment: 构造系统矩阵 Dk。
		#comment: 初始化一个 NumPy 数组 Dk，维度为 (Ns, N + max(1, options['asymp']))，数据类型为复数。
		#comment: Ns 是频率样本数，N 是极点数。max(1, options['asymp']) 考虑了渐近项 D 和 E 可能对列数的影响。
		Dk = np.empty((Ns,N+max(1, options['asymp'])), dtype=np.complex_)
		#comment: 循环遍历每个极点。
		for m in range(N):
			#comment: 对于实数极点 (cindex[m] == 0)。
			if cindex[m]==0: # real pole
				#comment: 对应的 Dk 列为 1 / (s - poles[m])。
				Dk[:,m] = 1 / (s-poles[m])
			#comment: 对于复数共轭极点对的第一个极点 (cindex[m] == 1)。
			elif cindex[m]==1: # complex pole pair, 1st part
				#comment: 对应的 Dk 列为 1/(s - poles[m]) + 1/(s - conj(poles[m]))。
				Dk[:,m]   =  1/(s-poles[m]) +  1/(s-np.conj(poles[m]))
				#comment: 处理复数共轭极点对的第二个极点，对应的 Dk 列为 1j/(s - poles[m]) - 1j/(s - conj(poles[m]))。
				Dk[:,m+1] = 1j/(s-poles[m]) - 1j/(s-np.conj(poles[m]))
		#comment: 将 Dk 的第 N 列设置为全 1，这对应于常数项 D。
		Dk[:,N] = 1
		#comment: 如果 options['asymp'] 为 2 (即包含 E 项)。
		if options['asymp']==2:
			#comment: 将 Dk 的第 N+1 列设置为 s，这对应于线性项 E。
			Dk[:,N+1] = s

		#comment: 如果启用松弛向量拟合 (options['relax'] 为 True)。
		if options['relax']: # relaxed VF
			#comment: 计算用于松弛向量拟合极点识别的最小二乘问题中最后一行的缩放因子。
			scale=0
			#comment: 遍历每个元素 (Nc)。
			for n in range(Nc):
				#comment: 如果使用共同权重。
				if common_weight:
					#comment: 计算权重与 f[n,:] 乘积的 L2 范数的平方加到 scale 中。
					scale += np.linalg.norm(weight[0,:]*f[n,:])**2
				#comment: 如果使用独立权重。
				else:
					#comment: 计算权重与 f[n,:] 乘积的 L2 范数的平方加到 scale 中。
					scale += np.linalg.norm(weight[n,:]*f[n,:])**2
			#comment: 将 scale 开平方并除以 Ns，得到最终的缩放因子。
			scale = np.sqrt(scale) / Ns

			#comment: 构建线性系统矩阵。
			#comment: 初始化 AA 矩阵，用于存储每个元素的部分解。
			AA = np.empty((Nc*(N+1),N+1))
			#comment: 初始化 bb 向量，用于存储每个元素的部分解的右侧。
			bb = np.zeros((Nc*(N+1)))
			#comment: 计算左块的列数。
			Nleft = N + options['asymp']
			#comment: 计算总列数。
			Ntot  = Nleft + N + 1
			#comment: 遍历每个元素 n。
			for n in range(Nc):
				#comment: 如果是最后一个元素 (n == Nc-1)。
				if n==Nc-1:
					#comment: A 矩阵的行数会增加 1，用于包含积分准则。
					A = np.zeros((2*Ns+1,Ntot))
				#comment: 如果不是最后一个元素。
				else:
					#comment: A 矩阵的行数为 2*Ns。
					A = np.empty((2*Ns,Ntot))
				#comment: 如果使用共同权重。
				if common_weight:
					#comment: 获取权重并增加一个维度使其可广播。
					weig = weight[0,:,nax]
				#comment: 如果使用独立权重。
				else:
					#comment: 获取权重并增加一个维度使其可广播。
					weig = weight[n,:,nax]
				#comment: 填充 A 矩阵的左块（实部）。
				A[:Ns,    :Nleft] =  weig * Dk[:,:Nleft].real
				#comment: 填充 A 矩阵的左块（虚部）。
				A[Ns:2*Ns,:Nleft] =  weig * Dk[:,:Nleft].imag
				#comment: 填充 A 矩阵的右块（实部），包含 f[n,:] 的贡献。
				A[:Ns,    Nleft:] = -weig * (Dk[:,:N+1] * f[n,:,nax]).real
				#comment: 填充 A 矩阵的右块（虚部），包含 f[n,:] 的贡献。
				A[Ns:2*Ns,Nleft:] = -weig * (Dk[:,:N+1] * f[n,:,nax]).imag

				#comment: 针对 sigma 的积分准则 (非平凡性约束)。
				if n==Nc-1:
					#comment: 添加积分约束到 A 矩阵的最后一行。
					A[2*Ns,Nleft:] = scale * np.sum(Dk[:,:N+1].real, axis=0)

				#comment: 对当前元素的 A 矩阵进行 QR 分解，并将其结果添加到 AA 和 bb。
				#comment: 执行 QR 分解，mode='reduced' 表示返回精简形式的 Q 和 R。
				Q,R = np.linalg.qr(A, mode='reduced')
				#comment: 将 R 矩阵的相关部分赋值给 AA 矩阵的对应行。
				AA[n*(N+1):(n+1)*(N+1),:] = R[Nleft:Ntot,Nleft:Ntot]
				#comment: 如果是最后一个元素。
				if n==Nc-1:
					#comment: 设置 bb 向量的对应部分。
					bb[n*(N+1):(n+1)*(N+1)] = Q[-1,Nleft:] * Ns * scale
			#comment: 循环结束
			# end for n in range(Nc)

			#comment: 解决大型线性系统。
			#comment: 计算 AA 矩阵每列的 L2 范数，用于列缩放。
			Escale = np.linalg.norm(AA, axis=0)
			#comment: 对 AA 矩阵进行列缩放。
			AA /= Escale[nax,:]
			#comment: 使用最小二乘法求解 AAx = bb。
			x = np.linalg.lstsq(AA, bb, rcond=-1)[0]
			#comment: 将解向量 x 反向缩放。
			x /= Escale
		#comment: 结束 if options['relax']

		#comment: 如果没有启用松弛向量拟合，或者通过松弛向量拟合得到的 sigma 的 D 项极其小或极其大，则再次求解。
		#comment: 这种情况是当松弛向量拟合失效或结果不合理时，回退到非松弛或固定 D 的方法。
		if (not options['relax']) or np.abs(x[-1])<TOLlow or np.abs(x[-1])>TOLhigh:
			#comment: 如果没有启用松弛向量拟合，或者 Dnew 在容差范围外，则将 Dnew 设置为固定值。
			if not options['relax']:
				#comment: 如果不使用松弛，Dnew 设置为 1。
				Dnew = 1
			#comment: 如果使用了松弛但结果不理想。
			else:
				#comment: 如果 x 的最后一个元素为 0，Dnew 设置为 1。
				if x[-1]==0:
					Dnew = 1
				#comment: 如果 x 的最后一个元素的绝对值小于 TOLlow，Dnew 设置为符号乘以 TOLlow。
				elif np.abs(x[-1])<TOLlow:
					Dnew = np.sign(x[-1]) * TOLlow
				#comment: 如果 x 的最后一个元素的绝对值大于 TOLhigh，Dnew 设置为符号乘以 TOLhigh。
				elif np.abs(x[-1])>TOLhigh:
					Dnew = np.sign(x[-1]) * TOLhigh

			#comment: 构造线性系统矩阵。
			#comment: 初始化 AA 矩阵，用于存储每个元素的部分解。
			AA = np.empty((Nc*N,N))
			#comment: 初始化 bb 向量，用于存储每个元素的部分解的右侧。
			bb = np.empty((Nc*N))
			#comment: 计算左块的列数。
			Nleft = N + options['asymp']
			#comment: 计算总列数。
			Ntot = Nleft + N
			#comment: 遍历每个元素 n。
			for n in range(Nc):
				#comment: 初始化 A 矩阵，用于当前元素的求解。
				A = np.empty((2*Ns,Ntot))
				#comment: 初始化 b 向量，用于当前元素的右侧。
				b = np.empty((2*Ns))
				#comment: 如果使用共同权重。
				if common_weight:
					#comment: 获取共同权重。
					weig = weight[0,:]
				#comment: 如果使用独立权重。
				else:
					#comment: 获取当前元素的独立权重。
					weig = weight[n,:]
				#comment: 填充 A 矩阵的左块（实部），包含 Dk 的贡献。
				A[:Ns,:Nleft] =  weig[:,nax] * Dk[:,:Nleft].real
				#comment: 填充 A 矩阵的左块（虚部），包含 Dk 的贡献。
				A[Ns:,:Nleft] =  weig[:,nax] * Dk[:,:Nleft].imag
				#comment: 填充 A 矩阵的右块（实部），包含 Dk 和 f 的贡献。
				A[:Ns,Nleft:] = -weig[:,nax] * (Dk[:,:N] * f[n,:,nax]).real
				#comment: 填充 A 矩阵的右块（虚部），包含 Dk 和 f 的贡献。
				A[Ns:,Nleft:] = -weig[:,nax] * (Dk[:,:N] * f[n,:,nax]).imag
				#comment: 填充 b 向量的实部，包含固定 Dnew 和 f 的贡献。
				b[:Ns] = Dnew * weig * f[n,:].real
				#comment: 填充 b 向量的虚部，包含固定 Dnew 和 f 的贡献。
				b[Ns:] = Dnew * weig * f[n,:].imag

				#comment: 对当前元素的 A 矩阵进行 QR 分解，并将其结果添加到 AA 和 bb。
				#comment: 执行 QR 分解，mode='reduced' 表示返回精简形式的 Q 和 R。
				Q,R = np.linalg.qr(A, mode='reduced')
				#comment: 将 R 矩阵的相关部分赋值给 AA 矩阵的对应行。
				AA[n*N:(n+1)*N,:] = R[Nleft:Ntot,Nleft:Ntot]
				#comment: 设置 bb 向量的对应部分。
				bb[n*N:(n+1)*N]   = np.dot(Q[:,Nleft:Ntot].T, b)
			#comment: 循环结束
			# end for n in range(Nc)

			#comment: 解决大型线性系统。
			#comment: 计算 AA 矩阵每列的 L2 范数，用于列缩放。
			Escale = np.linalg.norm(AA, axis=0)
			#comment: 对 AA 矩阵进行列缩放。
			AA /= Escale[nax,:]
			#comment: 使用最小二乘法求解 AAx = bb。
			x = np.linalg.lstsq(AA, bb, rcond=-1)[0]
			#comment: 将解向量 x 反向缩放。
			x /= Escale
			#comment: 将 Dnew 添加到解向量 x 的末尾。
			x = np.append(x, Dnew)
		#comment: 结束 if (not options['relax']) or np.abs(x[-1])<TOLlow or np.abs(x[-1])>TOLhigh

		#comment: 如果选项中开启了 spy1 绘图。
		if options['spy1']:
			#comment: 将解向量 x 转换为复数残差并计算 sigma。
			#comment: 初始化一个 NumPy 数组 C，维度为 (N)，用于存储残差。
			C = np.empty((N))
			#comment: 遍历每个极点。
			for m in range(N):
				#comment: 如果是实数极点 (cindex[m] == 0)。
				if cindex[m]==0:
					#comment: 直接赋值。
					C[m] = x[m]
				#comment: 如果是复数共轭极点对的第一个极点 (cindex[m] == 1)。
				elif cindex[m]==1:
					#comment: 计算复数残差。
					C[m]   = x[m] + 1j*x[m+1]
					#comment: 计算其共轭残差。
					C[m+1] = x[m] - 1j*x[m+1]
			#comment: 计算 sigma 曲线的理性近似。
			sigma_rat = x[-1] + np.dot(1/(s[:,nax]-poles[nax,:]), C)
			#comment: 将角频率 s 的虚部转换为 Hz。
			freq = s.imag / (2*np.pi)
			#comment: 创建一个新的绘图窗口。
			plt.figure()
			#comment: 绘制 sigma 的幅值曲线。
			plt.plot(freq, np.abs(sigma_rat), 'b', label='sigma')
			#comment: 设置 x 轴的显示范围。
			plt.xlim(freq[0], freq[-1])
			#comment: 如果选项中开启了对数 x 轴。
			if options['logx']:
				#comment: 设置 x 轴为对数刻度。
				plt.xscale('log')
			#comment: 如果选项中开启了对数 y 轴。
			if options['logy']:
				#comment: 设置 y 轴为对数刻度。
				plt.yscale('log')
			#comment: 设置 x 轴标签。
			plt.xlabel('Frequency [Hz]')
			#comment: 设置 y 轴标签。
			plt.ylabel('Magnitude')
			#comment: 设置图表标题。
			plt.title('Sigma')
			#comment: 如果选项中开启了图例。
			if options['legend']:
				#comment: 显示图例，并放置在最佳位置。
				plt.legend(loc='best')
			#comment: 如果选项中开启了阻塞显示。
			if options['block']:
				#comment: 显示图表并阻塞程序执行，直到图表关闭。
				plt.show()
			#comment: 如果没有开启阻塞显示。
			else:
				#comment: 绘制图表而不阻塞程序执行。
				plt.draw()

		#comment: 构建 sigma 的状态空间模型。
		#comment: 初始化 LAMBD 矩阵 (对角矩阵)，用于存储极点。
		LAMBD = np.zeros((N,N))
		#comment: 初始化 B 向量，用于状态空间模型。
		B = np.ones((N,1))
		#comment: 遍历每个极点。
		for m in range(N):
			#comment: 如果是实数极点 (cindex[m] == 0)。
			if cindex[m]==0:
				#comment: 将实数极点直接放置在 LAMBD 的对角线上。
				LAMBD[m,m] = poles[m].real
			#comment: 如果是复数共轭极点对的第一个极点 (cindex[m] == 1)。
			elif cindex[m]==1:
				#comment: 构建 2x2 块矩阵来表示复数共轭极点。
				LAMBD[m+1,m ]  =-poles[m].imag
				LAMBD[m,  m+1] = poles[m].imag
				LAMBD[m,  m]   = poles[m].real
				LAMBD[m+1,m+1] = poles[m].real
				#comment: 调整 B 向量中与复数共轭极点相关的分量。
				B[m,0]   = 2
				B[m+1,0] = 0
		#comment: C 向量取 x 的前 N 个元素 (作为行向量)。
		C = x[nax,:-1]
		#comment: D 项取 x 的最后一个元素。
		D = x[-1]

		#comment: 计算 sigma 的零点 (即新的极点)。通过求解 (LAMBD - B*C/D) 的特征值得到。
		newPoles = np.linalg.eigvals(LAMBD-B*C/D)
		#comment: 如果选项中开启了强制稳定极点。
		if options['stable']:
			#comment: 识别所有实部大于 0 的不稳定极点。
			unstables = (newPoles.real>0)
			#comment: 将不稳定极点“翻转”到左半平面，通过减去其实部的两倍来实现。
			newPoles[unstables] -= 2 * newPoles[unstables].real

		#comment: 对新的极点进行排序，实数极点在前，然后是复共轭对 (正虚部在先)。
		#comment: 使用 lexsort 进行多键排序: 首先按虚部的负值排序 (使正虚部在前)，然后按实部的绝对值排序，最后按虚部的绝对值排序。
		sortInd = np.lexsort((-newPoles.imag, np.abs(newPoles.real), np.abs(newPoles.imag)))
		#comment: 根据排序索引重新排列 newPoles。
		newPoles = newPoles[sortInd]

		#comment: 更新 poles 为新计算出的极点。
		poles = newPoles

		#comment: 找出新的极点中哪些是复共轭对。
		#comment: 初始化 cindex 数组。
		cindex = np.zeros((N), dtype=np.int_)
		#comment: 初始化循环计数器。
		m = 0
		#comment: 循环遍历新的极点。
		while m < N:
			#comment: 如果当前极点有虚部。
			if poles[m].imag != 0:
				#comment: 检查当前极点和下一个极点是否构成复共轭对。
				if poles[m].real!=poles[m+1].real or poles[m].imag!=-poles[m+1].imag:
					#comment: 如果不构成，则抛出 ValueError。
					raise ValueError('Initial poles '+str(m)+' and '+str(m+1)\
					                 +' are subsequent but not complex conjugate.')
				#comment: 标记为复共轭对的第一个。
				cindex[m]   = 1
				#comment: 标记为复共轭对的第二个。
				cindex[m+1] = 2
				#comment: 跳过下一个极点，因为已处理。
				m += 1
			#comment: 移动到下一个极点。
			m += 1
	#comment: 结束 if not options['skip_pole']

	# comment: 残差识别阶段
	# =================================
	# = RESIDUE IDENTIFICATION: =
	# =================================

	# comment: 初始化一个空字典 SER，用于存储状态空间模型参数。
	SER = {}
	# comment: 初始化 SER['C'] 为 None。
	SER['C'] = None
	# comment: 初始化 SER['D'] 为 None。
	SER['D'] = None
	# comment: 初始化 SER['E'] 为 None。
	SER['E'] = None
	# comment: 初始化拟合结果 fit 为 None。
	fit = None
	# comment: 初始化均方根误差 rmserr 为 0。
	rmserr = 0
	# comment: 如果不跳过残差识别阶段 (options['skip_res'] 为 False)。
	if not options['skip_res']:
		# comment: 构造系统矩阵 Dk。
		# comment: 初始化 Dk 矩阵，其列数为极点数 N 加上渐近项的数量 (由 options['asymp'] 决定)。
		Dk=np.empty((Ns,N+options['asymp']), dtype=np.complex_)
		# comment: 遍历每个极点。
		for m in range(N):
			# comment: 如果是实数极点。
			if cindex[m]==0: # real pole
				# comment: 对应的 Dk 列为 1 / (s - poles[m])。
				Dk[:,m] = 1 / (s-poles[m])
			# comment: 如果是复数共轭极点对的第一个极点。
			elif cindex[m]==1: # complex pole pair, 1st part
				# comment: 处理复数共轭极点对的第一个极点。
				Dk[:,m]   =  1/(s-poles[m]) +  1/(s-np.conj(poles[m]))
				# comment: 处理复数共轭极点对的第二个极点。
				Dk[:,m+1] = 1j/(s-poles[m]) - 1j/(s-np.conj(poles[m]))
		# comment: 如果存在渐近项 (options['asymp'] > 0)。
		if options['asymp']>0:
			# comment: 将 Dk 的第 N 列设置为全 1，对应于常数项 D。
			Dk[:,N] = 1
			# comment: 如果存在线性渐近项 (options['asymp'] == 2)。
			if options['asymp']==2:
				# comment: 将 Dk 的第 N+1 列设置为 s，对应于线性项 E。
				Dk[:,N+1] = s

		# comment: 初始化 A 矩阵，用于构建线性系统。其行数为 2*Ns (实部和虚部)，列数为 N + options['asymp']。
		A = np.zeros((2*Ns,N+options['asymp']))
		# comment: 如果使用共同权重。
		if common_weight:
			# comment: 填充 A 矩阵的实部部分，权重乘以 Dk 的实部。
			A[:Ns,:] = weight[0,:,nax] * Dk.real
			# comment: 填充 A 矩阵的虚部部分，权重乘以 Dk 的虚部。
			A[Ns:,:] = weight[0,:,nax] * Dk.imag
			# comment: 初始化 B 矩阵 (右侧向量)，其行数为 2*Ns，列数为 Nc。
			B = np.empty((2*Ns,Nc))
			# comment: 填充 B 矩阵的实部部分，权重乘以 f 的实部转置。
			B[:Ns,:] = weight[0,:,nax] * f.real.T
			# comment: 填充 B 矩阵的虚部部分，权重乘以 f 的虚部转置。
			B[Ns:,:] = weight[0,:,nax] * f.imag.T

			# comment: 解决线性系统。
			# comment: 计算 A 矩阵每列的 L2 范数，用于列缩放。
			Escale = np.linalg.norm(A, axis=0)
			# comment: A 矩阵进行列缩放，以改善数值稳定性。
			A /= Escale[nax,:]
			# comment: 使用最小二乘法求解 AX = B。
			X = np.linalg.lstsq(A, B, rcond=-1)[0]
			# comment: 对解矩阵 X 进行反向缩放。
			X /= Escale[:,nax]

			# comment: 从 X 构造残差。
			# comment: 将 X 的前 N 行转置赋值给 SER['C']。
			SER['C'] = X[:N,:].T
			# comment: 如果存在渐近项。
			if options['asymp']>0:
				# comment: 将 X 的第 N 行赋值给 SER['D']。
				SER['D'] = X[N,:]
				# comment: 如果存在线性渐近项。
				if options['asymp']==2:
					# comment: 将 X 的第 N+1 行赋值给 SER['E']。
					SER['E'] = X[N+1,:]
		# comment: 如果不使用共同权重 (即每个元素有独立权重)。
		else: # not common_weight
			# comment: 初始化 SER['C']。
			SER['C'] = np.empty((Nc,N))
			# comment: 如果存在渐近项。
			if options['asymp']>0:
				# comment: 初始化 SER['D']。
				SER['D'] = np.empty((Nc))
				# comment: 如果存在线性渐近项。
				if options['asymp']==2:
					# comment: 初始化 SER['E']。
					SER['E'] = np.empty((Nc))
			# comment: 遍历每个元素 n。
			for n in range(Nc):
				# comment: 填充 A 矩阵的实部部分，当前元素的权重乘以 Dk 的实部。
				A[:Ns,:] = weight[n,:,nax] * Dk.real
				# comment: 填充 A 矩阵的虚部部分，当前元素的权重乘以 Dk 的虚部。
				A[Ns:,:] = weight[n,:,nax] * Dk.imag
				# comment: 初始化 b 向量 (右侧向量)。
				b = np.empty((2*Ns))
				# comment: 填充 b 向量的实部部分，当前元素的权重乘以 f[n,:] 的实部。
				b[:Ns] = weight[n,:] * f[n,:].real
				# comment: 填充 b 向量的虚部部分，当前元素的权重乘以 f[n,:] 的虚部。
				b[Ns:] = weight[n,:] * f[n,:].imag

				# comment: 解决线性系统。
				# comment: 计算 A 矩阵每列的 L2 范数，用于列缩放。
				Escale = np.linalg.norm(A, axis=0)
				# comment: 对 A 矩阵进行列缩放。
				A /= Escale[nax,:]
				# comment: 使用最小二乘法求解 Ax = b。
				x = np.linalg.lstsq(A, b, rcond=-1)[0]
				# comment: 对解向量 x 进行反向缩放。
				x /= Escale

				# comment: 从 x 构造残差。
				# comment: 将 x 的前 N 个元素赋值给 SER['C'] 的对应行。
				SER['C'][n,:] = x[:N]
				# comment: 如果存在渐近项。
				if options['asymp']>0:
					# comment: 将 x 的第 N 个元素赋值给 SER['D'] 的对应元素。
					SER['D'][n] = x[N]
					# comment: 如果存在线性渐近项。
					if options['asymp']==2:
						# comment: 将 x 的第 N+1 个元素赋值给 SER['E'] 的对应元素。
						SER['E'][n] = x[N+1]
		# comment: 结束 if common_weight

		# comment: 如果需要，将 SER['C'] 转换为复数形式 (无论是否需要 cmplx_ss，都会计算 SERC 用于拟合计算)。
		# comment: 初始化 SERC 矩阵，用于存储复数残差。
		SERC = np.empty((Nc,N), dtype=np.complex_)
		# comment: 遍历每个极点。
		for m in range(N):
			# comment: 如果是实数极点。
			if cindex[m]==0:
				# comment: 直接赋值实数残差。
				SERC[:,m] = SER['C'][:,m]
			# comment: 如果是复数共轭极点对的第一个极点。
			if cindex[m]==1:
				# comment: 计算复数残差。
				SERC[:,m]   = SER['C'][:,m] + 1j*SER['C'][:,m+1]
				# comment: 计算其共轭残差。
				SERC[:,m+1] = SER['C'][:,m] - 1j*SER['C'][:,m+1]
		# comment: 如果选项中要求复杂状态空间模型。
		if options['cmplx_ss']:
			# comment: 将复数残差 SERC 赋值给 SER['C']。
			SER['C'] = SERC

		# comment: 计算拟合结果和均方根误差。
		# comment: 计算拟合结果，通过残差乘以共轭部分的逆矩阵 (sI - A)^-1 形式。
		fit = np.dot(SERC, (1/(s[nax,:]-poles[:,nax])))
		# comment: 如果存在渐近项。
		if options['asymp']>0:
			# comment: 添加常数项 D 到拟合结果。
			fit += SER['D'][:,nax]
			# comment: 如果存在线性渐近项。
			if options['asymp']==2:
				# comment: 添加线性项 E*s 到拟合结果。
				fit += s[nax,:] * SER['E'][:,nax]
		# comment: 计算均方根误差 (RMSE)。
		rmserr = np.sqrt(np.sum(np.abs((fit-f)**2))) / np.sqrt(Nc*Ns)

		# comment: 根据选项绘制第二个图。
		if options['spy2']:
			# comment: 幅值拟合图。
			# comment: 将角频率 s 的虚部转换为 Hz。
			freq = s.imag / (2*np.pi)
			# comment: 创建一个新的绘图窗口。
			plt.figure()
			# comment: 初始化 handles 和 labels 列表，用于图例。
			handles = []
			labels  = []
			# comment: 绘制原始数据的幅值曲线。
			handles.append(plt.plot(freq, np.abs(f.T), 'b-'));    labels.append('Data')
			# comment: 绘制拟合结果的幅值曲线。
			handles.append(plt.plot(freq, np.abs(fit.T), 'r--')); labels.append('FRVF')
			# comment: 如果选项中开启了误差绘图。
			if options['errplot']:
				# comment: 绘制偏差 (原始数据与拟合结果之差的绝对值)。
				handles.append(plt.plot(freq, np.abs(f-fit).T, 'g')); labels.append('Deviation')
			# comment: 设置 x 轴的显示范围。
			plt.xlim(freq[0], freq[-1])
			# comment: 如果选项中开启了对数 x 轴。
			if options['logx']:
				# comment: 设置 x 轴为对数刻度。
				plt.xscale('log')
			# comment: 如果选项中开启了对数 y 轴。
			if options['logy']:
				# comment: 设置 y 轴为对数刻度。
				plt.yscale('log')
			# comment: 设置 x 轴标签。
			plt.xlabel('Frequency [Hz]')
			# comment: 设置 y 轴标签。
			plt.ylabel('Magnitude')
			# comment: 设置图表标题。
			plt.title('Approximation of f')
			# comment: 如果选项中开启了图例。
			if options['legend']:
				# comment: 显示图例，并放置在最佳位置。
				plt.legend([h[0] for h in handles], labels, loc='best')
			# comment: 相位图。
			# comment: 如果选项中开启了相位绘图。
			if options['phaseplot']:
				# comment: 创建一个新的绘图窗口。
				plt.figure()
				# comment: 初始化 handles 和 labels 列表。
				handles = []
				labels  = []
				# comment: 绘制原始数据的相位角，并转换为度。
				handles.append(plt.plot(freq, 180*np.unwrap(np.angle(f)).T/np.pi, 'b'))
				labels.append('Data')
				# comment: 绘制拟合结果的相位角，并转换为度。
				handles.append(plt.plot(freq, 180*np.unwrap(np.angle(fit)).T/np.pi, 'r--'))
				labels.append('FRVF')
				# comment: 设置 x 轴的显示范围。
				plt.xlim(freq[0], freq[-1])
				# comment: 如果选项中开启了对数 x 轴。
				if options['logx']:
					# comment: 设置 x 轴为对数刻度。
					plt.xscale('log')
				# comment: 设置 x 轴标签。
				plt.xlabel('Frequency [Hz]')
				# comment: 设置 y 轴标签。
				plt.ylabel('Phase angle [deg]')
				# comment: 设置图表标题。
				plt.title('Approximation of f')
				# comment: 如果选项中开启了图例。
				if options['legend']:
					# comment: 显示图例，并放置在最佳位置。
					plt.legend([h[0] for h in handles], labels, loc='best')
			# comment: 如果选项中开启了阻塞显示。
			if options['block']:
				# comment: 显示图表并阻塞程序执行。
				plt.show()
			# comment: 如果没有开启阻塞显示。
			else:
				# comment: 绘制图表而不阻塞。
				plt.draw()
	# comment: 结束 if not options['skip_res']

	#comment: 将模型转换为实数状态空间模型 (如果请求)。
	#comment: 初始化 SER['B'] 为一个全 1 的 N 维向量。
	SER['B'] = np.ones((N))
	#comment: 如果不需要复杂状态空间模型 (options['cmplx_ss'] 为 False)。
	if not options['cmplx_ss']:
		#comment: 初始化 SER['A'] 为一个 N x N 的零矩阵。
		SER['A'] = np.zeros((N,N))
		#comment: 遍历每个极点。
		for m in range(N):
			#comment: 如果是实数极点。
			if cindex[m]==0:
				#comment: 将实数极点放置在 SER['A'] 的对角线上。
				SER['A'][m,m] = poles[m].real
			#comment: 如果是复数共轭极点对的第一个极点。
			elif cindex[m]==1:
				#comment: 构建 2x2 块矩阵来表示复数共轭极点。
				SER['A'][m,  m]   =  poles[m].real
				SER['A'][m,  m+1] =  poles[m].imag
				SER['A'][m+1,m]   = -poles[m].imag
				SER['A'][m+1,m+1] =  poles[m].real
				#comment: 调整 SER['B'] 向量中与复数共轭极点相关的分量。
				SER['B'][m]   = 2
				SER['B'][m+1] = 0
	#comment: 如果需要复杂状态空间模型。
	else:
		#comment: SER['A'] 直接为极点构成的对角矩阵。
		SER['A'] = np.diag(poles)

	#comment: 返回状态空间模型参数、新的极点、均方根误差和拟合结果。
	return SER, poles, rmserr, fit


#comment: 辅助函数。

#comment: 定义函数 ss2pr，用于将具有公共极点集的状态空间模型转换为极点-残差模型。
#comment: SER: 状态空间模型，必须是 vectfit3 函数的输出格式。
#comment: tri: 布尔值，如果为 True，表示输入来自 tri2full (矩阵值)，否则为 vectfit3 的输出 (向量值)。
def ss2pr(SER, tri=False):
	''' Convert state-space model having COMMON pole set into pole-residue model.
	    Input:
	        SER: must have the format produced by vectfit3. Both formats determined by parameter
	               options['cmplx_ss'] are valid.
	               Ouptut from tri2full is also accepted (set tri to True in this case)
	        tri: False: output from vectfit3 (vector-valued) is assumed
	             True:  output from tri2full (matrix-valued) is assumed
	    Output:
	        R(Nc,N)     Residues, tri=False
	         (Nc,Nc,N)  Residues, tri=True
	        a(N)           poles
	        D(Nc)       Constant term (or None if SER['D']==None)
	        E(Nc)       Linear term   (or None if SER['E']==None)
	    This example script is part of the vector fitting package (VFIT3.zip)
	    Last revised: 19.02.2019.
	    Created by:    Bjorn Gustavsen.
	    Translated and modified by: Simon De Ridder                                             '''

	#comment: 将实数状态空间模型转换为复数模型 (如果必要)。
	#comment: 从 SER 字典中获取 A、B、C 矩阵。
	A = SER['A']
	B = SER['B']
	C = SER['C']
	#comment: 检查 A 矩阵是否是对角矩阵 (即是否为实数状态空间模型)。
	if np.amax(np.abs(A-np.diag(np.diag(A))), axis=None)>0.0:
		#comment: 遍历 A 矩阵的行，直到倒数第二行。
		for m in range(A.shape[0]-1):
			#comment: 如果 A[m, m+1] 不为 0，这表明存在一个 2x2 的块，表示一对复共轭极点。
			if A[m,m+1]!=0.0:
				#comment: 更新 A[m,m] 以包含虚部，并将其标记为复数。这隐式地将 A 数组转换为复数类型。
				A[m,m]     = A[m,m]     + 1j*A[m,m+1] # first use should convert A to complex entirely
				#comment: 更新 A[m+1,m+1] 以包含其共轭虚部。
				A[m+1,m+1] = A[m+1,m+1] - 1j*A[m,m+1]
				#comment: B 矩阵的第 m 行和第 m+1 行取平均值，并更新 B[m,:]。这将它们合并为一个复数极点的贡献。
				B[m,:]   = (B[m,:]+B[m+1,:]) / 2
				#comment: B 矩阵的第 m+1 行复制第 m 行的值。
				B[m+1,:] = B[m,:]
				#comment: C 矩阵的第 m 列更新为复数形式。
				C[:,m]   = C[:,m] + 1j*C[:,m+1]
				#comment: C 矩阵的第 m+1 列更新为第 m 列的共轭。
				C[:,m+1] = np.conj(C[:,m])

	#comment: 将复数状态空间模型转换为极点-残差模型。
	#comment: 获取 C 矩阵的第一维度 (元素的数量 Nc)。
	Nc = C.shape[0]
	#comment: 如果 tri 为 True (矩阵值输入)。
	if tri:
		#comment: 计算每个元素的极点数量 N。
		N = int(A.shape[0]/Nc)
		#comment: 初始化残差矩阵 R，三维。
		R = np.empty((Nc,Nc,N), dtype=np.complex_)
		#comment: 遍历每个极点。
		for m in range(N):
			#comment: 计算残差 R[m]。通过对 C 和 B 的特定部分进行点积来聚合贡献。
			R[:,:,m] = np.sum(C[:,nax,m:Nc*N+m:N] * np.transpose(B[m:Nc*N+m:N,:])[nax,:,:], axis=2)
	#comment: 如果 tri 为 False (向量值输入)。
	else:
		#comment: 获取极点数量 N。
		N = A.shape[0]
		#comment: 初始化残差矩阵 R，二维。
		R = np.empty((Nc,N), dtype=np.complex_)
		#comment: 遍历每个极点。
		for m in range(N):
			#comment: 计算残差 R[:,m]。
			R[:,m] = np.sum(C[:,m:Nc*N+m:N] * B[nax,m:Nc*N+m:N], axis=1)
	#comment: 提取极点，即 A 的对角线元素。
	a = np.diag(A[:N,:N])
	#comment: 返回残差 R、极点 a、常数项 SER['D'] 和线性项 SER['E']。
	return R,a,SER['D'],SER['E']

#comment: 定义函数 tri2full，用于将表示矩阵下三角部分的有理模型转换为完整矩阵的状态空间模型。
#comment: SER: vectfit3 拟合下三角矩阵的输出结构。
def tri2full(SER):
	''' Convert rational model of lower matrix triangle into state-space model of full matrix.
	    Input:
	        SER: Output structure from vectfit3 when fitting lower triangle of a square matrix
	             using a common pole set.
	             Both formats determined by parameter options['cmplx_ss'] are valid
	    Output:
	        SER: State-space model of full matrix (with common pole set)
	    This example script is part of the vector fitting package (VFIT3.zip) 
	    Last revised: 08.08.2008. 
	    Created by:    Bjorn Gustavsen.
	    Translated by: Simon De Ridder                                                          '''

	#comment: 获取 SER['C'] 的第一维度 (拟合的元素总数)。
	Nt = SER['C'].shape[0]
	#comment: 根据下三角矩阵元素的数量 Nt 计算原始方阵的维度 Nc。
	#comment: 公式 Nt = Nc*(Nc+1)/2 的逆运算。
	Nc = -0.5 + np.sqrt(0.25+2.0*Nt)
	#comment: 检查 Nc 是否接近整数，以确保 Nt 是一个有效的下三角矩阵元素数量。
	if abs(Nc-np.round(Nc))>1e-12:
		#comment: 如果不是，则抛出 ValueError。
		raise ValueError('Dimension is not compatible with a vectorized lower triangular matrix')
	#comment: 将 Nc 转换为整数。
	Nc = int(np.round(Nc))
	#comment: 获取状态空间模型的极点数量 N。
	N = SER['A'].shape[0]
	#comment: 初始化 asymp 为 2 (表示存在 D 和 E 项)。
	asymp = 2
	#comment: 检查 SER['E'] 是否为 None，如果 E 项不存在，则 asymp 设为 1。
	if SER['E'] is None:
		asymp = 1
		#comment: 进一步检查 SER['D'] 是否为 None，如果 D 项也不存在，则 asymp 设为 0。
		if SER['D'] is None:
			asymp = 0

	#comment: 初始化 tell (指针)，用于跟踪 SER['C'], SER['D'], SER['E'] 中的当前位置。
	tell = 0
	#comment: 初始化新的状态空间矩阵 AA、BB、CC。
	#comment: AA 矩阵的维度为 (Nc*N, Nc*N)，复杂类型。
	AA = np.zeros((Nc*N,Nc*N), dtype=np.complex_)
	#comment: BB 矩阵的维度为 (Nc*N, Nc)，复杂类型。
	BB = np.zeros((Nc*N,Nc),   dtype=np.complex_)
	#comment: CC 矩阵的维度为 (Nc, Nc*N)，复杂类型。
	CC = np.empty((Nc,Nc*N),   dtype=np.complex_)
	#comment: 初始化 DD 和 EE 为 None。
	DD = None
	EE = None
	#comment: 如果存在渐近项 (asymp > 0)，则初始化 DD 和/或 EE。
	if asymp >0:
		#comment: DD 矩阵的维度为 (Nc, Nc)，复杂类型。
		DD = np.empty((Nc,Nc), dtype=np.complex_)
		#comment: 如果存在线性渐近项 (asymp == 2)。
		if asymp==2:
			#comment: EE 矩阵的维度为 (Nc, Nc)，复杂类型。
			EE = np.empty((Nc,Nc), dtype=np.complex_)
	#comment: 遍历每个列 (用于构建完整矩阵)。
	for col in range(Nc):
		#comment: 填充 AA 矩阵的块对角线部分，每个块都是原始的 SER['A']。
		AA[col*N:(col+1)*N,col*N:(col+1)*N] = SER['A']
		#comment: 填充 BB 矩阵的对应列，每个块是原始的 SER['B']。
		BB[col*N:(col+1)*N,col] = SER['B']
		#comment: 填充 CC 矩阵的下三角部分 (直接提取原下三角中的行)。
		CC[col:,col*N:(col+1)*N] = SER['C'][tell:tell+Nc-col,:]
		#comment: 填充 CC 矩阵的上三角部分 (通过展平原始下三角中的元素)。
		CC[col,(col+1)*N:]       = SER['C'][tell+1:tell+Nc-col,:].flatten()
		#comment: 如果存在渐近项。
		if asymp>0:
			#comment: 填充 DD 矩阵的下三角部分。
			DD[col:Nc,col]   = SER['D'][tell:tell+Nc-col]
			#comment: 填充 DD 矩阵的上三角部分。
			DD[col,col+1:Nc] = SER['D'][tell+1:tell+Nc-col]
			#comment: 如果存在线性渐近项。
			if asymp==2:
				#comment: 填充 EE 矩阵的下三角部分。
				EE[col:Nc,col]   = SER['E'][tell:tell+Nc-col]
				#comment: 填充 EE 矩阵的上三角部分。
				EE[col,col+1:Nc] = SER['E'][tell+1:tell+Nc-col]
		#comment: 更新 tell 指针，移动到下一个下三角块的起始位置。
		tell += Nc - col

	#comment: 返回包含完整状态空间模型参数的字典。
	return {'A':AA, 'B':BB, 'C':CC, 'D':DD, 'E':EE}