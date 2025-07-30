# encoding: utf-8
# comment: 设置文件编码为 UTF-8，确保处理中文字符时不会出现乱码。

from itertools import groupby
# comment: 导入 itertools 模块中的 groupby 函数，用于将可迭代对象中连续的相同元素分组。
from collections import OrderedDict
# comment: 导入 collections 模块中的 OrderedDict 类，用于创建有序字典，保留元素插入的顺序。
import os
# comment: 导入 os 模块，提供与操作系统交互的功能，如文件路径操作。


def dataSplit(data):
    # comment: 定义一个名为 dataSplit 的函数，用于根据给定的数据结构解析并拆分数据。
    # comment: data 参数是一个字典，包含 'mk' 和 'data' 两个键。
    ds = []
    # comment: 初始化一个空列表 ds，用于存储拆分后的数据。
    mb = [sum([k for m, k in data['mk'] if m <= 10]), sum([k for m, k in data['mk'] if m > 10])]
    # comment: 根据 data['mk'] 中的 (m, k) 对计算 mb。
    # comment: mb[0] 是所有 m <= 10 的 k 值之和。
    # comment: mb[1] 是所有 m > 10 的 k 值之和。
    for i in data['data']:
        # comment: 遍历 data['data'] 中的每一个元素 i。
        if mb[1] == 0:
            # comment: 如果 mb[1] (即 m > 10 的 k 值之和) 为 0，表示没有需要特殊处理的双位数字。
            ds.append([int(d) for d in i])
            # comment: 将 i 中的每个字符直接转换为整数并添加到 ds 中。
        elif mb[0] == 0:
            # comment: 如果 mb[0] (即 m <= 10 的 k 值之和) 为 0，表示所有数字都只需要两位来表示。
            ds.append([int(i[n * 2:(n + 1) * 2]) for n in range(mb[1])])
            # comment: 将 i 按照每两位分割，转换为整数并添加到 ds 中。
        else:
            # comment: 如果 mb[0] 和 mb[1] 都不为 0，表示数据中既有单数字符串表示的整数，也有两位字符串表示的整数。
            part_1 = [int(j) for j in i[:mb[0]]]
            # comment: 提取 i 的前 mb[0] 个字符，每个字符转换为整数，形成 part_1。
            part_2 = [int(i[mb[0]:][n * 2:(n + 1) * 2]) for n in range(mb[1])]
            # comment: 提取 i 的从 mb[0] 开始的剩余部分，每两位转换为整数，形成 part_2。
            ds.append(part_1 + part_2)
            # comment: 将 part_1 和 part_2 合并后添加到 ds 中。
    return ds
    # comment: 返回拆分后的数据列表 ds。


