import re

import ckit

RegexLexer = ckit.RegexLexer
Token_Text = ckit.Token_Text
Token_Keyword = ckit.Token_Keyword
Token_Name = ckit.Token_Name
Token_Number = ckit.Token_Number
Token_String = ckit.Token_String
Token_Preproc = ckit.Token_Preproc
Token_Comment = ckit.Token_Comment
Token_Space = ckit.Token_Space
Token_Error = ckit.Token_Error


## @addtogroup textwidget
## @{


#----------------------------------------------------------

debug = False

#----------------------------------------------------------

## Python のシンタックス解析クラス
class PythonLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
    
        self.rule_map["keywords"] = [
            (r'(class|def|from|import|'
             r'assert|break|continue|del|elif|else|except|exec|'
             r'finally|for|in|global|if|lambda|pass|print|raise|'
             r'and|or|not|'
             r'return|try|while|yield|as|with)\b', Token_Keyword, None, RegexLexer.Detail),
        ]

        self.rule_map['builtins'] = [
            (r'(__import__|abs|all|any|apply|basestring|bin|bool|buffer|'
             r'bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|'
             r'complex|delattr|dict|dir|divmod|enumerate|eval|execfile|exit|'
             r'file|filter|float|frozenset|getattr|globals|hasattr|hash|hex|id|'
             r'input|int|intern|isinstance|issubclass|iter|len|list|locals|'
             r'long|map|max|min|next|object|oct|open|ord|pow|property|range|'
             r'raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|'
             r'sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|'
             r'vars|xrange|zip|'
             r'None|Ellipsis|NotImplemented|False|True|'
             r'ArithmeticError|AssertionError|AttributeError|'
             r'BaseException|DeprecationWarning|EOFError|EnvironmentError|'
             r'Exception|FloatingPointError|FutureWarning|GeneratorExit|IOError|'
             r'ImportError|ImportWarning|IndentationError|IndexError|KeyError|'
             r'KeyboardInterrupt|LookupError|MemoryError|NameError|'
             r'NotImplemented|NotImplementedError|OSError|OverflowError|'
             r'OverflowWarning|PendingDeprecationWarning|ReferenceError|'
             r'RuntimeError|RuntimeWarning|StandardError|StopIteration|'
             r'SyntaxError|SyntaxWarning|SystemError|SystemExit|TabError|'
             r'TypeError|UnboundLocalError|UnicodeDecodeError|'
             r'UnicodeEncodeError|UnicodeError|UnicodeTranslateError|'
             r'UnicodeWarning|UserWarning|ValueError|VMSError|Warning|'
             r'WindowsError|ZeroDivisionError)\b', Token_Name, None, RegexLexer.Detail),
        ]
        
        self.rule_map['name'] = [
            (r'@[a-zA-Z0-9_.]+', Token_Name),
            ('[a-zA-Z_][a-zA-Z0-9_]*', Token_Text, None, RegexLexer.Detail),
        ]

        self.rule_map['numbers'] = [
            (r'((\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?|'
             r'\d+[eE][+-]?[0-9]+|'
             r'0\d+|'
             r'0[xX][a-fA-F0-9]+|'
             r'\d+L|'
             r'\d+)', Token_Number, None, RegexLexer.Detail)
        ]

        self.rule_map['stringescape'] = [
            (r'\\([\\abfnrtv"\']|\n|N{.*?}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', Token_String)
        ]

        self.rule_map['dqs'] = [
            (r'"', Token_String, 'root'),
            (r'$', Token_String, 'root'),
            (None, Token_String),
        ]
        
        self.rule_map['sqs'] = [
            (r"'", Token_String, 'root'),
            (r'$', Token_String, 'root'),
            (None, Token_String),
        ]

        self.rule_map['dqse'] = self.rule_map['stringescape'] + self.rule_map['dqs']
        self.rule_map['sqse'] = self.rule_map['stringescape'] + self.rule_map['sqs']

        self.rule_map['tdqs'] = [
            (r'"""', Token_String, 'root'),
            (None, Token_String),
        ]

        self.rule_map['tsqs'] = [
            (r"'''", Token_String, 'root'),
            (None, Token_String),
        ]
        
        self.rule_map['tdqse'] = self.rule_map['stringescape'] + self.rule_map['tdqs']
        self.rule_map['tsqse'] = self.rule_map['stringescape'] + self.rule_map['tsqs']
        
        self.rule_map["root"] = []
        self.rule_map["root"] += self.rule_map["keywords"] 
        self.rule_map["root"] += self.rule_map["builtins"]
        self.rule_map["root"] += self.rule_map["name"]
        self.rule_map["root"] += self.rule_map["numbers"]
        self.rule_map["root"] += [
            ('(?:[rR]|[uU][rR]|[rR][uU])"""', Token_String, 'tdqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'''", Token_String, 'tsqs'),
            ('[uU]?"""', Token_String, 'tdqse'),
            ("[uU]?'''", Token_String, 'tsqse'),
            ('(?:[rR]|[uU][rR]|[rR][uU])"', Token_String, 'dqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'", Token_String, 'sqs'),
            ('[uU]?"', Token_String, 'dqse'),
            ("[uU]?'", Token_String, 'sqse'),
            (r'#.*$', Token_Comment),
            (None,Token_Text)
        ]

#----------------------------------------------------------

## Perl のシンタックス解析クラス
class PerlLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)

        self.rule_map["balanced-regex"] = [
            (r'/(\\\\|\\[^\\]|[^\\/])*/[egimosx]*', Token_String, 'root'),
            (r'!(\\\\|\\[^\\]|[^\\!])*![egimosx]*', Token_String, 'root'),
            (r'\\(\\\\|[^\\])*\\[egimosx]*', Token_String, 'root'),
            (r'\{(\\\\|\\[^\\]|[^\\}])*\}[egimosx]*', Token_String, 'root'),
            (r'<(\\\\|\\[^\\]|[^\\>])*>[egimosx]*', Token_String, 'root'),
            (r'\[(\\\\|\\[^\\]|[^\\\]])*\][egimosx]*', Token_String, 'root'),
            (r'\((\\\\|\\[^\\]|[^\\)])*\)[egimosx]*', Token_String, 'root'),
            (r'@(\\\\|\\[^\\]|[^\\@])*@[egimosx]*', Token_String, 'root'),
            (r'%(\\\\|\\[^\\]|[^\\%])*%[egimosx]*', Token_String, 'root'),
            (r'\$(\\\\|\\[^\\]|[^\\$])*\$[egimosx]*', Token_String, 'root'),
            (None,Token_String)
        ]
        
        self.rule_map["root"] = [
            (r'\#.*?$', Token_Comment),
            (r'^=[a-zA-Z0-9]+\s+.*?\n=cut', Token_Comment),
            (r'(case|continue|do|else|elsif|for|foreach|if|last|my|next|our|redo|'
             r'reset|then|unless|until|while|use|print|new|BEGIN|CHECK|INIT|END|return)\b',Token_Keyword, None, RegexLexer.Detail),
            (r'(format)(\s+)(\w+)(\s*)(=)(\s*\n)', (Token_Keyword, Token_Text, Token_Name, Token_Text, Token_Text, Token_Text), 'format'),
            (r'(eq|lt|gt|le|ge|ne|not|and|or|cmp)\b', Token_Keyword, None, RegexLexer.Detail),
            # common delimiters
            (r's/(\\\\|\\[^\\]|[^\\/])*/(\\\\|\\[^\\]|[^\\/])*/[egimosx]*', Token_String),
            (r's!(\\\\|\\!|[^!])*!(\\\\|\\!|[^!])*![egimosx]*', Token_String),
            (r's\\(\\\\|[^\\])*\\(\\\\|[^\\])*\\[egimosx]*', Token_String),
            (r's@(\\\\|\\[^\\]|[^\\@])*@(\\\\|\\[^\\]|[^\\@])*@[egimosx]*', Token_String),
            (r's%(\\\\|\\[^\\]|[^\\%])*%(\\\\|\\[^\\]|[^\\%])*%[egimosx]*', Token_String),
            # balanced delimiters
            (r's\{(\\\\|\\[^\\]|[^\\}])*\}\s*', Token_String, 'balanced-regex'),
            (r's<(\\\\|\\[^\\]|[^\\>])*>\s*', Token_String, 'balanced-regex'),
            (r's\[(\\\\|\\[^\\]|[^\\\]])*\]\s*', Token_String, 'balanced-regex'),
            (r's\((\\\\|\\[^\\]|[^\\)])*\)\s*', Token_String, 'balanced-regex'),

            (r'm?/(\\\\|\\[^\\]|[^\\/\n])*/[gcimosx]*', Token_String),
            (r'm(?=[/!\\{<\[(@%$])', Token_String, 'balanced-regex'),
            (r'((?<==~)|(?<=\())\s*/(\\\\|\\[^\\]|[^\\/])*/[gcimosx]*', Token_String),
            (r'\s+', Token_Text),
            (r'(abs|accept|alarm|atan2|bind|binmode|bless|caller|chdir|'
             r'chmod|chomp|chop|chown|chr|chroot|close|closedir|connect|'
             r'continue|cos|crypt|dbmclose|dbmopen|defined|delete|die|'
             r'dump|each|endgrent|endhostent|endnetent|endprotoent|'
             r'endpwent|endservent|eof|eval|exec|exists|exit|exp|fcntl|'
             r'fileno|flock|fork|format|formline|getc|getgrent|getgrgid|'
             r'getgrnam|gethostbyaddr|gethostbyname|gethostent|getlogin|'
             r'getnetbyaddr|getnetbyname|getnetent|getpeername|getpgrp|'
             r'getppid|getpriority|getprotobyname|getprotobynumber|'
             r'getprotoent|getpwent|getpwnam|getpwuid|getservbyname|'
             r'getservbyport|getservent|getsockname|getsockopt|glob|gmtime|'
             r'goto|grep|hex|import|index|int|ioctl|join|keys|kill|last|'
             r'lc|lcfirst|length|link|listen|local|localtime|log|lstat|'
             r'map|mkdir|msgctl|msgget|msgrcv|msgsnd|my|next|no|oct|open|'
             r'opendir|ord|our|pack|package|pipe|pop|pos|printf|'
             r'prototype|push|quotemeta|rand|read|readdir|'
             r'readline|readlink|readpipe|recv|redo|ref|rename|require|'
             r'reverse|rewinddir|rindex|rmdir|scalar|seek|seekdir|'
             r'select|semctl|semget|semop|send|setgrent|sethostent|setnetent|'
             r'setpgrp|setpriority|setprotoent|setpwent|setservent|'
             r'setsockopt|shift|shmctl|shmget|shmread|shmwrite|shutdown|'
             r'sin|sleep|socket|socketpair|sort|splice|split|sprintf|sqrt|'
             r'srand|stat|study|substr|symlink|syscall|sysopen|sysread|'
             r'sysseek|system|syswrite|tell|telldir|tie|tied|time|times|tr|'
             r'truncate|uc|ucfirst|umask|undef|unlink|unpack|unshift|untie|'
             r'utime|values|vec|wait|waitpid|wantarray|warn|write)\b', Token_Name, None, RegexLexer.Detail),
            (r'((__(DATA|DIE|WARN)__)|(STD(IN|OUT|ERR)))\b', Token_Name, None, RegexLexer.Detail),
            (r'<<([\'"]?)([a-zA-Z_]\w*)\1;?\n.*?\n\2\n', Token_String),
            (r'__END__', Token_Preproc, 'end-part'),
            (r'\$\^[ADEFHILMOPSTWX]', Token_Name),
            (r"\$[\\\"\[\]'&`+*.,;=%~?@$!<>(^|/-](?!\w)", Token_Name),
            (r'[$@%#]+', Token_Name, 'varname'),
            (r'0_?[0-7]+(_[0-7]+)*', Token_Number, None, RegexLexer.Detail),
            (r'0x[0-9A-Fa-f]+(_[0-9A-Fa-f]+)*', Token_Number, None, RegexLexer.Detail),
            (r'0b[01]+(_[01]+)*', Token_Number, None, RegexLexer.Detail),
            (r'(?i)(\d*(_\d*)*\.\d+(_\d*)*|\d+(_\d*)*\.\d+(_\d*)*)(e[+-]?\d+)?', Token_Number, None, RegexLexer.Detail),
            (r'(?i)\d+(_\d*)*e[+-]?\d+(_\d*)*', Token_Number, None, RegexLexer.Detail),
            (r'\d+(_\d+)*', Token_Number, None, RegexLexer.Detail),
            (r"'(\\\\|\\[^\\]|[^'\\])*'", Token_String),
            (r'"(\\\\|\\[^\\]|[^"\\])*"', Token_String),
            (r'`(\\\\|\\[^\\]|[^`\\])*`', Token_String),
            (r'<([^\s>]+)>', Token_String),
            (r'(q|qq|qw|qr|qx)\{', Token_String, 'cb-string'),
            (r'(q|qq|qw|qr|qx)\(', Token_String, 'rb-string'),
            (r'(q|qq|qw|qr|qx)\[', Token_String, 'sb-string'),
            (r'(q|qq|qw|qr|qx)\<', Token_String, 'lt-string'),
            (r'(q|qq|qw|qr|qx)([\W_])(.|\n)*?\2', Token_String),
            (r'package\s+', Token_Keyword, 'modulename'),
            (r'sub\s+', Token_Keyword, 'funcname'),
            (r'(\[\]|\*\*|::|<<|>>|>=|<=>|<=|={3}|!=|=~|'
             r'!~|&&?|\|\||\.{1,3})', Token_Text, None, RegexLexer.Detail),
            (r'[-+/*%=<>&^|!\\~]=?', Token_Text, None, RegexLexer.Detail),
            (r'[()\[\]:;,<>/?{}]', Token_Text, None, RegexLexer.Detail),  # yes, there's no shortage of punctuation in Perl!
            ('[a-zA-Z_][a-zA-Z0-9_]*', Token_Text, None, RegexLexer.Detail),
            (None,Token_Text)
        ]

        self.rule_map["format"] = [
            (r'\.\n', Token_String, 'root'),
            (r'[^\n]*\n', Token_String),
            (None,Token_String)
        ]
        
        self.rule_map["varname"] = [
            (r'\s+', Token_Text),
            (r'\{', Token_Text, 'root'),    # hash syntax?
            (r'\)|,', Token_Text, 'root'),  # argument specifier
            (r'\w+::', Token_Name),
            (r'[\w:]+', Token_Name, 'root'),
            (None,Token_Name)
        ]
        
        self.rule_map["name"] = [
            (r'\w+::', Token_Name),
            (r'[\w:]+', Token_Name, 'root'),
            (r'[A-Z_]+(?=\W)', Token_Name, 'root'),
            (r'(?=\W)', Token_Text, 'root'),
            (None,Token_Name)
        ]
        
        self.rule_map["modulename"] = [
            (r'[a-zA-Z_]\w*', Token_Name, 'root'),
            (None,Token_Name)
        ]
        
        self.rule_map["funcname"] = [
            (r'[a-zA-Z_]\w*[!?]?', Token_Name),
            (r'\s+', Token_Text),
            # argument declaration
            (r'(\([$@%]*\))(\s*)', (Token_Text, Token_Text)),
            (r';', Token_Text, 'root'),
            (r'.*?\{', Token_Text, 'root'),
            (None,Token_Name)
        ]
        
        self.rule_map["cb-string"] = [
            (r'\\[{}\\]', Token_String),
            (r'\\', Token_String),
            #(r'\{', Token_String, 'cb-string'), # FIXME : ネストを解釈していない
            (r'\}', Token_String, 'root'),
            (r'[^{}\\]+', Token_String),
            (None,Token_String)
        ]
        
        self.rule_map["rb-string"] = [
            (r'\\[()\\]', Token_String),
            (r'\\', Token_String),
            #(r'\(', Token_String, 'rb-string'), # FIXME : ネストを解釈していない
            (r'\)', Token_String, 'root'),
            (r'[^()]+', Token_String),
            (None,Token_String)
        ]
        
        self.rule_map["sb-string"] = [
            (r'\\[\[\]\\]', Token_String),
            (r'\\', Token_String),
            #(r'\[', Token_String, 'sb-string'), # FIXME : ネストを解釈していない
            (r'\]', Token_String, 'root'),
            (r'[^\[\]]+', Token_String),
            (None,Token_String)
        ]
        
        self.rule_map["lt-string"] = [
            (r'\\[<>\\]', Token_String),
            (r'\\', Token_String),
            #(r'\<', Token_String, 'lt-string'), # FIXME : ネストを解釈していない
            (r'\>', Token_String, 'root'),
            (r'[^<>]+', Token_String),
            (None,Token_String)
        ]
        
        self.rule_map["end-part"] = [
            (r'.+', Token_Preproc, 'root'),
            (None,Token_Preproc)
        ]

#----------------------------------------------------------

## JavaScript のシンタックス解析クラス
class JavaScriptLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)

        self.rule_map['multiline_comment'] = [
            (r'[*]/', Token_Comment, 'root'),
            (None, Token_Comment),
        ]

        # FIXME : 正規表現リテラルをちゃんと扱う

        """
        self.rule_map['slashstartsregex'] = [
            (r'\s+', Token_Text),
            (r'<!--', Token_Comment),
            (r'//.*$', Token_Comment, 'root'),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'/(\\.|[^[/\\\n]|\[(\\.|[^\]\\\n])*])+/'
             r'([gim]+\b|\B)', Token_String, 'root'),
            #(r'(?=/)', Token_Text, 'root'),
            (None, Token_Text, 'root'),
        ]
        """

        self.rule_map['root'] = [
            #(r'^(?=\s|/|<!--)', Token_Text, 'slashstartsregex'), 
            (r'\s+', Token_Text),
            (r'<!--', Token_Comment),
            (r'//.*$', Token_Comment),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            #(r'\+\+|--|~|&&|\?|:|\|\||\\(?=\n)|'
            # r'(<<|>>>?|==?|!=?|[-<>+*%&\|\^/])=?', Token_Text, 'slashstartsregex'),
            #(r'[{(\[;,]', Token_Text, 'slashstartsregex'),
            (r'[})\].]', Token_Text),
            (r'(for|in|while|do|break|return|continue|switch|case|default|if|else|'
             r'throw|try|catch|finally|new|delete|typeof|instanceof|void|'
             r'this)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(var|with|function)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(abstract|boolean|byte|char|class|const|debugger|double|enum|export|'
             r'extends|final|float|goto|implements|import|int|interface|long|native|'
             r'package|private|protected|public|short|static|super|synchronized|throws|'
             r'transient|volatile)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(true|false|null|NaN|Infinity|undefined)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(Array|Boolean|Date|Error|Function|Math|netscape|'
             r'Number|Object|Packages|RegExp|String|sun|decodeURI|'
             r'decodeURIComponent|encodeURI|encodeURIComponent|'
             r'Error|eval|isFinite|isNaN|parseFloat|parseInt|document|this|'
             r'window)\b', Token_Name, None, RegexLexer.Detail),
            (r'[$a-zA-Z_][a-zA-Z0-9_]*', Token_Text),
            (r'[0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?', Token_Number, None, RegexLexer.Detail),
            (r'0x[0-9a-fA-F]+', Token_Number, None, RegexLexer.Detail),
            (r'[0-9]+', Token_Number, None, RegexLexer.Detail),
            (r'"(\\\\|\\"|[^"])*"', Token_String),
            (r"'(\\\\|\\'|[^'])*'", Token_String),
            (None,Token_Text)
        ]


