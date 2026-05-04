import re

# From jieba/__init__.py
re_userdict = re.compile(r'^(.+?)( [0-9]+)?( [a-z]+)?$', re.U)
re_eng_default = re.compile(r'[a-zA-Z0-9]', re.U)
r"""
\u4e00-\u9fd5a-zA-Z0-9+#&\._ : All non-space characters. Will be handled with re_han
\r\n|\s : whitespace characters. Will not be handled.
re_han_default = re.compile("([\u4e00-\u9fd5a-zA-Z0-9+#&\._%]+)", re.U)
Adding "-" symbol in re_han_default
bk: 原无 `r` 标识 。 jieba/__init__.py:45: SyntaxWarning: invalid escape sequence '\.'
    re_han_default = re.compile("([\u4e00-\u9fd5a-zA-Z0-9+#&\._%\-]+)", re.U)
"""
re_han_default = re.compile(r'([\u4E00-\u9FD5a-zA-Z0-9+#&\._%\-]+)', re.U)
re_skip_default = re.compile(r'(\r\n|\s)', re.U)

# From jieba/finalseg.py
re_han_final = re.compile(r'([\u4E00-\u9FD5]+)')
re_skip_final = re.compile(r'([a-zA-Z0-9]+(?:\.\d+)?%?)')

# From jieba/posseg.py
r"""
Lingma: 推荐使用方案，将范围扩展到 \u4e00-\u9fff，理由：
- 覆盖更完整的汉字范围
- 无需额外依赖
- 性能相同
- 向后兼容（只是扩大了匹配范围）
"""
re_han_detail = re.compile(r'([\u4E00-\u9FD5]+)')
re_skip_detail = re.compile(r'([\.0-9]+|[a-zA-Z0-9]+)')
re_han_internal = re.compile(r'([\u4E00-\u9FD5a-zA-Z0-9+#&\._]+)')
re_skip_internal = re.compile(r'(\r\n|\s)')
re_eng_pos = re.compile(r'[a-zA-Z0-9]+')
re_num_pos = re.compile(r'[\.0-9]+')
re_eng1_pos = re.compile(r'^[a-zA-Z0-9]$', re.U)
