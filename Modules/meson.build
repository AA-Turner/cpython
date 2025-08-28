modules_src = [
  'main.c',
  'gcmodule.c',
  'getbuildinfo.c'
]

# Built-in modules required to get a functioning interpreter;
# cannot be built as shared!
bootstrap_modules = [
  # module C APIs are used in core
  { 'name': 'atexit', 'sources': [ 'atexitmodule.c' ] },
  { 'name': 'faulthandler', 'sources': [ 'faulthandler.c' ] },
  { 'name': 'posix', 'sources': [ 'posixmodule.c' ] },
  { 'name': '_signal', 'sources': [ 'signalmodule.c' ] },
  { 'name': '_tracemalloc', 'sources': [ '_tracemalloc.c' ] },
  { 'name': '_suggestions', 'sources': [ '_suggestions.c' ] },

  # modules used by importlib, deepfreeze, freeze, runpy, and sysconfig
  { 'name': '_codecs', 'sources': [ '_codecsmodule.c' ] },
  { 'name': '_collections', 'sources': [ '_collectionsmodule.c' ] },
  { 'name': 'errno', 'sources': [ 'errnomodule.c' ] },
  { 'name': '_io', 'sources': [ '_io/_iomodule.c', '_io/iobase.c', '_io/fileio.c', '_io/bytesio.c', '_io/bufferedio.c', '_io/textio.c', '_io/stringio.c' ] },
  { 'name': 'itertools', 'sources': [ 'itertoolsmodule.c' ] },
  { 'name': '_sre', 'sources': [ '_sre/sre.c' ] },
  { 'name': '_sysconfig', 'sources': [ '_sysconfig.c' ] },
  { 'name': '_thread', 'sources': [ '_threadmodule.c' ] },
  { 'name': 'time', 'sources': [ 'timemodule.c' ] },
  { 'name': '_typing', 'sources': [ '_typingmodule.c' ] },
  { 'name': '_weakref', 'sources': [ '_weakref.c' ] },

  # commonly used core modules
  { 'name': '_abc', 'sources': [ '_abc.c' ] },
  { 'name': '_functools', 'sources': [ '_functoolsmodule.c' ] },
  { 'name': '_locale', 'sources': [ '_localemodule.c' ] },
  { 'name': '_opcode', 'sources': [ '_opcode.c' ] },
  { 'name': '_operator', 'sources': [ '_operator.c' ] },
  { 'name': '_stat', 'sources': [ '_stat.c' ] },
  { 'name': '_symtable', 'sources': [ 'symtablemodule.c' ] },
]

module_pwd = true #TODO
if module_pwd
  # for systems without $HOME env, used by site._getuserbase()
  bootstrap_modules += { 'name': '', 'sources': [ 'pwdmodule.c' ] }
endif