#----------------------------------------------------------

## C言語 のシンタックス解析クラス
class CLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)

        self.rule_map['string'] = [
            (r'"', Token_String, 'root'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', Token_String),
            (r'\\\n', Token_String), # line continuation
            (r'\\', Token_String), # stray backslash
            (r'$', Token_Text, 'root'),
            (None, Token_String),
        ]
        
        self.rule_map['multiline_comment'] = [
            (r'[*]/', Token_Comment, 'root'),
            (None, Token_Comment),
        ]

        self.rule_map['macro'] = [
            (r'\"[^"]*\"', Token_String),
            (r'\<[^<>]*\>', Token_String),
            (r'//.*$', Token_Comment, 'root'),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'$', Token_Text, 'root'),
            (None, Token_Text),
        ]

        self.rule_map['root'] = [
            (r'^\s*#\s*[a-z]+', Token_Preproc, 'macro'),
            (r'//.*$', Token_Comment),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'L?"', Token_String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", Token_String),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Token_Number, None, RegexLexer.Detail),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Token_Number, None, RegexLexer.Detail),
            (r'0x[0-9a-fA-F]+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'0[0-7]+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'\d+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'(asm|auto|break|case|catch|const|const_cast|continue|'
             r'default|delete|do|dynamic_cast|else|enum|explicit|export|'
             r'extern|for|friend|goto|if|mutable|namespace|new|operator|'
             r'private|protected|public|register|reinterpret_cast|return|'
             r'sizeof|static|struct|switch|'
             r'typedef|typename|union|'
             r'volatile|while)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(int|long|float|short|double|char|unsigned|signed|'
             r'void|wchar_t)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'NULL\b', Token_Name, None, RegexLexer.Detail),
            ('[a-zA-Z_][a-zA-Z0-9_]*:(?!:)', Token_Text),
            ('[a-zA-Z_][a-zA-Z0-9_]*', Token_Text),
            (r'\*/', Token_Error),
            (None,Token_Text)
        ]

#----------------------------------------------------------

## C++ のシンタックス解析クラス
class CppLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)

        self.rule_map['string'] = [
            (r'"', Token_String, 'root'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', Token_String),
            (r'\\\n', Token_String), # line continuation
            (r'\\', Token_String), # stray backslash
            (r'$', Token_Text, 'root'),
            (None, Token_String),
        ]
        
        self.rule_map['multiline_comment'] = [
            (r'[*]/', Token_Comment, 'root'),
            (None, Token_Comment),
        ]

        self.rule_map['macro'] = [
            (r'\"[^"]*\"', Token_String),
            (r'\<[^<>]*\>', Token_String),
            (r'//.*$', Token_Comment, 'root'),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'$', Token_Text, 'root'),
            (None, Token_Text),
        ]

        self.rule_map['root'] = [
            (r'^\s*#\s*[a-z]+', Token_Preproc, 'macro'),
            (r'//.*$', Token_Comment),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'L?"', Token_String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", Token_String),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Token_Number, None, RegexLexer.Detail),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Token_Number, None, RegexLexer.Detail),
            (r'0x[0-9a-fA-F]+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'0[0-7]+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'\d+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'(asm|auto|break|case|catch|const|const_cast|continue|'
             r'default|delete|do|dynamic_cast|else|enum|explicit|export|'
             r'extern|for|friend|goto|if|mutable|namespace|new|operator|'
             r'private|protected|public|register|reinterpret_cast|return|'
             r'restrict|sizeof|static|static_cast|class|struct|switch|template|'
             r'this|throw|throws|try|typedef|typeid|typename|union|using|'
             r'volatile|virtual|while)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(bool|int|long|float|short|double|char|unsigned|signed|'
             r'void|wchar_t)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(_{0,2}inline|naked|thread)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'__(asm|int8|based|except|int16|stdcall|cdecl|fastcall|int32|'
             r'declspec|finally|int64|try|leave|wchar_t|w64|virtual_inheritance|'
             r'uuidof|unaligned|super|single_inheritance|raise|noop|'
             r'multiple_inheritance|m128i|m128d|m128|m64|interface|'
             r'identifier|forceinline|event|assume)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(true|false)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'NULL\b', Token_Name, None, RegexLexer.Detail),
            ('[a-zA-Z_][a-zA-Z0-9_]*:(?!:)', Token_Text),
            ('[a-zA-Z_][a-zA-Z0-9_]*', Token_Text),
            (r'\*/', Token_Error),
            (None,Token_Text)
        ]

#----------------------------------------------------------

## C# のシンタックス解析クラス
class CsharpLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        self.rule_map['string'] = [
            (r'"', Token_String, 'root'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', Token_String),
            (r'\\\n', Token_String), # line continuation
            (r'\\', Token_String), # stray backslash
            (r'$', Token_Text, 'root'),
            (None, Token_String),
        ]
        
        self.rule_map['multiline_comment'] = [
            (r'[*]/', Token_Comment, 'root'),
            (None, Token_Comment),
        ]

        self.rule_map['macro'] = [
            (r'\"[^"]*\"', Token_String),
            (r'\<[^<>]*\>', Token_String),
            (r'//.*$', Token_Comment, 'root'),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'$', Token_Text, 'root'),
            (None, Token_Text),
        ]

        self.rule_map['root'] = [
            (r'^\s*#\s*[a-z]+', Token_Preproc, 'macro'),
            (r'//.*$', Token_Comment),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'"', Token_String, 'string'),
            (r"'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", Token_String),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Token_Number, None, RegexLexer.Detail),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Token_Number, None, RegexLexer.Detail),
            (r'0x[0-9a-fA-F]+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'0[0-7]+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'\d+[Ll]?', Token_Number, None, RegexLexer.Detail),
            (r'(abstract|as|base|break|case|catch|'
             r'checked|const|continue|default|delegate|'
             r'do|else|enum|event|explicit|extern|false|finally|'
             r'fixed|for|foreach|goto|if|implicit|in|interface|'
             r'internal|is|lock|new|null|operator|'
             r'out|override|params|private|protected|public|readonly|'
             r'ref|return|sealed|sizeof|stackalloc|static|'
             r'switch|this|throw|true|try|typeof|'
             r'unchecked|unsafe|virtual|void|while|'
             r'get|set|new|partial|yield|add|remove|value|'
             r'global|class|struct|namespace|using|'
             r'short|string|uint|ulong|ushort|'
             r'bool|byte|char|decimal|double|float|int|long|object|sbyte|var|volatile)\b', Token_Keyword, None, RegexLexer.Detail),
            ('[a-zA-Z_][a-zA-Z0-9_]*:(?!:)', Token_Text),
            ('[a-zA-Z_][a-zA-Z0-9_]*', Token_Text),
            (r'\*/', Token_Error),
            (None,Token_Text)
        ]


#----------------------------------------------------------

## Java のシンタックス解析クラス
class JavaLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        self.rule_map['multiline_comment'] = [
            (r'[*]/', Token_Comment, 'root'),
            (None, Token_Comment),
        ]

        self.rule_map['root'] = [
            (r'[^\S\n]+', Token_Text),
            (r'//.*$', Token_Comment),
            (r'/[*]', Token_Comment, 'multiline_comment'),
            (r'@[a-zA-Z_][a-zA-Z0-9_\.]*', Token_Text),
            (r'(assert|break|case|catch|continue|default|do|else|finally|for|'
             r'class|interface|package|import|'
             r'if|goto|instanceof|new|return|switch|this|throw|try|while)\b',
             Token_Keyword, None, RegexLexer.Detail),
            (r'(abstract|const|enum|extends|final|implements|native|private|'
             r'protected|public|static|strictfp|super|synchronized|throws|'
             r'transient|volatile)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'(boolean|byte|char|double|float|int|long|short|void)\b',
             Token_Keyword, None, RegexLexer.Detail),
            (r'(true|false|null)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'"(\\\\|\\"|[^"])*"', Token_String),
            (r"'\\.'|'[^\\]'|'\\u[0-9a-f]{4}'", Token_String),
            (r'(\.)([a-zA-Z_][a-zA-Z0-9_]*)', (Token_Text, Token_Text)),
            (r'[a-zA-Z_][a-zA-Z0-9_]*:', Token_Text),
            (r'[a-zA-Z_\$][a-zA-Z0-9_]*', Token_Text),
            (r'[~\^\*!%&\[\]\(\)\{\}<>\|+=:;,./?-]', Token_Text),
            (r'[0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?', Token_Number, None, RegexLexer.Detail),
            (r'0x[0-9a-f]+', Token_Number, None, RegexLexer.Detail),
            (r'[0-9]+L?', Token_Number, None, RegexLexer.Detail),
            (None,Token_Text)
        ]


#----------------------------------------------------------

## GLSL のシンタックス解析クラス
class GlslLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        self.rule_map['root'] = [
            (r'^#.*', Token_Preproc),
            (r'//.*', Token_Comment),
            (r'/\*[\w\W]*\*/', Token_Comment),
            (r'\+|-|~|!=?|\*|/|%|<<|>>|<=?|>=?|==?|&&?|\^|\|\|?', Token_Text),
            (r'[?:]', Token_Text),
            (r'\bdefined\b', Token_Text),
            (r'[;{}(),\[\]]', Token_Text),
            (r'[+-]?\d*\.\d+([eE][-+]?\d+)?', Token_Number, None, RegexLexer.Detail),
            (r'[+-]?\d+\.\d*([eE][-+]?\d+)?', Token_Number, None, RegexLexer.Detail),
            (r'0[xX][0-9a-fA-F]*', Token_Number, None, RegexLexer.Detail),
            (r'0[0-7]*', Token_Number, None, RegexLexer.Detail),
            (r'[1-9][0-9]*', Token_Number, None, RegexLexer.Detail),
            (r'\b(attribute|const|uniform|varying|centroid|break|continue|'
             r'do|for|while|if|else|in|out|inout|float|int|void|bool|true|'
             r'false|invariant|discard|return|mat[234]|mat[234]x[234]|'
             r'vec[234]|[ib]vec[234]|sampler[123]D|samplerCube|'
             r'sampler[12]DShadow|struct)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'\b(asm|class|union|enum|typedef|template|this|packed|goto|'
             r'switch|default|inline|noinline|volatile|public|static|extern|'
             r'external|interface|long|short|double|half|fixed|unsigned|'
             r'lowp|mediump|highp|precision|input|output|hvec[234]|'
             r'[df]vec[234]|sampler[23]DRect|sampler2DRectShadow|sizeof|'
             r'cast|namespace|using)\b', Token_Keyword, None, RegexLexer.Detail),
            (r'[a-zA-Z_][a-zA-Z_0-9]*', Token_Text),
            (r'\.', Token_Text),
            (r'\s+', Token_Text),
            (None,Token_Text)
        ]


#----------------------------------------------------------

## XML のシンタックス解析クラス
class XmlLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        self.rule_map['comment'] = [
            ('[^-]+', Token_Comment),
            ('-->', Token_Comment, 'root'),
            ('-', Token_Comment),
            (None, Token_Comment),
        ]

        self.rule_map['attr'] = [
            ('\s+', Token_Text),
            ('".*?"', Token_String, 'tag'),
            ("'.*?'", Token_String, 'tag'),
            (r'[^\s>]+', Token_String, 'tag'),
            (None, Token_String),
        ]

        self.rule_map['tag'] = [
            (r'\s+', Token_Text),
            (r'[a-zA-Z0-9_.:-]+\s*=', Token_Text, 'attr'),
            (r'/?\s*>', Token_Keyword, 'root'),
            (None, Token_Text),
        ]

        self.rule_map['root'] = [
            ('[^<&]+', Token_Text),
            (r'&\S*?;', Token_Name),
            (r'\<\!\[CDATA\[.*?\]\]\>', Token_Preproc),
            ('<!--', Token_Comment, 'comment'),
            (r'<\?.*?\?>', Token_Preproc),
            ('<![^>]*>', Token_Preproc),
            (r'<\s*[a-zA-Z0-9:._-]+', Token_Keyword, 'tag'),
            (r'<\s*/\s*[a-zA-Z0-9:._-]+\s*>', Token_Keyword),
            (None,Token_Text)
        ]


#----------------------------------------------------------

## HTML のシンタックス解析クラス
class HtmlLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        self.rule_map['comment'] = [
            ('[^-]+', Token_Comment),
            ('-->', Token_Comment, 'root'),
            ('-', Token_Comment),
            (None, Token_Comment),
        ]

        self.rule_map['attr'] = [
            ('".*?"', Token_String, 'tag'),
            ("'.*?'", Token_String, 'tag'),
            (r'[^\s>]+', Token_String, 'tag'),
            (None, Token_String),
        ]

        self.rule_map['tag'] = [
            (r'\s+', Token_Text),
            (r'[a-zA-Z0-9_:-]+\s*=', Token_Text, 'attr'),
            (r'[a-zA-Z0-9_:-]+', Token_Text),
            (r'/?\s*>', Token_Keyword, 'root'),
            (None, Token_Text),
        ]
        
        # FIXME : JavaScript と CSS を 入れ子にできるように
    
        """
        self.rule_map['script-content'] = [
            (r'<\s*/\s*script\s*>', Token_Name, 'root'),
            (r'.+?(?=<\s*/\s*script\s*>)', Token_Text ),
            (None, Token_Text),
        ]

        self.rule_map['style-content'] = [
            (r'<\s*/\s*style\s*>', Token_Name, 'root'),
            (r'.+?(?=<\s*/\s*style\s*>)', Token_Text ),
            (None, Token_Text),
        ]
        """

        self.rule_map['root'] = [
            ('[^<&]+', Token_Text),
            (r'&\S*?;', Token_Name),
            (r'\<\!\[CDATA\[.*?\]\]\>', Token_Preproc),
            ('<!--', Token_Comment, 'comment'),
            (r'<\?.*?\?>', Token_Preproc),
            ('<![^>]*>', Token_Preproc),
            #(r'<\s*script\s*', Token_Name, ('script-content', 'tag')),
            #(r'<\s*style\s*', Token_Name, ('style-content', 'tag')),
            (r'<\s*[a-zA-Z0-9:]+', Token_Keyword, 'tag'),
            (r'<\s*/\s*[a-zA-Z0-9:]+\s*>', Token_Keyword),
            (None, Token_Text),
        ]


#----------------------------------------------------------

## Makefile のシンタックス解析クラス
class MakefileLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        """
        self.rule_map['export'] = [
            (r'[a-zA-Z0-9_${}-]+', Token_Name),
            (r'$', Token_Text, 'root'),
            (r'\s+', Token_Text),
            (None,Token_Text),
        ]
        
        self.rule_map['block-header'] = [
            (r'[^,\\\n#]+', Token_Number),
            (r',', Token_Text),
            (r'#.*$', Token_Comment),
            (r'\\\n', Token_Text), # line continuation
            (r'\\.', Token_Text),
            (r'(?:[\t ]+.*\n|\n)+', Token_Text, 'root'),
            (None,Token_Text),
        ]
        """

        self.rule_map['root'] = [
            (r'^(?:[\t ]+.*\n|\n)+', Token_Text),
            (r'\$\((?:.*\\\n|.*\n)+', Token_Text),
            (r'\s+', Token_Text),
            (r'#.*?$', Token_Comment),
            #(r'(export)(\s+)(?=[a-zA-Z0-9_${}\t -]+\n)', (Token_Keyword, Token_Text), 'export'),
            (r'\b(ifeq|ifneq|ifdef|ifndef|else|endif|include|define|endef|:)\b', Token_Keyword),
            # assignment
            #(r'([a-zA-Z0-9_${}.-]+)(\s*)([!?:+]?=)([ \t]*)((?:.*\\\n|.*\n)+)',
            # (Token_Name, Token_Text, Token_Text, Token_Text, Token_Text)),
            # strings
            (r'(?s)"(\\\\|\\.|[^"\\])*"', Token_String),
            (r"(?s)'(\\\\|\\.|[^'\\])*'", Token_String),
            # targets
            #(r'([^\n:]+)(:+)([ \t]*)', (Token_Name, Token_Text, Token_Text), 'block-header'),
            # TODO: add paren handling (grr)
            (None,Token_Text),
        ]
        

#----------------------------------------------------------

## Batch のシンタックス解析クラス
class BatchLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        self.re_flags = re.IGNORECASE

        self.rule_map['root'] = [
            # Lines can start with @ to prevent echo
            (r'^\s*@', Token_Text),
            (r'^(\s*)(rem\s.*)$', (Token_Text, Token_Comment)),
            (r'".*?"', Token_String),
            (r"'.*?'", Token_String),
            # If made more specific, make sure you still allow expansions
            # like %~$VAR:zlt
            (r'%%?[~$:\w]+%?', Token_Name),
            (r'::.*', Token_Comment), # Technically :: only works at BOL
            (r'(set)(\s+)(\w+)', (Token_Keyword, Token_Text, Token_Name)),
            (r'(call)(\s+)(:\w+)', (Token_Keyword, Token_Text, Token_Name)),
            (r'(goto)(\s+)(\w+)', (Token_Keyword, Token_Text, Token_Name)),
            (r'\b(set|call|echo|on|off|endlocal|for|do|goto|if|pause|'
             r'setlocal|shift|errorlevel|exist|defined|cmdextversion|'
             r'errorlevel|else|cd|md|del|deltree|cls|choice)\b', Token_Keyword),
            (r'\b(equ|neq|lss|leq|gtr|geq)\b', Token_Keyword),
            (r'".*?"', Token_String),
            (r"'.*?'", Token_String),
            (r'`.*?`', Token_String),
            (r'-?\d+', Token_Number),
            (r',', Token_Text),
            (r'=', Token_Text),
            (r'/\S+', Token_Name),
            (r':\w+', Token_Name),
            (r'\w:\w+', Token_Text),
            (r'([<>|])(\s*)(\w+)', (Token_Text, Token_Text, Token_Name)),
            (None,Token_Text),
        ]


#----------------------------------------------------------

## SQL のシンタックス解析クラス
class SqlLexer(RegexLexer):
    
    def __init__(self):
    
        RegexLexer.__init__(self)
        
        self.re_flags = re.IGNORECASE

        self.rule_map['multiline_comment'] = [
            # (r'/\*', Token_Comment), # FIXME : コメントのネストを解釈していない
            (r'\*/', Token_Comment, 'root'),
            (None, Token_Comment),
        ]

        self.rule_map['root'] = [
            (r'\s+', Token_Text),
            (r'--.*?\n', Token_Comment),
            (r'/\*', Token_Comment, 'multiline_comment'),
            (r'\b(ABORT|ABS|ABSOLUTE|ACCESS|ADA|ADD|ADMIN|AFTER|AGGREGATE|'
             r'ALIAS|ALL|ALLOCATE|ALTER|ANALYSE|ANALYZE|AND|ANY|ARE|AS|'
             r'ASC|ASENSITIVE|ASSERTION|ASSIGNMENT|ASYMMETRIC|AT|ATOMIC|'
             r'AUTHORIZATION|AVG|BACKWARD|BEFORE|BEGIN|BETWEEN|BITVAR|'
             r'BIT_LENGTH|BOTH|BREADTH|BY|C|CACHE|CALL|CALLED|CARDINALITY|'
             r'CASCADE|CASCADED|CASE|CAST|CATALOG|CATALOG_NAME|CHAIN|'
             r'CHARACTERISTICS|CHARACTER_LENGTH|CHARACTER_SET_CATALOG|'
             r'CHARACTER_SET_NAME|CHARACTER_SET_SCHEMA|CHAR_LENGTH|CHECK|'
             r'CHECKED|CHECKPOINT|CLASS|CLASS_ORIGIN|CLOB|CLOSE|CLUSTER|'
             r'COALSECE|COBOL|COLLATE|COLLATION|COLLATION_CATALOG|'
             r'COLLATION_NAME|COLLATION_SCHEMA|COLUMN|COLUMN_NAME|'
             r'COMMAND_FUNCTION|COMMAND_FUNCTION_CODE|COMMENT|COMMIT|'
             r'COMMITTED|COMPLETION|CONDITION_NUMBER|CONNECT|CONNECTION|'
             r'CONNECTION_NAME|CONSTRAINT|CONSTRAINTS|CONSTRAINT_CATALOG|'
             r'CONSTRAINT_NAME|CONSTRAINT_SCHEMA|CONSTRUCTOR|CONTAINS|'
             r'CONTINUE|CONVERSION|CONVERT|COPY|CORRESPONTING|COUNT|'
             r'CREATE|CREATEDB|CREATEUSER|CROSS|CUBE|CURRENT|CURRENT_DATE|'
             r'CURRENT_PATH|CURRENT_ROLE|CURRENT_TIME|CURRENT_TIMESTAMP|'
             r'CURRENT_USER|CURSOR|CURSOR_NAME|CYCLE|DATA|DATABASE|'
             r'DATETIME_INTERVAL_CODE|DATETIME_INTERVAL_PRECISION|DAY|'
             r'DEALLOCATE|DECLARE|DEFAULT|DEFAULTS|DEFERRABLE|DEFERRED|'
             r'DEFINED|DEFINER|DELETE|DELIMITER|DELIMITERS|DEREF|DESC|'
             r'DESCRIBE|DESCRIPTOR|DESTROY|DESTRUCTOR|DETERMINISTIC|'
             r'DIAGNOSTICS|DICTIONARY|DISCONNECT|DISPATCH|DISTINCT|DO|'
             r'DOMAIN|DROP|DYNAMIC|DYNAMIC_FUNCTION|DYNAMIC_FUNCTION_CODE|'
             r'EACH|ELSE|ENCODING|ENCRYPTED|END|END-EXEC|EQUALS|ESCAPE|EVERY|'
             r'EXCEPT|ESCEPTION|EXCLUDING|EXCLUSIVE|EXEC|EXECUTE|EXISTING|'
             r'EXISTS|EXPLAIN|EXTERNAL|EXTRACT|FALSE|FETCH|FINAL|FIRST|FOR|'
             r'FORCE|FOREIGN|FORTRAN|FORWARD|FOUND|FREE|FREEZE|FROM|FULL|'
             r'FUNCTION|G|GENERAL|GENERATED|GET|GLOBAL|GO|GOTO|GRANT|GRANTED|'
             r'GROUP|GROUPING|HANDLER|HAVING|HIERARCHY|HOLD|HOST|IDENTITY|'
             r'IGNORE|ILIKE|IMMEDIATE|IMMUTABLE|IMPLEMENTATION|IMPLICIT|IN|'
             r'INCLUDING|INCREMENT|INDEX|INDITCATOR|INFIX|INHERITS|INITIALIZE|'
             r'INITIALLY|INNER|INOUT|INPUT|INSENSITIVE|INSERT|INSTANTIABLE|'
             r'INSTEAD|INTERSECT|INTO|INVOKER|IS|ISNULL|ISOLATION|ITERATE|JOIN|'
             r'KEY|KEY_MEMBER|KEY_TYPE|LANCOMPILER|LANGUAGE|LARGE|LAST|'
             r'LATERAL|LEADING|LEFT|LENGTH|LESS|LEVEL|LIKE|LIMIT|LISTEN|LOAD|'
             r'LOCAL|LOCALTIME|LOCALTIMESTAMP|LOCATION|LOCATOR|LOCK|LOWER|'
             r'MAP|MATCH|MAX|MAXVALUE|MESSAGE_LENGTH|MESSAGE_OCTET_LENGTH|'
             r'MESSAGE_TEXT|METHOD|MIN|MINUTE|MINVALUE|MOD|MODE|MODIFIES|'
             r'MODIFY|MONTH|MORE|MOVE|MUMPS|NAMES|NATIONAL|NATURAL|NCHAR|'
             r'NCLOB|NEW|NEXT|NO|NOCREATEDB|NOCREATEUSER|NONE|NOT|NOTHING|'
             r'NOTIFY|NOTNULL|NULL|NULLABLE|NULLIF|OBJECT|OCTET_LENGTH|OF|OFF|'
             r'OFFSET|OIDS|OLD|ON|ONLY|OPEN|OPERATION|OPERATOR|OPTION|OPTIONS|'
             r'OR|ORDER|ORDINALITY|OUT|OUTER|OUTPUT|OVERLAPS|OVERLAY|OVERRIDING|'
             r'OWNER|PAD|PARAMETER|PARAMETERS|PARAMETER_MODE|PARAMATER_NAME|'
             r'PARAMATER_ORDINAL_POSITION|PARAMETER_SPECIFIC_CATALOG|'
             r'PARAMETER_SPECIFIC_NAME|PARAMATER_SPECIFIC_SCHEMA|PARTIAL|'
             r'PASCAL|PENDANT|PLACING|PLI|POSITION|POSTFIX|PRECISION|PREFIX|'
             r'PREORDER|PREPARE|PRESERVE|PRIMARY|PRIOR|PRIVILEGES|PROCEDURAL|'
             r'PROCEDURE|PUBLIC|READ|READS|RECHECK|RECURSIVE|REF|REFERENCES|'
             r'REFERENCING|REINDEX|RELATIVE|RENAME|REPEATABLE|REPLACE|RESET|'
             r'RESTART|RESTRICT|RESULT|RETURN|RETURNED_LENGTH|'
             r'RETURNED_OCTET_LENGTH|RETURNED_SQLSTATE|RETURNS|REVOKE|RIGHT|'
             r'ROLE|ROLLBACK|ROLLUP|ROUTINE|ROUTINE_CATALOG|ROUTINE_NAME|'
             r'ROUTINE_SCHEMA|ROW|ROWS|ROW_COUNT|RULE|SAVE_POINT|SCALE|SCHEMA|'
             r'SCHEMA_NAME|SCOPE|SCROLL|SEARCH|SECOND|SECURITY|SELECT|SELF|'
             r'SENSITIVE|SERIALIZABLE|SERVER_NAME|SESSION|SESSION_USER|SET|'
             r'SETOF|SETS|SHARE|SHOW|SIMILAR|SIMPLE|SIZE|SOME|SOURCE|SPACE|'
             r'SPECIFIC|SPECIFICTYPE|SPECIFIC_NAME|SQL|SQLCODE|SQLERROR|'
             r'SQLEXCEPTION|SQLSTATE|SQLWARNINIG|STABLE|START|STATE|STATEMENT|'
             r'STATIC|STATISTICS|STDIN|STDOUT|STORAGE|STRICT|STRUCTURE|STYPE|'
             r'SUBCLASS_ORIGIN|SUBLIST|SUBSTRING|SUM|SYMMETRIC|SYSID|SYSTEM|'
             r'SYSTEM_USER|TABLE|TABLE_NAME| TEMP|TEMPLATE|TEMPORARY|TERMINATE|'
             r'THAN|THEN|TIMESTAMP|TIMEZONE_HOUR|TIMEZONE_MINUTE|TO|TOAST|'
             r'TRAILING|TRANSATION|TRANSACTIONS_COMMITTED|'
             r'TRANSACTIONS_ROLLED_BACK|TRANSATION_ACTIVE|TRANSFORM|'
             r'TRANSFORMS|TRANSLATE|TRANSLATION|TREAT|TRIGGER|TRIGGER_CATALOG|'
             r'TRIGGER_NAME|TRIGGER_SCHEMA|TRIM|TRUE|TRUNCATE|TRUSTED|TYPE|'
             r'UNCOMMITTED|UNDER|UNENCRYPTED|UNION|UNIQUE|UNKNOWN|UNLISTEN|'
             r'UNNAMED|UNNEST|UNTIL|UPDATE|UPPER|USAGE|USER|'
             r'USER_DEFINED_TYPE_CATALOG|USER_DEFINED_TYPE_NAME|'
             r'USER_DEFINED_TYPE_SCHEMA|USING|VACUUM|VALID|VALIDATOR|VALUES|'
             r'VARIABLE|VERBOSE|VERSION|VIEW|VOLATILE|WHEN|WHENEVER|WHERE|'
             r'WITH|WITHOUT|WORK|WRITE|YEAR|ZONE)\b', Token_Keyword),
            (r'\b(ARRAY|BIGINT|BINARY|BIT|BLOB|BOOLEAN|CHAR|CHARACTER|DATE|'
             r'DEC|DECIMAL|FLOAT|INT|INTEGER|INTERVAL|NUMBER|NUMERIC|REAL|'
             r'SERIAL|SMALLINT|VARCHAR|VARYING|INT8|SERIAL8|TEXT)\b',
             Token_Name),
            #(r'[+*/<>=~!@#%^&|`?-]', Operator),
            (r'[0-9]+', Token_Number),
            # TODO: Backslash escapes?
            (r"'(''|[^'])*'", Token_String),
            (r'"(""|[^"])*"', Token_String), # not a real string literal in ANSI SQL
            #(r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
            #(r'[;:()\[\],\.]', Punctuation),
            (None, Token_Text),
        ]


#----------------------------------------------------------

def test():
    
    ctx = rootContext()
    
    if 0:
        lexer = PythonLexer()
        lines = [
        
            "import os",
            "import sys",
        
            "'''",
            "abc",
            "'''",
        ]
        
    if 0:
        lexer = CppLexer()
        lines = [
            "// comment",
            '#include "python.h"'
        ]
    
    if 1:
        lexer = CsharpLexer()
        lines = [
            'using System;'
        ]
    
    for line in lines:
        
        tokens, ctx = lexer.lex( ctx, line, True )
    
        for i in range(len(tokens)):
            pos1 = tokens[i][0]
            if i+1 < len(tokens):
                pos2 = tokens[i+1][0]
            else:
                pos2 = len(line)
            print( "  %s %s" % ( tokens[i][1], line[pos1:pos2] ) )

if debug:
    test()

## @} textwidget

