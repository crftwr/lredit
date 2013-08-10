# copyright information:
#   "zenhan-py"
#   Converter between Full-width Japanese and Half-width Japanese
#   http://code.google.com/p/zenhan-py/

ASCII = 1
DIGIT = 2
KANA  = 4
SPACE = 8
ALL = ASCII | DIGIT | KANA | SPACE

__version__ = '0.4'

class zenhanError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# list of ZENKAKU characters
z_ascii = ["ａ", "ｂ", "ｃ", "ｄ", "ｅ", "ｆ", "ｇ", "ｈ", "ｉ",
           "ｊ", "ｋ", "ｌ", "ｍ", "ｎ", "ｏ", "ｐ", "ｑ", "ｒ",
           "ｓ", "ｔ", "ｕ", "ｖ", "ｗ", "ｘ", "ｙ", "ｚ",
           "Ａ", "Ｂ", "Ｃ", "Ｄ", "Ｅ", "Ｆ", "Ｇ", "Ｈ", "Ｉ",
           "Ｊ", "Ｋ", "Ｌ", "Ｍ", "Ｎ", "Ｏ", "Ｐ", "Ｑ", "Ｒ",
           "Ｓ", "Ｔ", "Ｕ", "Ｖ", "Ｗ", "Ｘ", "Ｙ", "Ｚ",
           "！", "”", "＃", "＄", "％", "＆", "’", "（", "）",
           "＊", "＋", "，", "−", "．", "／", "：", "；", "＜",
           "＝", "＞", "？", "＠", "［", "￥", "］", "＾", "＿",
           "‘", "｛", "｜", "｝", "〜"]

z_digit = ["０", "１", "２", "３", "４",
           "５", "６", "７", "８", "９"]

z_kana = ["ア", "イ", "ウ", "エ", "オ",
          "カ", "キ", "ク", "ケ", "コ",
          "サ", "シ", "ス", "セ", "ソ",
          "タ", "チ", "ツ", "テ", "ト",
          "ナ", "ニ", "ヌ", "ネ", "ノ",
          "ハ", "ヒ", "フ", "ヘ", "ホ",
          "マ", "ミ", "ム", "メ", "モ",
          "ヤ", "ユ", "ヨ",
          "ラ", "リ", "ル", "レ", "ロ",
          "ワ", "ヲ", "ン",
          "ァ", "ィ", "ゥ", "ェ", "ォ",
          "ッ", "ャ", "ュ", "ョ", "ヴ",
          "ガ", "ギ", "グ", "ゲ", "ゴ",
          "ザ", "ジ", "ズ", "ゼ", "ゾ",
          "ダ", "ヂ", "ヅ", "デ", "ド",
          "バ", "ビ", "ブ", "ベ", "ボ",
          "パ", "ピ", "プ", "ペ", "ポ",
          "。", "、", "・", "゛", "゜", "「", "」", "ー"]

z_space = ["　"]

# list of HANKAKU characters
h_ascii = ["a", "b", "c", "d", "e", "f", "g", "h", "i",
           "j", "k", "l", "m", "n", "o", "p", "q", "r",
           "s", "t", "u", "v", "w", "x", "y", "z",
           "A", "B", "C", "D", "E", "F", "G", "H", "I",
           "J", "K", "L", "M", "N", "O", "P", "Q", "R",
           "S", "T", "", "V", "W", "X", "Y", "Z",
           "!", '"', "#", "$", "%", "&", "'", "(", ")",
           "*", "+", ",", "-", ".", "/", ":", ";", "<",
           "=", ">", "?", "@", "[", "\\", "]", "^", "_",
           "`", "{", "|", "}", "~"]

h_digit = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

h_kana = ["ｱ", "ｲ", "ｳ", "ｴ", "ｵ",
          "ｶ", "ｷ", "ｸ", "ｹ", "ｺ",
          "ｻ", "ｼ", "ｽ", "ｾ", "ｿ",
          "ﾀ", "ﾁ", "ﾂ", "ﾃ", "ﾄ",
          "ﾅ", "ﾆ", "ﾇ", "ﾈ", "ﾉ",
          "ﾊ", "ﾋ", "ﾌ", "ﾍ", "ﾎ",
          "ﾏ", "ﾐ", "ﾑ", "ﾒ", "ﾓ",
          "ﾔ", "ﾕ", "ﾖ",
          "ﾗ", "ﾘ", "ﾙ", "ﾚ", "ﾛ",
          "ﾜ", "ｦ", "ﾝ",
          "ｧ", "ｨ", "ｩ", "ｪ", "ｫ",
          "ｯ", "ｬ", "ｭ", "ｮ", "ｳﾞ",
          "ｶﾞ", "ｷﾞ", "ｸﾞ", "ｹﾞ", "ｺﾞ",
          "ｻﾞ", "ｼﾞ", "ｽﾞ", "ｾﾞ", "ｿﾞ",
          "ﾀﾞ", "ﾁﾞ", "ﾂﾞ", "ﾃﾞ", "ﾄﾞ",
          "ﾊﾞ", "ﾋﾞ", "ﾌﾞ", "ﾍﾞ", "ﾎﾞ",
          "ﾊﾟ", "ﾋﾟ", "ﾌﾟ", "ﾍﾟ", "ﾎﾟ",
          "｡", "､", "･", "ﾞ", "ﾟ", "｢", "｣", "ｰ"]