stdlib_modules = [
  # Modules that should always be present (POSIX and Windows):
  { 'name': 'array', 'sources': files([ 'arraymodule.c' ]) },
  { 'name': '_asyncio', 'sources': files([ '_asynciomodule.c' ]) },
  { 'name': '_bisect', 'sources': files([ '_bisectmodule.c' ]) },
  { 'name': '_contextvars', 'sources': files([ '_contextvarsmodule.c' ]) },
  { 'name': '_csv', 'sources': files([ '_csv.c' ]) },
  { 'name': '_heapq', 'sources': files([ '_heapqmodule.c' ]) },
  { 'name': '_json', 'sources': files([ '_json.c' ]) },
  { 'name': '_lsprof', 'sources': files([ '_lsprof.c', 'rotatingtree.c' ]) },
  { 'name': '_pickle', 'sources': files([ '_pickle.c' ]) },
  { 'name': '_queue', 'sources': files([ '_queuemodule.c' ]) },
  { 'name': '_random', 'sources': files([ '_randommodule.c' ]) },
  { 'name': '_struct', 'sources': files([ '_struct.c' ]) },

  # build supports subinterpreters
  { 'name': '_interpreters', 'sources': files([ '_interpretersmodule.c' ]) },
  { 'name': '_interpchannels', 'sources': files([ '_interpchannelsmodule.c' ]) },
  { 'name': '_interpqueues', 'sources': files([ '_interpqueuesmodule.c' ]) },

  { 'name': '_zoneinfo', 'sources': files([ '_zoneinfo.c' ]) },

  # needs libm
  { 'name': 'math', 'sources': files([ 'mathmodule.c' ]), 'deps': [ libm_dep ] },
  { 'name': 'cmath', 'sources': files([ 'cmathmodule.c' ]), 'deps': [ libm_dep ] },
  { 'name': '_statistics', 'sources': files([ '_statisticsmodule.c' ]), 'deps': [ libm_dep ] },

  # needs libm and on some platforms librt
  { 'name': '_datetime', 'sources': files([ '_datetimemodule.c' ]), 'deps': [ libm_dep, librt_dep ] },

  # _decimal uses libmpdec
  # either static libmpdec.a from Modules/_decimal/libmpdec or libmpdec.so
  # with ./configure --with-system-libmpdec
  { 'name': '_decimal', 'sources': files([ '_decimal/_decimal.c' ]), 'deps': [ libmpdec_dep ] },

  # compression libs and binascii (optional CRC32 from zlib)
  # bindings need -lbz2, -lz, or -llzma, respectively
  { 'name': 'binascii', 'sources': files([ 'binascii.c' ]) },
  { 'name': '_bz2', 'sources': files([ '_bz2module.c' ]), 'deps': [ bzip_dep ] },
  { 'name': '_lzma', 'sources': files([ '_lzmamodule.c' ]), 'deps': [ lzma_dep ] },
  { 'name': 'zlib', 'sources': files([ 'zlibmodule.c' ]), 'deps': [ zlib_dep ] },

  ############################################################################
  # XML and text

  # pyexpat module uses libexpat
  # either static libexpat.a from Modules/expat or libexpat.so with
  { 'name': 'pyexpat', 'sources': files([ 'pyexpat.c' ]), 'deps': [ expat_dep ] },
  # _elementtree libexpat via CAPI hook in pyexpat.
  { 'name': '_elementtree', 'sources': files([ '_elementtree.c' ]), 'deps': [ expat_dep.partial_dependency(includes: true) ] },

  { 'name': '_codecs_cn', 'sources': files([ 'cjkcodecs/_codecs_cn.c' ]) },
  { 'name': '_codecs_hk', 'sources': files([ 'cjkcodecs/_codecs_hk.c' ]) },
  { 'name': '_codecs_iso2022', 'sources': files([ 'cjkcodecs/_codecs_iso2022.c' ]) },
  { 'name': '_codecs_jp', 'sources': files([ 'cjkcodecs/_codecs_jp.c' ]) },
  { 'name': '_codecs_kr', 'sources': files([ 'cjkcodecs/_codecs_kr.c' ]) },
  { 'name': '_codecs_tw', 'sources': files([ 'cjkcodecs/_codecs_tw.c' ]) },
  { 'name': '_multibytecodec', 'sources': files([ 'cjkcodecs/multibytecodec.c' ]) },
  { 'name': 'unicodedata', 'sources': files([ 'unicodedata.c' ]) },

  ############################################################################
  # Modules with some UNIX dependencies
  #

  { 'name': 'fcntl', 'sources': files([ 'fcntlmodule.c' ]) },
  { 'name': 'grp', 'sources': files([ 'grpmodule.c' ]) },
  { 'name': 'mmap', 'sources': files([ 'mmapmodule.c' ]) },
  # needs sys/soundcard.h or linux/soundcard.h (Linux, FreeBSD)
  { 'name': '_posixsubprocess', 'sources': files([ '_posixsubprocess.c' ]) },
  { 'name': 'resource', 'sources': files([ 'resource.c' ]) },
  { 'name': 'select', 'sources': files([ 'selectmodule.c' ]) },
  { 'name': '_socket', 'sources': files([ 'socketmodule.c' ]) },
  { 'name': 'syslog', 'sources': files([ 'syslogmodule.c' ]) },
  { 'name': 'termios', 'sources': files([ 'termios.c' ]) },

  # multiprocessing
  { 'name': '_posixshmem', 'sources': files([ '_multiprocessing/posixshmem.c' ]) },
  { 'name': '_multiprocessing', 'sources': files([ '_multiprocessing/multiprocessing.c', '_multiprocessing/semaphore.c' ]) },


  ############################################################################
  # Modules with third party dependencies
  #

  # needs -lffi and -ldl
  { 'name': '_ctypes', 'sources': files([ '_ctypes/_ctypes.c', '_ctypes/callbacks.c', '_ctypes/callproc.c', '_ctypes/stgdict.c', '_ctypes/cfield.c', host_machine.system() == 'darwin' ? '_ctypes/malloc_closure.c' : [] ]), 'deps': [ ffi_dep, dl_dep, host_machine.system() == 'darwin' ? declare_dependency(compile_args: '-DUSING_MALLOC_CLOSURE_DOT_C=1') : [] ] },

  # needs -lssl and -lcrypt
  { 'name': '_ssl', 'sources': files([ '_ssl.c' ]), 'deps': [ openssl_dep ] },
  # needs -lcrypt
  { 'name': '_hashlib', 'sources': files([ '_hashopenssl.c' ]), 'deps': [ openssl_dep ] },
]