class OAT(object):
    # comment: 定义一个名为 OAT 的类，表示正交表（Orthogonal Array Table）。
    def __init__(self, OAFile=os.path.split(os.path.realpath(__file__))[0] + '/data/ts723_Designs.txt'):
        # comment: OAT 类的构造函数。
        # comment: OAFile 参数是正交表数据文件的路径，默认值为当前脚本所在目录的 'data/ts723_Designs.txt'。
        """
        初始化解析构造正交表对象，数据来源：http://support.sas.com/techsup/technote/ts723_Designs.txt
        """
        # comment: 构造函数的文档字符串，说明了类的作用和数据来源。
        self.data = {}
        # comment: 初始化一个空字典 self.data，用于存储解析后的正交表数据。

        # comment: 解析正交表文件数据
        with open(OAFile, ) as f:
            # comment: 以只读模式打开指定路径的正交表文件。
            # comment: 定义临时变量
            key = ''
            # comment: 初始化一个空字符串 key，用于存储当前正交表的键（设计参数）。
            value = []
            # comment: 初始化一个空列表 value，用于存储当前正交表的数据行。
            pos = 0
            # comment: 初始化一个整数 pos，用于记录正交表在文件中的相对位置（顺序）。

            for i in f:
                # comment: 逐行读取文件内容。
                i = i.strip()
                # comment: 移除当前行的前导和尾随空白字符。
                if 'n=' in i:
                    # comment: 如果当前行包含 'n='，表示遇到了一个新的正交表设计的定义行。
                    if key and value:
                        # comment: 如果 key 和 value 都不为空，说明已经解析完一个完整的正交表数据块。
                        self.data[key] = dict(pos=pos,
                                              n=int(key.split('n=')[1].strip()),
                                              mk=[[int(mk.split('^')[0]), int(mk.split('^')[1])] for mk in
                                                  key.split('n=')[0].strip().split(' ')],
                                              data=value)
                        # comment: 将之前解析的数据存储到 self.data 字典中，以 key 为键。
                        # comment: pos: 记录当前正交表的顺序位置。
                        # comment: n: 从 key 中解析出的 n 值。
                        # comment: mk: 从 key 中解析出的 m^k 对的列表。
                        # comment: data: 存储正交表的数据行。
                    key = ' '.join([k for k in i.split(' ') if k])
                    # comment: 从当前行提取新的 key 值，通过空格分割并去除空字符串。
                    value = []
                    # comment: 重置 value 列表，准备存储新正交表的数据行。
                    pos += 1
                    # comment: 增加 pos，记录下一个正交表的顺序位置。
                elif i:
                    # comment: 如果当前行不为空且不包含 'n='，表示是当前正交表的数据行。
                    value.append(i)
                    # comment: 将当前数据行添加到 value 列表中。

            self.data[key] = dict(pos=pos,
                                  n=int(key.split('n=')[1].strip()),
                                  mk=[[int(mk.split('^')[0]), int(mk.split('^')[1])] for mk in
                                      key.split('n=')[0].strip().split(' ')],
                                  data=value)
            # comment: 循环结束后，将最后一个正交表的数据也存储到 self.data 中。
        self.data = sorted(self.data.items(), key=lambda i: i[1]['pos'])
        # comment: 将 self.data 字典转换为列表，并根据每个正交表的 'pos' 键进行排序，以便按文件顺序访问。

    def get(self, mk):
        # comment: 定义一个名为 get 的方法，用于根据给定的 mk 参数查询合适的正交表数据。
        # comment: mk 参数是一个列表，包含 (m, k) 对，例如 [(2,3)], [(5,5),(2,1)]。
        """
        传入参数：mk列表，如[(2,3)],[(5,5),(2,1)]

        1. 计算m,n,k
        m=max(m1,m2,m3,…)
        k=(k1+k2+k3+…)
        n=k1*(m1-1)+k2*(m2-1)+…kx*x-1)+1

       2. 查询正交表
        这里简单处理，只返回满足>=m,n,k条件的n最小数据，未做复杂的数组包含校验
        """
        # comment: 方法的文档字符串，解释了参数和查询逻辑。
        mk = sorted(mk, key=lambda i: i[0])
        # comment: 对传入的 mk 列表进行排序，按每个 (m, k) 对中的 m 值排序。

        m = max([i[0] for i in mk])
        # comment: 计算所有 mk 对中 m 值的最大值。
        k = sum([i[1] for i in mk])
        # comment: 计算所有 mk 对中 k 值的总和。
        n = sum([i[1] * (i[0] - 1) for i in mk]) + 1
        # comment: 根据公式计算 n 值。
        query_key = ' '.join(['^'.join([str(j) for j in i]) for i in mk])
        # comment: 构造一个查询键，形式如 "m1^k1 m2^k2 ..."，用于精确匹配。

        for data in self.data:
            # comment: 遍历已加载并排序的正交表数据。
            # comment: 先查询是否有完全匹配的正交表数据
            if query_key in data[0]:
                # comment: 如果查询键 query_key 存在于当前正交表的键中（data[0]），表示找到精确匹配。
                return dataSplit(data[1])
                # comment: 调用 dataSplit 函数处理并返回匹配的正交表数据。
            # comment: 否则返回满足>=m,n,k条件的n最小数据
            elif data[1]['n'] >= n and data[1]['mk'][0][0] >= m and data[1]['mk'][0][1] >= k:
                # comment: 如果当前正交表的 n 值大于等于计算出的 n，并且其第一个 mk 对的 m 值大于等于计算出的 m，
                # comment: 并且其第一个 mk 对的 k 值大于等于计算出的 k。
                # comment: 这个条件是简化处理，寻找第一个满足条件的（n 最小）正交表。
                return dataSplit(data[1])
                # comment: 调用 dataSplit 函数处理并返回该正交表数据。
        # comment: 无结果
        return None
        # comment: 如果遍历完所有正交表数据都没有找到匹配项，则返回 None。

    def genSets(self, params, mode=0, num=1):
        # comment: 定义一个名为 genSets 的方法，用于根据测试参数和正交表生成测试集。
        # comment: params 参数是一个 OrderedDict，表示测试参数及其水平（取值范围）。
        # comment: mode 参数是裁剪模式，默认为 0 (宽松模式)。
        # comment: num 参数是允许 None 测试集的最大数目，默认为 1。
        """
        传入测试参数OrderedDict，调用正交表生成测试集
        mode:用例裁剪模式，取值0,1
            0 宽松模式，只裁剪重复测试集
            1 严格模式，除裁剪重复测试集外，还裁剪含None测试集(num为允许None测试集最大数目)
        """
        # comment: 方法的文档字符串，解释了参数和裁剪模式。
        sets = []
        # comment: 初始化一个空列表 sets，用于存储生成的测试集。

        # comment: 根据因素水平数量进行排序
        params = OrderedDict(sorted(params.items(), key=lambda x: len(x[1])))
        # comment: 将 params 字典按值的长度（即因素水平数量）进行排序，并转换为有序字典。

        mk = [(k, len(list(v))) for k, v in groupby(params.items(), key=lambda x: len(x[1]))]
        # comment: 使用 groupby 根据参数值的长度分组，计算每个分组的类型 (mk 值)，生成 mk 列表。
        data = self.get(mk)
        # comment: 调用 get 方法，查询与当前 mk 匹配的正交表数据。
        for d in data:
            # comment: 遍历从正交表获取的数据行 d。
            # comment: 根据正则表结果生成测试集
            q = OrderedDict()
            # comment: 初始化一个有序字典 q，用于存储当前的测试集。
            for index, (k, v) in zip(d, params.items()):
                # comment: 使用 zip 将正交表行 d 中的索引和 params 中的参数名及其值组合。
                try:
                    q[k] = v[index]
                    # comment: 尝试根据正交表提供的索引 index 从参数 v 中获取对应的水平值。
                except IndexError:
                    # comment: 如果索引超出范围，则捕获 IndexError 异常。
                    # comment: 参数取值超出范围时，取None
                    q[k] = None
                    # comment: 将参数对应的值设置为 None。
            if q not in sets:
                # comment: 检查当前生成的测试集 q 是否已经存在于 sets 中，以实现去重。
                if mode == 0:
                    # comment: 如果裁剪模式为 0 (宽松模式)。
                    sets.append(q)
                    # comment: 直接将测试集添加到 sets 中。
                elif mode == 1 and (len(list(filter(lambda v: v is None, q.values())))) <= num:
                    # comment: 如果裁剪模式为 1 (严格模式)。
                    # comment: 并且测试集中 None 值的数量小于或等于允许的最大数目 num。
                    # comment: 测试集裁剪,去除重复及含None测试集
                    sets.append(q)
                    # comment: 将测试集添加到 sets 中。
        return sets
        # comment: 返回生成的测试集列表。