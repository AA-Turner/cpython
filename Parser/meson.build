parser_src = [
	'action_helpers.c',
	'lexer/buffer.c',
	'lexer/lexer.c',
	'lexer/state.c',
	'myreadline.c',
	'parser.c',
	'peg_api.c',
	'pegen.c',
	'pegen_errors.c',
	'string_parser.c',
	'token.c',
	'tokenizer/file_tokenizer.c',
	'tokenizer/helpers.c',
	'tokenizer/readline_tokenizer.c',
	'tokenizer/string_tokenizer.c',
	'tokenizer/utf8_tokenizer.c'
]

python_parser_lib = static_library('python-parser', parser_src,
	c_args: [ '-DPy_BUILD_CORE' ],
	include_directories: [ inc, private_inc ]
)