# dbm/gdbm
if libdbm_dep.found()
  # dbm needs either libndbm, libgdbm_compat, or libdb 5.x
  stdlib_modules += { 'name': '_dbm', 'sources': files([ '_dbmmodule.c' ]), 'deps': [ libdbm_dep ] }
endif
if libgdbm_dep.found()
  # gdbm module needs -lgdbm
  stdlib_modules += { 'name': '_gdbm', 'sources': files([ '_gdbmmodule.c' ]), 'deps': [ libgdbm_dep ] }
endif

if readline_dep.found()
  # needs -lreadline or -ledit, sometimes termcap, termlib, or tinfo
  stdlib_modules += { 'name': 'readline', 'sources': files([ 'readline.c' ]), 'deps': [ readline_dep.partial_dependency(includes: true, link_args: true, links: true) ] } # readline.pc adds -D_XOPEN_SOURCE=600 by default
endif

# hashing builtins, can be disabled with --without-builtin-hashlib-hashes
hacl_dep = declare_dependency(include_directories: include_directories([ '_hacl', '_hacl/include' ]))
stdlib_hashlib_modules = [
  { 'name': '_md5', 'key': 'md5', 'sources': files([ 'md5module.c', '_hacl/Hacl_Hash_MD5.c' ]), 'deps': [ hacl_dep ] },
  { 'name': '_sha1', 'key': 'sha1', 'sources': files([ 'sha1module.c', '_hacl/Hacl_Hash_SHA1.c' ]), 'deps': [ hacl_dep ] },
  { 'name': '_sha2', 'key': 'sha2', 'sources': files([ 'sha2module.c', '_hacl/Hacl_Hash_SHA2.c' ]), 'deps': [ hacl_dep ] },
  { 'name': '_sha3', 'key': 'sha3', 'sources': files([ 'sha3module.c', '_hacl/Hacl_Hash_SHA3.c' ]), 'deps': [ hacl_dep ] },
  { 'name': '_blake2', 'key': 'blake2', 'sources': files([
      'blake2module.c',
      '_hacl/Hacl_Hash_Blake2b.c',
      '_hacl/Hacl_Hash_Blake2s.c',
      hacl_can_compile_simd128 ? '_hacl/Hacl_Hash_Blake2s_Simd128.c' : [],
      hacl_can_compile_simd256 ? '_hacl/Hacl_Hash_Blake2b_Simd256.c' : [],
      '_hacl/Lib_Memzero0.c'
    ]), 'deps': [ hacl_dep, declare_dependency(compile_args: [
      hacl_can_compile_simd128 ? hacl_simd128_args + ['-DHACL_CAN_COMPILE_VEC128'] : [],
      hacl_can_compile_simd256 ? hacl_simd256_args + ['-DHACL_CAN_COMPILE_VEC256'] : [],
      have_explicit_bzero ? [] : '-DLINUX_NO_EXPLICIT_BZERO'])
  ] }
]
foreach module : stdlib_hashlib_modules
  if get_option('builtin-hashlib-hashes').contains(module['key'])
    stdlib_modules += module
  endif
