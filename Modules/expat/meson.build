expat_src = [
  'xmlparse.c',
  'xmlrole.c',
  'xmltok.c',
  'xmltok_impl.c',
  'xmltok_ns.c'
]

expat_lib = static_library('expat', expat_src,
  include_directories: [ root_inc ]
)
expat_dep = declare_dependency(
  include_directories: include_directories('.'),
  link_with: expat_lib
)
