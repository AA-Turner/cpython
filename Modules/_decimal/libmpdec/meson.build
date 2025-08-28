libmpdec_src = [
  'basearith.c',
  'constants.c',
  'context.c',
  'convolute.c',
  'crt.c',
  'difradix2.c',
  'fnt.c',
  'fourstep.c',
  'io.c',
  'mpalloc.c',
  'mpdecimal.c',
  'numbertheory.c',
  'sixstep.c',
  'transpose.c',
  # _decimal does not use signaling API
  #'mpsignal.c'
]

libmpdec_cargs = [ '-DUNIVERSAL' ]
libmpdec_inc = [ include_directories('.'), root_inc ]
libmpdec_lib = static_library('mpdec', libmpdec_src,
  c_args: libmpdec_cargs,
  include_directories: libmpdec_inc,
  dependencies: [ libm_dep ]
)
libmpdec_dep = declare_dependency(
  compile_args: libmpdec_cargs,
  include_directories: libmpdec_inc,
  link_with: libmpdec_lib,
  dependencies: [ libm_dep ]
)