endforeach


if sqlite3_dep.found()
  stdlib_modules += {
    'name': '_sqlite3',
    'sources': files([
      '_sqlite/blob.c',
      '_sqlite/connection.c',
      '_sqlite/cursor.c',
      '_sqlite/microprotocols.c',
      '_sqlite/module.c',
      '_sqlite/prepare_protocol.c',
      '_sqlite/row.c',
      '_sqlite/statement.c',
      '_sqlite/util.c'
    ]),
    'deps': [ sqlite3_dep ]
  }
endif

if have_uuid
  # Linux: -luuid, BSD/AIX: libc's uuid_create()
  stdlib_modules += { 'name': '_uuid', 'sources': files([ '_uuidmodule.c' ]), 'deps': [ uuid_dep ] }
endif

if tcl_dep.found() and tk_dep.found()
  stdlib_modules += { 'name': '_tkinter', 'sources': files([ '_tkinter.c', 'tkappinit.c' ]), 'deps': [ tcl_dep, tk_dep, declare_dependency(compile_args: '-DWITH_APPINIT') ] }
endif

if ncurses_dep.found() and panel_dep.found()
  ncurses_dep_without_cargs = ncurses_dep.partial_dependency(includes: true, link_args: true, links: true)
  panel_dep_without_cargs = panel_dep.partial_dependency(includes: true, link_args: true, links: true)
  # needs -lncurses[w], sometimes -ltermcap/tinfo
  stdlib_modules += { 'name': '_curses', 'sources': files([ '_cursesmodule.c' ]), 'deps': [ ncurses_dep_without_cargs ] }
  # needs -lncurses[w] and -lpanel[w]
  stdlib_modules += { 'name': '_curses_panel', 'sources': files([ '_curses_panel.c' ]), 'deps': [ ncurses_dep_without_cargs, panel_dep_without_cargs ] }
endif


if host_machine.system() == 'darwin' and host_machine.subsstem() == 'macos'
  # _scproxy needs SystemConfiguration and CoreFoundation framework
  stdlib_modules += { 'name': '_scproxy', 'sources': files([ '_scproxy.c' ]) }
endif

if get_option('stdlib') == 'auto'
  if get_option('default_library') == 'shared'
    builtin_modules = [ bootstrap_modules ]
    dynamic_modules = [ stdlib_modules ]
  else # static & both
    builtin_modules = [ bootstrap_modules, stdlib_modules ]
    dynamic_modules = []
  endif
elif get_option('stdlib') == 'builtin'
  builtin_modules = [ bootstrap_modules, stdlib_modules ]
  dynamic_modules = []
elif get_option('stdlib') == 'dynamic'
  if get_option('default_library') != 'shared'
    error('-Dstdlib=dynamic is possible if building a shared library')
  endif
  builtin_modules = [ bootstrap_modules ]
  dynamic_modules = [ stdlib_modules ]
endif


builtin_names = []
builtin_sources = []
builtin_deps = []
foreach moduleset : builtin_modules
  foreach module : moduleset
    builtin_names += module['name']
    builtin_sources += module['sources']
    if 'deps' in module
      builtin_deps += module['deps']
    endif
  endforeach
endforeach

makemeson_config = custom_target('makemeson-config',
  output: 'config.c',
  command: [
    find_program('sh'), meson.current_source_dir() / 'makemeson',
    '-c', meson.current_source_dir () / 'config.c.in',
    '-o', '@OUTPUT@',
    '--', builtin_names
  ]
)

python_modules_lib = static_library('python-builtin-modules', modules_src, builtin_sources, makemeson_config,
  c_args: [ '-DPy_BUILD_CORE' ],
  include_directories: [ inc, private_inc, root_inc ],
  dependencies: builtin_deps
)

python_modules_dep = declare_dependency(
  dependencies: builtin_deps,
  link_whole: python_modules_lib
)