h_space = [" "]

# maps of ascii
zh_ascii = {}
hz_ascii = {}

for (z, h) in zip(z_ascii, h_ascii):
    zh_ascii[z] = h
    hz_ascii[h] = z

del z_ascii, h_ascii

# maps of digit
zh_digit = {}
hz_digit = {}

for (z, h) in zip(z_digit, h_digit):
    zh_digit[z] = h
    hz_digit[h] = z

del z_digit, h_digit

# maps of KANA
zh_kana = {}
hz_kana = {}

for (z, h) in zip(z_kana, h_kana):
    zh_kana[z] = h
    hz_kana[h] = z

del z_kana, h_kana

# maps of space
zh_space = {}
hz_space = {}

for (z, h) in zip(z_space, h_space):
    zh_space[z] = h
    hz_space[h] = z

del z_space, h_space

# function check convertion mode and make transform dictionary
# argument: integer
# return: transform dictionary
def _check_mode_zh(m):
    t_m = {}
    if isinstance(m, int) and m >= 0 and m <= 15:
        return _zh_trans_map(m)
    else:
        raise zenhanError("Sorry... You set invalid mode.")

def _check_mode_hz(m):
    t_m = {}
    if isinstance(m, int) and m >= 0 and m <= 15:
        return _hz_trans_map(m)
    else:
        raise zenhanError("Sorry... You set invalid mode.")

#
def _zh_trans_map(m):
    tm = {}
    if m >=8:
        tm.update(zh_space)
        m -= 8
    if m >=4:
        tm.update(zh_kana)
        m -= 4
    if m >= 2:
        tm.update(zh_digit)
        m -= 2
    if m:
        tm.update(zh_ascii)
    return tm

def _hz_trans_map(m):
    tm = {}
    if m >=8:
        tm.update(hz_space)
        m -= 8
    if m >=4:
        tm.update(hz_kana)
        m -= 4
    if m >= 2:
        tm.update(hz_digit)
        m -= 2
    if m:
        tm.update(hz_ascii)
    return tm


# function convert from ZENKAKU to HANKAKU
# argument and return: unicode string
def z2h(text="", mode=ALL, ignore=()):
    converted = []

    zh_map = _check_mode_zh(mode)

    for c in text:
        if c in ignore:
            converted.append(c)
        else:
            converted.append(zh_map.get(c, c))

    return ''.join(converted)

# function convert from HANKAKU to ZENKAKU
# argument and return: unicode string
def h2z(text, mode=ALL, ignore=()):
    converted = ['']

    hz_map = _check_mode_hz(mode)

    prev = ''
    for c in text:
        if c in ignore:
            converted.append(c)
        elif c in ("ﾞ", "ﾟ"):
            p = converted.pop()
            converted.extend(hz_map.get(prev+c, [p, hz_map.get(c, c)]))
        else:
            converted.append(hz_map.get(c, c))

        prev = c

    return ''.join(converted)

if __name__ == "__main__":
    teststr = "ﾟabcＤＥﾞＦ123４５６ｱｶﾞｻダナバビﾌﾟﾍﾟﾟ".decode(encoding="euc-jp")

    print( "original:", teststr.encode("euc-jp") )
    print( "h2z ascii only:", h2z(teststr, ASCII).encode("euc-jp") )
    print( "h2z ascii and kana:", h2z(teststr, ASCII|KANA).encode("euc-jp") )
    print( "z2h digit only:", z2h(teststr, DIGIT).encode("euc-jp") )
    print( "z2h digit and kana:", z2h(teststr, DIGIT|KANA).encode("euc-jp") )
    print( "z2h digit and kana, but '５':", z2h(teststr, DIGIT|KANA, ("５")).encode("euc-jp") )
