frozen_bootstrap = [
  # We manually freeze getpath.py rather than through freeze_modules
  { 'name': 'getpath', 'in': 'Modules/getpath.py', 'out': 'getpath.h' },

  { 'name': 'importlib__bootstrap', 'in': 'Lib/importlib/_bootstrap.py', 'out': 'importlib._bootstrap.h' },
  { 'name': 'importlib__bootstrap_external', 'in': 'Lib/importlib/_bootstrap_external.py', 'out': 'importlib._bootstrap_external.h' },
  { 'name': 'zipimport', 'in': 'Lib/zipimport.py', 'out': 'zipimport.h' },
]

frozen = [
  { 'name': 'abc', 'in': 'Lib/abc.py', 'out': 'abc.h' },
  { 'name': 'codecs', 'in': 'Lib/codecs.py', 'out': 'codecs.h' },
  { 'name': 'io', 'in': 'Lib/io.py', 'out': 'io.h' },
  { 'name': '_collections_abc', 'in': 'Lib/_collections_abc.py', 'out': '_collections_abc.h' },
  { 'name': '_sitebuiltins', 'in': 'Lib/_sitebuiltins.py', 'out': '_sitebuiltins.h' },
  { 'name': 'genericpath', 'in': 'Lib/genericpath.py', 'out': 'genericpath.h' },
  { 'name': 'ntpath', 'in': 'Lib/ntpath.py', 'out': 'ntpath.h' },
  { 'name': 'posixpath', 'in': 'Lib/posixpath.py', 'out': 'posixpath.h' },
  { 'name': 'os', 'in': 'Lib/os.py', 'out': 'os.h' },
  { 'name': 'site', 'in': 'Lib/site.py', 'out': 'site.h' },
  { 'name': 'stat', 'in': 'Lib/stat.py', 'out': 'stat.h' },
  { 'name': 'importlib_util', 'in': 'Lib/importlib/util.py', 'out': 'importlib.util.h' },
  { 'name': 'importlib_machinery', 'in': 'Lib/importlib/machinery.py', 'out': 'importlib.machinery.h' },
  { 'name': 'runpy', 'in': 'Lib/runpy.py', 'out': 'runpy.h' },
  { 'name': '__hello__', 'in': 'Lib/__hello__.py', 'out': '__hello__.h' },
  { 'name': '__phello__', 'in': 'Lib/__phello__/__init__.py', 'out': '__phello__.h' },
  { 'name': '__phello___ham', 'in': 'Lib/__phello__/ham/__init__.py', 'out': '__phello__.ham.h' },
  { 'name': '__phello___ham_eggs', 'in': 'Lib/__phello__/ham/eggs.py', 'out': '__phello__.ham.eggs.h' },
  { 'name': '__phello___spam', 'in': 'Lib/__phello__/spam.py', 'out': '__phello__.spam.h' },
  { 'name': 'frozen_only', 'in': 'Tools/freeze/flag.py', 'out': 'frozen_only.h' },
]

frozen_tgts = []

if meson.can_run_host_binaries()
  freezer = executable('_freeze_module', meson.project_source_root() / 'Programs' / '_freeze_module.c', meson.project_source_root() / 'Modules' / 'getpath_noop.c',
    c_args: [ '-DPy_BUILD_CORE' ],
    include_directories: [ inc, private_inc ],
    link_with: [ python_objects_lib, python_python_lib_omit_frozen ],
    dependencies: [
      python_modules_dep,
      libm_dep
    ],
    install: false
  )
  foreach file : frozen_bootstrap
    frozen_tgts += custom_target(file['out'],
      output: file['out'],
      input: meson.project_source_root() / file['in'],
      command: [freezer, file['name'], '@INPUT0@', '@OUTPUT@']
    )
  endforeach

  bootstrap_path_cfg = configuration_data()
  bootstrap_path_cfg.set_quoted('MODULE_STDLIB_DIR', meson.project_source_root() / 'Lib')
  bootstrap_path_cfg.set_quoted('MODULE_PLATLIB_DIR', meson.project_build_root() / 'Modules' / 'Dynamic')

  bootstrap_python_src = configure_file(
    input: meson.project_source_root() / 'Programs' / '_bootstrap_python.c.in',
    output: '_bootstrap_python.c',
    configuration: bootstrap_path_cfg
  )

  bootstrap_python = executable('_bootstrap_python', bootstrap_python_src, meson.project_source_root() / 'Modules' / 'getpath.c', frozen_tgts,
    c_args: [ '-DPy_BUILD_CORE' ],
    include_directories: [ inc, private_inc ],
    link_with: [ python_objects_lib, python_python_lib_omit_frozen ],
    dependencies: [
      python_modules_dep,
      libm_dep
    ],
    install: false
  )

  foreach file : frozen
    frozen_tgts += custom_target(file['out'],
      output: file['out'],
      input: meson.project_source_root() / file['in'],
      command: [bootstrap_python, meson.project_source_root() / 'Programs' / '_freeze_module.py', file['name'], '@INPUT0@', '@OUTPUT@']
    )
  endforeach
else
  build_python = find_program(get_option('cross-build-machine-python'), version: [ '>= @0@'.format(py_release), '< @0@.@1@'.format(version_components[0], version_components[1].to_int()+1) ], native: true)
  foreach set : [frozen_bootstrap, frozen]
    foreach file : set
      frozen_tgts += custom_target(file['out'],
        output: file['out'],
        input: meson.project_source_root() / file['in'],
        command: [build_python, meson.project_source_root() / 'Programs' / '_freeze_module.py', file['name'], '@INPUT0@', '@OUTPUT@']
      )
    endforeach
  endforeach
endif
