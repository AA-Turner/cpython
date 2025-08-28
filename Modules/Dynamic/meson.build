dynamic_module_tgts = []
foreach moduleset : dynamic_modules
  foreach module : moduleset
    deps = []
    if 'deps' in module
      deps += module['deps']
    endif

    name = '@0@.@1@'.format(module['name'], soabi)
    dynamic_module_tgts += shared_library(name, module['sources'],
      include_directories: [ private_inc ],
      dependencies: [
        libpython_dep,
        deps
      ],
      name_prefix: '',
      install: true,
      install_dir: get_option('libdir') / 'python@0@'.format(py_release) / 'lib-dynload'
    )
  endforeach
endforeach
