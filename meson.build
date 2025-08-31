# Initialise Meson
project('Python', 'c',
  version: '3.15.0a0',
  default_options: ['warning_level=1', 'c_std=c11'],
  license: 'PSFv2',
  license_files: ['LICENSE'],
  meson_version: '>= 1.9.0',
)

#
# MESON MODULES
#
fs = import('fs')

message('Building Python version ' + meson.project_version())

version_components = meson.project_version().split('.')
py_release = '@0@.@1@'.format(version_components[0], version_components[1])

#
# OPTIONS
#

with_pydebug = get_option('buildtype') == 'debug'
with_gil = get_option('gil')
with_ipv6 = get_option('ipv6')
with_docstrings = get_option('doc-strings')
with_c_locale_coercion = get_option('c-locale-coercion')
with_decimal_contextvar = get_option('decimal-contextvar')
with_loadable_sqlite_extensions = get_option('loadable-sqlite-extensions')
with_system_libmpdec = get_option('system-libmpdec')
with_system_expat = get_option('system-expat')
enable_shared = get_option('enable-shared')
# TODO: fill in others

root_inc = include_directories('.')

#
# COMPILER DETECTION
#
compiler = meson.get_compiler('c')

#
# COMPILER OPTIONS
#

# PLAFORM TRIPLET

message('Checking for the platform triplet based on compiler characteristics')
platform_triplet = compiler.get_define(
  'TRIPLET',
  include_directories: include_directories('Misc'),
  prefix: '#include "platform_triplet.c"',
)
# TODO calculate MULTIARCH, SOABI,

#
# Dependencies
#
# Can be found in PCBuild/get_externals.bat
#

if false
libm_dep = compiler.find_library('m', required: false)
librt_dep = compiler.find_library('rt', required: false)

libmpdec_dep = compiler.find_library('mpdec', required: with_system_libmpdec)

#bzip_dep = dependency('bz2')
lzma_dep = dependency('liblzma')
zlib_dep = dependency('zlib')

libdbm_dep = dependency('', required: false)
dbm_libs = {
  'ndbm': { 'lib': 'ndbm', 'cflags': '-DUSE_NDBM', 'headers': [ 'ndbm.h' ] },
  'gdbm': { 'lib': 'gdbm_compat', 'cflags': '-DUSE_GDBM_COMPAT', 'headers': [ 'gdbm/ndbm.h', 'gdbm-ndbm.h' ] },
  'bdb': { 'lib': 'db', 'cflags': '-DUSE_BERKDB', 'headers': [ 'db.h' ] }
}
foreach dbm_lib : get_option('dbm-lib-order')
  dep = compiler.find_library(dbm_libs[dbm_lib]['lib'], required: false)
  has_header = false
  foreach header : dbm_libs[dbm_lib]['headers']
    if compiler.has_header(header, dependencies: dep)
      has_header = true
      break
    endif
  endforeach
  if dep.found() and has_header
    libdbm_dep = declare_dependency(
      compile_args: dbm_libs[dbm_lib]['cflags'],
      dependencies: dep
    )
    break
  endif
endforeach
libgdbm_dep = compiler.find_library('gdbm', required: false)

readline_dep = dependency('readline', required: false)
expat_dep = dependency('expat', required: get_option('system-expat'))
ffi_dep = dependency('libffi')
dl_dep = dependency('dl', required: false)

ncurses_dep = dependency('ncursesw', required: false)
panel_dep = dependency('panelw', required: false)
have_ncursesw = ncurses_dep.found()
have_panelw = panel_dep.found()
if not ncurses_dep.found()
  ncurses_dep = dependency('ncurses', required: false)
endif
if not panel_dep.found()
  panel_dep = dependency('panel', required: false)
endif

sqlite3_dep = dependency('sqlite3', version: '>= 3.15.2', required: false)
openssl_dep = dependency('openssl')
ssl_lib = compiler.find_library('ssl', required: false)
crypto_lib = compiler.find_library('crypto', required: false)
uuid_dep = dependency('uuid', version: '>= 2.20', required: false)

tcl_dep = dependency('tcl', version: '>= 8.5.12', required: false)
tk_dep = dependency('tk', version: '>= 8.5.12', required: false)
endif

#
# INCLUDE PATHS
#


# We need to make sure the following resources get picked up before
# their $SRCDIR counterparts:
#
#   Objects/ -> typeslots.inc
#   Include/ -> Python.h
#
base_includes = include_directories(
  'Objects',
  'Include',
  'Include' / 'internal',
  'Python',
)

# GIT
# TODO: investigate https://mesonbuild.com/Reference-manual_functions.html#vcs_tag
#git = find_program('git', required: false, native: true)
if false and git.found() and fs.exists(meson.project_source_root() / '.git')
  git_version = run_command(git, 'rev-parse', '--short', 'HEAD', check: true).stdout()
  git_tag = run_command(git, 'describe', '--all', '--always', '--dirty', check: true).stdout()
  git_branch = run_command(git, 'name-rev', '--name-only', 'HEAD', check: true).stdout()
else
  git_version = ''
  git_tag = ''
  git_branch = ''
endif

#rm = find_program('rm', required: false, native: true)
#run_command(rm, 'pybuilddir.txt', check: false)

# PYTHON FOR FREEZE
message('checking for Python interpreter freezing...')

# PYTHON FOR REGEN
foreach test_pfr : [
  'python' + meson.project_version(),
  'python3.15',
  'python3.14',
  'python3.13',
  'python3.12',
  'python3.11',
  'python3.10',
  'python',
  'python3',
]
  python_for_regen = find_program(test_pfr, required: false, native: true)
  if python_for_regen.found()
    message('Found Python interpreter for regen: ' + python_for_regen.full_path())
    break
  endif
endforeach

feature_flags = [
#  '-D_NETBSD_SOURCE',
#  '-D__BSD_VISIBLE',
#  '-D_DARWIN_C_SOURCE',
  '-D_XOPEN_SOURCE=700',
  '-D_XOPEN_SOURCE_EXTENDED',
  '-D_POSIX_C_SOURCE=200809L',
  '-D_ALL_SOURCE',
#  '-D_DARWIN_C_SOURCE',
  '-D_GNU_SOURCE',
  '-D_HPUX_ALT_XOPEN_SOCKET_API',
#  '-D_NETBSD_SOURCE',
  '-D_OPENBSD_SOURCE',
  '-D_POSIX_PTHREAD_SEMANTICS',
]
# TODO define_xopen_source

## these sadly don't count for the compiler check methods
#add_project_arguments(feature_flags, language: 'c')

cfg = configuration_data()
# The later definition of _XOPEN_SOURCE and _POSIX_C_SOURCE disables
# certain features on NetBSD, so we need _NETBSD_SOURCE to re-enable
# them.
cfg.set10(
  '_NETBSD_SOURCE', true,
  description: 'Define on NetBSD to activate all library features',
)
# The later definition of _XOPEN_SOURCE and _POSIX_C_SOURCE disables
# certain features on FreeBSD, so we need __BSD_VISIBLE to re-enable
# them.
cfg.set10(
  '__BSD_VISIBLE', true,
  description: 'Define on FreeBSD to activate all library features',
)
# The later definition of _XOPEN_SOURCE and _POSIX_C_SOURCE disables
# certain features on Mac OS X, so we need _DARWIN_C_SOURCE to re-enable
# them.
cfg.set10(
  '_DARWIN_C_SOURCE', true,
  description: 'Define on Darwin to activate all library features',
)

if enable_shared
  PY_ENABLE_SHARED = true
  cfg.set10('Py_ENABLE_SHARED', true,
    description: 'Defined if Python is built as a shared library.')



endif

error('!!!')

# autoconf 2.71 deprecates STDC_HEADERS, keep for backwards compatibility
# assume C99 compilers provide ANSI C headers
cfg.set10('STDC_HEADERS', true,
  description: 'Define to 1 if you have the ANSI C header files.')


cfg.set('HAVE_STDIO_H', compiler.has_header('stdio.h'))
cfg.set('HAVE_STDLIB_H', compiler.has_header('stdlib.h'))
cfg.set('HAVE_STRING_H', compiler.has_header('string.h'))
cfg.set('HAVE_INTTYPES_H', compiler.has_header('inttypes.h'))
cfg.set('HAVE_STDINT_H', compiler.has_header('stdint.h'))
cfg.set('HAVE_STRINGS_H', compiler.has_header('strings.h'))
cfg.set('HAVE_SYS_STAT_H', compiler.has_header('sys/stat.h'))
have_sys_types_h = compiler.has_header('sys/types.h')
cfg.set('HAVE_SYS_TYPES_H', have_sys_types_h)
cfg.set('HAVE_UNISTD_H', compiler.has_header('sys/unistd.h'))
have_wchar_h = compiler.has_header('wchar.h')
cfg.set('HAVE_WCHAR_H', have_wchar_h)
cfg.set('HAVE_MINIX_CONFIG_H', compiler.has_header('minix/config.h'))

cfg.set('PY_SUPPORT_TIER', 0) # Building python with meson is currently not officially supported
cfg.set('Py_GIL_DISABLED', not get_option('gil'))
cfg.set('Py_DEBUG', with_pydebug)
abiflags = (get_option('gil') ? '' : 't') + (with_pydebug ? 'd' : '')
abi = '@0@-@1@'.format(host_machine.cpu_family(), host_machine.system())
soabi = '@0@-@1@@2@-@3@'.format(meson.project_name(), py_release.replace('.', ''), abiflags, abi)
if platform_triplet != '' and (false and platform_triplet != MULTIARCH)
  cfg.set_quoted('MULTIARCH', platform_triplet)
endif
cfg.set_quoted('SOABI', soabi)
if with_pydebug
  cfg.set_quoted('ALT_SOABI', '@0@-@1@@2@-@3@'.format(meson.project_name(), py_release.replace('.', ''), abiflags.replace('d', ''), abi))
endif

cfg.set_quoted('_PYTHONFRAMEWORK', '')
cfg.set_quoted('PREFIX', get_option('prefix'))
cfg.set_quoted('EXEC_PREFIX', get_option('prefix'))
cfg.set_quoted('VERSION', meson.project_version())
cfg.set_quoted('VPATH', '')
cfg.set_quoted('PLATLIBDIR', get_option('prefix') / get_option('libdir'))

liblog_dep = declare_dependency()
if host_machine.system() == 'android'
  cfg.set('ANDROID_API_LEVEL', compiler.get_define('__ANDROID_API__'))
  liblog_dep = compiler.find_library('log')
endif

cfg.set('HAVE_ALLOCA_H', compiler.has_header('alloca.h'))
cfg.set('HAVE_ASM_TYPES_H', compiler.has_header('asm/types.h'))
cfg.set('HAVE_BLUETOOTH_H', compiler.has_header('bluetooth.h'))
cfg.set('HAVE_CONIO_H', compiler.has_header('conio.h'))
cfg.set('HAVE_DIRECT_H', compiler.has_header('direct.h'))
cfg.set('HAVE_DLFCN_H', compiler.has_header('dlfcn.h'))
have_endian_h = compiler.has_header('endian.h')
cfg.set('HAVE_ENDIAN_H', have_endian_h)
cfg.set('HAVE_ERRNO_H', compiler.has_header('errno.h'))
cfg.set('HAVE_FCNTL_H', compiler.has_header('fcntl.h'))
have_grp_h = compiler.has_header('grp.h')
cfg.set('HAVE_GRP_H', have_grp_h)
cfg.set('HAVE_IO_H', compiler.has_header('io.h'))
cfg.set('HAVE_LANGINFO_H', compiler.has_header('langinfo.h'))
cfg.set('HAVE_LIBINTL_H', compiler.has_header('libintl.h'))
cfg.set('HAVE_LIBUTIL_H', compiler.has_header('libutil.h'))
cfg.set('HAVE_LINUX_AUXVEC_H', compiler.has_header('linux/auxvec.h'))
cfg.set('HAVE_SYS_AUXV_H', compiler.has_header('sys/auxv.h'))
cfg.set('HAVE_LINUX_FS_H', compiler.has_header('linux/fs.h'))
cfg.set('HAVE_LINUX_LIMITS_H', compiler.has_header('linux/limits.h'))
cfg.set('HAVE_LINUX_MEMFD_H', compiler.has_header('linux/memfd.h'))
cfg.set('HAVE_LINUX_NETFILTER_IPV4_H', compiler.has_header('linux/netfilter_ipv4.h'))
cfg.set('HAVE_LINUX_RANDOM_H', compiler.has_header('linux/random.h'))
cfg.set('HAVE_LINUX_SOUNDCARD_H', compiler.has_header('linux/soundcard.h'))
cfg.set('HAVE_LINUX_SCHED_H', compiler.has_header('linux/sched.h'))
cfg.set('HAVE_LINUX_TIPC_H', compiler.has_header('linux/tipc.h'))
cfg.set('HAVE_LINUX_WAIT_H', compiler.has_header('linux/wait.h'))
cfg.set('HAVE_NETDB_H', compiler.has_header('netdb.h'))
cfg.set('HAVE_NET_ETHERNET_H', compiler.has_header('net/ethernet.h'))
cfg.set('HAVE_NETINET_IN_H', compiler.has_header('netinet/in.h'))
cfg.set('HAVE_NETPACKET_PACKET_H', compiler.has_header('netpacket/packet.h'))
cfg.set('HAVE_POLL_H', compiler.has_header('poll.h'))
cfg.set('HAVE_PROCESS_H', compiler.has_header('process.h'))
cfg.set('HAVE_PTHREAD_H', compiler.has_header('pthread.h'))
cfg.set('HAVE_PTY_H', compiler.has_header('pty.h'))
cfg.set('HAVE_SCHED_H', compiler.has_header('sched.h'))
cfg.set('HAVE_SETJMP_H', compiler.has_header('setjmp.h'))
cfg.set('HAVE_SHADOW_H', compiler.has_header('shadow.h'))
cfg.set('HAVE_SIGNAL_H', compiler.has_header('signal.h'))
cfg.set('HAVE_SPAWN_H', compiler.has_header('spawn.h'))
cfg.set('HAVE_STROPTS_H', compiler.has_header('stdopts.h'))
cfg.set('HAVE_SYS_AUDIOIO_H', compiler.has_header('sys/audioio.h'))
cfg.set('HAVE_SYS_BSDTTY_H', compiler.has_header('bsd/bsdtty.h'))
cfg.set('HAVE_SYS_DEVPOLL_H', compiler.has_header('sys/devpoll.h'))
have_sys_endian_h = compiler.has_header('sys/endian.h')
cfg.set('HAVE_SYS_ENDIAN_H', have_sys_endian_h)
cfg.set('HAVE_SYS_EPOLL_H', compiler.has_header('sys/epoll.h'))
cfg.set('HAVE_SYS_EVENT_H', compiler.has_header('sys/event.h'))
cfg.set('HAVE_SYS_EVENTFD_H', compiler.has_header('sys/eventfd.h'))
cfg.set('HAVE_SYS_FILE_H', compiler.has_header('sys/file.h'))
cfg.set('HAVE_SYS_IOCTL_H', compiler.has_header('sys/ioctl.h'))
cfg.set('HAVE_SYS_KERN_CONTROL_H', compiler.has_header('sys/kern_control.h'))
cfg.set('HAVE_SYS_LOADAVG_H', compiler.has_header('sys/loadavg.h'))
cfg.set('HAVE_SYS_LOCK_H', compiler.has_header('sys/lock.h'))
have_sys_memfd_h = compiler.has_header('sys/memfd.h')
cfg.set('HAVE_SYS_MEMFD_H', have_sys_memfd_h)
cfg.set('HAVE_SYS_MKDEV_H', compiler.has_header('sys/mkdev.h'))
have_sys_mman_h = compiler.has_header('sys/mman.h')
cfg.set('HAVE_SYS_MMAN_H', compiler.has_header('sys/mman.h'))
cfg.set('HAVE_SYS_MODEM_H', compiler.has_header('sys/modem.h'))
cfg.set('HAVE_SYS_PARAM_H', compiler.has_header('sys/param.h'))
cfg.set('HAVE_SYS_PIDFD_H', compiler.has_header('sys/pidfd.h'))
cfg.set('HAVE_SYS_POLL_H', compiler.has_header('sys/poll.h'))
cfg.set('HAVE_SYS_RANDOM_H', compiler.has_header('sys/random.h'))
cfg.set('HAVE_SYS_RESOURCE_H', compiler.has_header('sys/resource.h'))
cfg.set('HAVE_SYS_SELECT_H', compiler.has_header('sys/select.h'))
cfg.set('HAVE_SYS_SENDFILE_H', compiler.has_header('sys/sendfile.h'))
have_sys_socket_h = compiler.has_header('sys/socket.h')
cfg.set('HAVE_SYS_SOCKET_H', compiler.has_header('sys/socket.h'))
cfg.set('HAVE_SYS_SOUNDCARD_H', compiler.has_header('sys/soundcard.h'))
cfg.set('HAVE_SYS_STAT_H', compiler.has_header('sys/stat.h'))
cfg.set('HAVE_SYS_STATVFS_H', compiler.has_header('sys/statvfs.h'))
cfg.set('HAVE_SYS_SYS_DOMAIN_H', compiler.has_header('sys/sys_domain.h'))
cfg.set('HAVE_SYS_SYSCALL_H', compiler.has_header('sys/syscall.h'))
cfg.set('HAVE_SYS_SYSMACROS_H', compiler.has_header('sys/sysmacros.h'))
cfg.set('HAVE_SYS_TERMIO_H', compiler.has_header('sys/termio.h'))
have_sys_time_h = compiler.has_header('sys/time.h')
cfg.set('HAVE_SYS_TIME_H', have_sys_time_h)
cfg.set('HAVE_SYS_TIMES_H', compiler.has_header('sys/times.h'))
cfg.set('HAVE_SYS_TIMERFD_H', compiler.has_header('sys/timerfd.h'))
cfg.set('HAVE_SYS_TYPES_H', compiler.has_header('sys/types.h'))
cfg.set('HAVE_SYS_UIO_H', compiler.has_header('sys/uio.h'))
cfg.set('HAVE_SYS_UN_H', compiler.has_header('sys/un.h'))
cfg.set('HAVE_SYS_UTSNAME_H', compiler.has_header('sys/utsname.h'))
cfg.set('HAVE_SYS_WAIT_H', compiler.has_header('sys/wait.h'))
cfg.set('HAVE_SYS_XATTR_H', compiler.has_header('sys/xattr.h'))
cfg.set('HAVE_SYSEXITS_H', compiler.has_header('sysexits.h'))
cfg.set('HAVE_SYSLOG_H', compiler.has_header('syslog.h'))
cfg.set('HAVE_TERMIOS_H', compiler.has_header('termios.h'))
cfg.set('HAVE_UTIL_H', compiler.has_header('util.h'))
cfg.set('HAVE_UTIME_H', compiler.has_header('utime.h'))
cfg.set('HAVE_UTMP_H', compiler.has_header('utmp.h'))

foreach header : [
  { 'def': 'HAVE_DIRENT_H', 'header': 'dirent.h' },
  { 'def': 'HAVE_SYS_NDIR_H', 'header': 'sys/ndir.h' },
  { 'def': 'HAVE_SYS_DIR_H', 'header': 'sys/dir.h' },
  { 'def': 'HAVE_NDIR_H', 'header': 'ndir.h' }
]
  if compiler.has_type('DIR*', prefix: '#include <@0@>'.format(header['header']))
    cfg.set(header['def'], true)
    break
  endif
endforeach

major_in_mkdev = compiler.has_header('sys/mkdev.h')
cfg.set('MAJOR_IN_MKDEV', major_in_mkdev)
major_in_sysmacros = compiler.has_header('sys/sysmacros.h')
cfg.set('MAJOR_IN_SYSMACROS', major_in_sysmacros)

# bluetooth/bluetooth.h has been known to not compile with -std=c99.
# http://permalink.gmane.org/gmane.linux.bluez.kernel/22294
cfg.set('HAVE_BLUETOOTH_BLUETOOTH_H', compiler.has_header('bluetooth/bluetooth.h')) # TODO

cfg.set('HAVE_NET_IF_H', compiler.has_header('net/if.h'))

cfg.set('HAVE_LINUX_NETLINK_H', compiler.has_header('linux/netlink.h'))
cfg.set('HAVE_NETLINK_NETLINK_H', compiler.has_header('netlink/netlink.h'))

cfg.set('HAVE_LINUX_QRTR_H', compiler.has_header('linux/qrtr.h'))
cfg.set('HAVE_LINUX_VM_SOCKETS_H', compiler.has_header('linux/vm_sockets.h'))

cfg.set('HAVE_LINUX_CAN_H', compiler.has_header('linux/can.h'))
cfg.set('HAVE_LINUX_CAN_BCM_H', compiler.has_header('linux/can/bcm.h'))
cfg.set('HAVE_LINUX_CAN_J1939_H', compiler.has_header('linux/can/j1939.h'))
cfg.set('HAVE_LINUX_CAN_RAW_H', compiler.has_header('linux/can/raw.h'))

cfg.set('HAVE_NETCAN_CAN_H', compiler.has_header('netcan/can.h'))

if compiler.has_type('clock_t', prefix: '#include <time.h>')
  cfg.set('HAVE_CLOCK_T', true)
else
  cfg.set('clock_t', 'long')
endif

cfg.set('HAVE_MAKEDEV', compiler.compiles('''
#if @0@
#include <sys/mkdev.h>
#elif @1@
#include <sys/sysmacros.h>
#else
#include <sys/types.h>
#endif

int main(void) {
  makedev(0, 0);
  return 0;
}'''.format(major_in_mkdev ? '1' : '0', major_in_sysmacros ? '1' : '0')))

cfg.set('HAVE_DEVICE_MACROS', compiler.compiles('''
#if @0@
#include <sys/mkdev.h>
#elif @1@
#include <sys/sysmacros.h>
#else
#include <sys/types.h>
#endif

int main(void) {
  makedev(major(0), minor(0));
  return 0;
}'''.format(major_in_mkdev ? '1' : '0', major_in_sysmacros ? '1' : '0')))

cfg.set('SYS_SELECT_WITH_SYS_TIME', true)

cfg.set('HAVE_HTOLE64', compiler.compiles('''
#if @0@
#include <endian.h>
#elif @1@
#include <sys/endian.h>
#endif

int main(void) {
  return le64toh(1);
}
'''.format(have_endian_h ? 1 : 0, have_sys_endian_h ? 1 : 0), args: feature_flags))

use_lfs = true
# Don't use largefile support for GNU/Hurd
if host_machine.system() == 'gnu'
  use_lfs = false
endif
if use_lfs
  # TODO: AIX do #define _LARGE_FILES 1
  cfg.set('_LARGEFILE_SOURCE', 1)
  cfg.set('_FILE_OFFSET_BITS', 64)
endif

if not compiler.has_type('mode_t', prefix: '#include <sys/types.h>')
  cfg.set('mode_t', 'int')
endif

if not compiler.has_type('off_t', prefix: '#include <sys/types.h>')
  cfg.set('off_t', 'long int')
endif

if not compiler.has_type('pid_t', prefix: '#include <sys/types.h>')
  if compiler.compiles('''
#if defined _WIN64 && !defined __CYGWIN__
LLP64
#endif

int main(void) {
  return 0;
}
  ''')
    cfg.set('pid_t', 'int')
  else
    cfg.set('pid_t', '__int64')
  endif
endif

cfg.set('RETSIGTYPE', 'void')

if not compiler.has_type('size_t', prefix: '#include <stddef.h>')
  cfg.set('size_t', '(unsigned int)')
endif

if not compiler.has_type('uid_t', prefix: '#include <sys/types.h>')
  cfg.set('uid_t', 'int')
endif

if not compiler.has_type('gid_t', prefix: '#include <sys/types.h>')
  cfg.set('gid_t', 'int')
endif

cfg.set('HAVE_SSIZE_T', compiler.has_type('ssize_t', prefix: '#include <sys/types.h>') ? 1 : 0)

have_uint128_t = compiler.has_type('__uint128_t')
cfg.set('HAVE___UINT128_T', have_uint128_t)
cfg.set('HAVE_GCC_UINT128_T', have_uint128_t)

cfg.set('SIZEOF_INT', compiler.sizeof('int'))
size_long = compiler.sizeof('long')
cfg.set('SIZEOF_LONG', size_long)
cfg.set('ALIGNOF_LONG', compiler.alignment('long'))
size_long_long = compiler.sizeof('long long')
cfg.set('SIZEOF_LONG_LONG', size_long_long)
cfg.set('SIZEOF_VOID_P', compiler.sizeof('void*'))
cfg.set('SIZEOF_SHORT', compiler.sizeof('short'))
cfg.set('SIZEOF_FLOAT', compiler.sizeof('float'))
cfg.set('SIZEOF_DOUBLE', compiler.sizeof('double'))
cfg.set('SIZEOF_FPOS_T', compiler.sizeof('fpos_t'))
cfg.set('SIZEOF_SIZE_T', compiler.sizeof('size_t'))
cfg.set('ALIGNOF_SIZE_T', compiler.alignment('size_t'))
cfg.set('SIZEOF_PID_T', compiler.sizeof('pid_t', prefix: '#include <sys/types.h>'))
cfg.set('SIZEOF_UINTPTR_T', compiler.sizeof('uintptr_t', prefix: '#include <stdint.h>'))
cfg.set('ALIGNOF_MAX_ALIGN_T', compiler.alignment('max_align_t'))
if compiler.has_type('long double')
  cfg.set('HAVE_LONG_DOUBLE', true)
  cfg.set('SIZEOF_LONG_DOUBLE', compiler.sizeof('long double'))
endif
cfg.set('SIZEOF__BOOL', compiler.sizeof('_Bool'))
size_off_t = compiler.sizeof('off_t', prefix: '#include <sys/types.h>')
cfg.set('SIZEOF_OFF_T', size_off_t)

cfg.set('HAVE_LARGEFILE_SUPPORT', size_off_t > size_long and size_long_long >= size_off_t)

cfg.set('SIZEOF_TIME_T', compiler.sizeof('time_t', prefix: '#include <time.h>'))
if compiler.has_type('pthread_t', prefix: '#include <pthread.h>')
  cfg.set('SIZEOF_PTHREAD_T', compiler.sizeof('pthread_t', prefix: '#include <pthread.h>'))
  cfg.set('SIZEOF_PTHREAD_KEY_T', compiler.sizeof('pthread_key_t', prefix: '#include <pthread.h>'))

  # Issue #25658: POSIX hasn't defined that pthread_key_t is compatible with int.
  # This checking will be unnecessary after removing deprecated TLS API.
  # The cast to long int works around a bug in the HP C Compiler
  # version HP92453-01 B.11.11.23709.GP, which incorrectly rejects
  # declarations like 'int a3[[(sizeof (unsigned char)) >= 0]];'.
  # This bug is HP SR number 8606223364.
  cfg.set('PTHREAD_KEY_T_IS_COMPATIBLE_WITH_INT', compiler.compiles('''
#include <pthread.h>

int main(void) {
  pthread_key_t k; k * 1;
  return 0;
}
'''))
endif

cfg.set('PY_HAVE_PERF_TRAMPOLINE',
  host_machine.system() == 'linux' and ['x86_64', 'aarch64'].contains(host_machine.cpu_family())
)

sendfile_lib = compiler.find_library('sendfile', required: false)
if sendfile_lib.found()
  cfg.set('HAVE_LIBSENDFILE', compiler.links('''
#ifdef __cplusplus
extern "C"
#endif
char sendfile(void);
int main(void) {
  return sendfile();
}
'''))
endif

dl_lib = compiler.find_library('dl', required: false)
if dl_lib.found()
  cfg.set('HAVE_LIBDL', compiler.links('''
#ifdef __cplusplus
extern "C"
#endif
char dlopen(void);
int main(void) {
  return dlopen();
}
'''))
endif

dld_lib = compiler.find_library('dld', required: false)
if dld_lib.found()
  cfg.set('HAVE_LIBDLD', compiler.links('''
#ifdef __cplusplus
extern "C"
#endif
char shl_load(void);
int main(void) {
  return shl_load();
}
'''))
endif

have_uuid = compiler.has_header('uuid.h') or uuid_dep.found()
cfg.set('HAVE_UUID_H', have_uuid)
if have_uuid
  cfg.set('HAVE_UUID_GENERATE_TIME_SAFE', compiler.links('''
#ifdef __cplusplus
extern "C"
#endif
char uuid_generate_time_safe(void);
int main(void) {
  return uuid_generate_time_safe();
}
''', dependencies: uuid_dep))
endif

intl_lib = compiler.find_library('intl', required: false)
cfg.set('HAVE_LIBINTL', compiler.links('''
#ifdef __cplusplus
extern "C"
#endif
char textdomain(void);
int main(void) {
  return textdomain();
}
''', dependencies: intl_lib))

if meson.can_run_host_binaries()
  cfg.set('Py_HAVE_C_COMPLEX', compiler.run('''
#include <complex.h>
#define test(type, out) {                              \
  type complex z = 1 + 2*I; z = z*z;                 \
  (out) = (out) || creal(z) != -3 || cimag(z) != 4;  \
}
int main(void) {
  int res = 0;
  test(float, res);
  test(double, res);
  test(long double, res);
  return res;
}
''').returncode() == 0)
else
  cfg.set('Py_HAVE_C_COMPLEX', false)
endif

if meson.can_run_host_binaries()
  cfg.set('HAVE_ALIGNED_REQUIRED', compiler.run('''
int main(void) {
  char s[16];
  int i, *p1, *p2;
  for (i=0; i < 16; i++)
    s[i] = i;
  p1 = (int*)(s+1);
  p2 = (int*)(s+2);
  if (*p1 == *p2)
    return 1;
  return 0;
}
''').returncode() != 0)
else
  cfg.set('HAVE_ALIGNED_REQUIRED', host_machine.system() != 'android')
endif

hash_algos = { 'siphash13': 3, 'siphash24': 1, 'fnv': 2, 'auto': false }
cfg.set('Py_HASH_ALGORITHM', hash_algos[get_option('hash-algorithm')])

if ffi_dep.found()
  if ffi_dep.type_name() == 'internal'
    # We can't evaluate a library that hasn't been built yet, just assume its new enough
    cfg.set('HAVE_FFI_PREP_CIF_VAR', 1)
    cfg.set('HAVE_FFI_PREP_CLOSURE_LOC', 1)
    cfg.set('HAVE_FFI_CLOSURE_ALLOC', 1)
    cfg.set('Py_FFI_SUPPORT_C_COMPLEX', true)
  else
    cfg.set('HAVE_FFI_PREP_CIF_VAR', compiler.has_function('ffi_prep_cif_var', prefix: '#include <ffi.h>', dependencies: ffi_dep) ? 1 : 0)
    cfg.set('HAVE_FFI_PREP_CLOSURE_LOC', compiler.has_function('ffi_prep_closure_loc', prefix: '#include <ffi.h>', dependencies: ffi_dep) ? 1 : 0)
    cfg.set('HAVE_FFI_CLOSURE_ALLOC', compiler.has_function('ffi_closure_alloc', prefix: '#include <ffi.h>', dependencies: ffi_dep) ? 1 : 0)

    # Check for libffi with real complex double support.
    # # This is a workaround, since FFI_TARGET_HAS_COMPLEX_TYPE was defined in libffi v3.2.1,
    # # but real support was provided only in libffi v3.3.0.
    # # See https://github.com/python/cpython/issues/125206 for more details.
    if meson.can_run_host_binaries()
      cfg.set('Py_FFI_SUPPORT_C_COMPLEX', compiler.run('''
#include <complex.h>
#include <ffi.h>
int z_is_expected(double complex z) {
  const double complex expected = CMPLX(1.25, -0.5);
  return z == expected;
}
int main(void) {
  double complex z = 1.25 - 0.5 * I;
  ffi_type *args[1] = {&ffi_type_complex_double};
  void *values[1] = {&z};
  ffi_cif cif;
  if (ffi_prep_cif(&cif, FFI_DEFAULT_ABI, 1,
      &ffi_type_sint, args) != FFI_OK)
  {
    return 2;
  }
  ffi_arg rc;
  ffi_call(&cif, FFI_FN(z_is_expected), &rc, values);
  return !rc;
}
''', dependencies: ffi_dep).returncode() == 0)
    else
      cfg.set('Py_FFI_SUPPORT_C_COMPLEX', false)
    endif
  endif
endif

cfg.set('WITH_DECIMAL_CONTEXTVAR', get_option('decimal-contextvar')) 

if sqlite3_dep.found() and compiler.has_header('sqlite3.h', dependencies: sqlite3_dep)
  needed_funcs = [ 'sqlite3_bind_double', 'sqlite3_column_decltype', 'sqlite3_column_double', 'sqlite3_complete', 'sqlite3_progress_handler', 'sqlite3_result_double', 'sqlite3_set_authorizer', 'sqlite3_trace_v2', 'sqlite3_value_double' ]
  have_sqlite3 = true
  foreach func : needed_funcs
    if not compiler.has_function(func, prefix: '#include <sqlite3.h>', dependencies: sqlite3_dep)
      have_sqlite3 = false
      break
    endif
  endforeach
  cfg.set('HAVE_LIBSQLITE3', have_sqlite3)
  cfg.set('PY_SQLITE_HAVE_SERIALIZE', compiler.has_function('sqlite3_serialize', prefix: '#include <sqlite3.h>', dependencies: sqlite3_dep))
  cfg.set('PY_SQLITE_ENABLE_LOAD_EXTENSION', compiler.has_function('sqlite3_load_extension', prefix: '#include <sqlite3.h>', dependencies: sqlite3_dep, required: get_option('loadable-sqlite-extensions')))
endif

if libgdbm_dep.found()
  cfg.set('HAVE_GDBM_H', compiler.has_header('gdbm.h', dependencies: libgdbm_dep))
endif
if libdbm_dep.found()
  cfg.set('HAVE_NDBM_H', compiler.has_header('ndbm.h', dependencies: libdbm_dep))
  cfg.set('HAVE_GDBM_NDBM_H', compiler.has_header('gdbm/ndbm.h', dependencies: libdbm_dep))
  cfg.set('HAVE_GDBM_DASH_NDBM_H', compiler.has_header('gdbm-ndbm.h', dependencies: libdbm_dep))
  cfg.set('HAVE_DB_H', compiler.has_header('db.h', dependencies: libdbm_dep))
endif


cfg.set('_REENTRANT', 1)
cfg.set('PTHREAD_SYSTEM_SCHED_SUPPORTED', true) # TODO
have_sigmask = compiler.has_function('pthread_sigmask', prefix: '#include <pthread.h>\n#include <signal.h>', args: feature_flags)
cfg.set('HAVE_PTHREAD_SIGMASK', have_sigmask)
if have_sigmask and host_machine.system() == 'cygwin'
  cfg.set('HAVE_BROKEN_PTHREAD_SIGMASK', true)
endif
cfg.set('HAVE_PTHREAD_GETCPUCLOCKID', compiler.has_function('pthread_getcpuclockid', prefix: '#include <pthread.h>', args: feature_flags))

cfg.set('ENABLE_IPV6',
  compiler.has_define('AF_INET6', prefix: '#include <sys/types.h>\n#include <sys/socket.h>') and # required in has_define would be nice
  compiler.has_member('struct sockaddr_in6', 'sin6_scope_id', prefix: '#include <sys/types.h>\n#include <netinet/in.h>', required: get_option('ipv6'))
)
cfg.set('HAVE_LINUX_CAN_RAW_FD_FRAMES', compiler.has_header_symbol('linux/can/raw.h', 'CAN_RAW_FD_FRAMES'))
cfg.set('HAVE_LINUX_CAN_RAW_JOIN_FILTERS', compiler.has_header_symbol('linux/can/raw.h', 'CAN_RAW_JOIN_FILTERS'))

cfg.set('WITH_DOC_STRINGS', get_option('doc-strings'))

cfg.set('HAVE_STD_ATOMIC', compiler.links('''
#include <stdatomic.h>
atomic_int int_var;
atomic_uintptr_t uintptr_var;
int main(void) {
  atomic_store_explicit(&int_var, 5, memory_order_relaxed);
  atomic_store_explicit(&uintptr_var, 0, memory_order_relaxed);
  int loaded_value = atomic_load_explicit(&int_var, memory_order_seq_cst);
  return 0;
}
'''))

cfg.set('HAVE_BUILTIN_ATOMIC', compiler.links('''
int val;
int main(void) {
  __atomic_store_n(&val, 1, __ATOMIC_SEQ_CST);
  (void)__atomic_load_n(&val, __ATOMIC_SEQ_CST);
  return 0;
}
'''))

with_mimalloc = get_option('allocator') == 'mimalloc'
cfg.set('WITH_MIMALLOC', with_mimalloc)
cfg.set('WITH_PYMALLOC', 1) # option?

cfg.set('PY_COERCE_C_LOCALE', get_option('c-locale-coercion'))

cfg.set('HAVE_DLOPEN', compiler.has_function('dlopen'))
# TODO: dynload_file
cfg.set('HAVE_DYNAMIC_LOADING', true)

cfg.set('HAVE_ACCEPT4', compiler.has_function('accept4'))
cfg.set('HAVE_ALARM', compiler.has_function('alarm'))
cfg.set('HAVE_BIND_TEXTDOMAIN_CODESET', compiler.has_function('bind_textdomain_codeset'))
cfg.set('HAVE_CHMOD', compiler.has_function('chmod'))
cfg.set('HAVE_CHOWN', compiler.has_function('chown'))
cfg.set('HAVE_CLOCK', compiler.has_function('clock'))
cfg.set('HAVE_CLOSEFROM', compiler.has_function('closefrom'))
cfg.set('HAVE_CLOSE_RANGE', compiler.has_function('close_range'))
cfg.set('HAVE_CONFSTR', compiler.has_function('confstr'))
cfg.set('HAVE_COPY_FILE_RANGE', compiler.has_function('copy_file_range'))
cfg.set('HAVE_CTERMID', compiler.has_function('ctermid'))
cfg.set('HAVE_DLADDR', compiler.has_function('dladdr'))
cfg.set('HAVE_DUP', compiler.has_function('dup'))
cfg.set('HAVE_DUP3', compiler.has_function('dup3'))
cfg.set('HAVE_EXECV', compiler.has_function('execv'))
have_explicit_bzero = compiler.has_function('explicit_bzero')
cfg.set('HAVE_EXPLICIT_BZERO', have_explicit_bzero)
cfg.set('HAVE_EXPLICIT_MEMSET', compiler.has_function('explicit_memset'))
cfg.set('HAVE_FACCESSAT', compiler.has_function('faccessat'))
cfg.set('HAVE_FCHMOD', compiler.has_function('fchmod'))
cfg.set('HAVE_FCHMODAT', compiler.has_function('fchmodat'))
cfg.set('HAVE_FCHOWN', compiler.has_function('fchown'))
cfg.set('HAVE_FCHOWNAT', compiler.has_function('fchownat'))
cfg.set('HAVE_FDOPENDIR', compiler.has_function('fdopendir'))
cfg.set('HAVE_FDWALK', compiler.has_function('fdwalk'))
cfg.set('HAVE_FEXECVE', compiler.has_function('fexecve'))
cfg.set('HAVE_FORK', compiler.has_function('fork'))
cfg.set('HAVE_FORK1', compiler.has_function('fork1'))
cfg.set('HAVE_FPATHCONF', compiler.has_function('fpathconf'))
cfg.set('HAVE_FSTATAT', compiler.has_function('fstatat'))
cfg.set('HAVE_FTIME', compiler.has_function('ftime'))
cfg.set('HAVE_FTRUNCATE', compiler.has_function('ftruncate'))
cfg.set('HAVE_FUTIMENS', compiler.has_function('futimens'))
cfg.set('HAVE_FUTIMES', compiler.has_function('futimes'))
cfg.set('HAVE_FUTIMESAT', compiler.has_function('futimesat'))
cfg.set('HAVE_GAI_STRERROR', compiler.has_function('gai_strerror'))
cfg.set('HAVE_GETEGID', compiler.has_function('getegid'))
cfg.set('HAVE_GETEUID', compiler.has_function('geteuid'))
cfg.set('HAVE_GETGID', compiler.has_function('getgid'))
cfg.set('HAVE_GETGRENT', compiler.has_function('getgrent'))
cfg.set('HAVE_GETGRGID', compiler.has_function('getgrgid'))
cfg.set('HAVE_GETGRGID_R', compiler.has_function('getgrgid_r'))
cfg.set('HAVE_GETGRNAM_R', compiler.has_function('getgrnam_r'))
cfg.set('HAVE_GETGROUPLIST', compiler.has_function('getgrouplist'))
cfg.set('HAVE_GETHOSTNAME', compiler.has_function('gethostname'))
cfg.set('HAVE_GETITIMER', compiler.has_function('getitimer'))
cfg.set('HAVE_GETLOADAVG', compiler.has_function('getloadavg'))
cfg.set('HAVE_GETLOGIN', compiler.has_function('getlogin'))
cfg.set('HAVE_GETPEERNAME', compiler.has_function('getpeername'))
cfg.set('HAVE_GETPGID', compiler.has_function('getpgid'))
cfg.set('HAVE_GETPID', compiler.has_function('getpid'))
cfg.set('HAVE_GETPPID', compiler.has_function('getppid'))
cfg.set('HAVE_GETPRIORITY', compiler.has_function('getpriority'))
cfg.set('HAVE__GETPTY', compiler.has_function('_getpty'))
cfg.set('HAVE_GETPWENT', compiler.has_function('getpwent'))
cfg.set('HAVE_GETPWNAM_R', compiler.has_function('getpwnam_r'))
cfg.set('HAVE_GETPWUID', compiler.has_function('getpwuid'))
cfg.set('HAVE_GETPWUID_R', compiler.has_function('getpwuid_r'))
cfg.set('HAVE_GETRESGID', compiler.has_function('getresgid'))
cfg.set('HAVE_GETRESUID', compiler.has_function('getresuid'))
cfg.set('HAVE_GETRUSAGE', compiler.has_function('getrusage'))
cfg.set('HAVE_GETSID', compiler.has_function('getsid'))
cfg.set('HAVE_GETSPENT', compiler.has_function('getspent'))
cfg.set('HAVE_GETSPNAM', compiler.has_function('getspnam'))
cfg.set('HAVE_GETUID', compiler.has_function('getuid'))
cfg.set('HAVE_GETWD', compiler.has_function('getwd'))
cfg.set('HAVE_GRANTPT', compiler.has_function('grantpt'))
cfg.set('HAVE_IF_NAMEINDEX', compiler.has_function('if_nameindex'))
cfg.set('HAVE_INITGROUPS', compiler.has_function('initgroups'))
cfg.set('HAVE_KILL', compiler.has_function('kill'))
cfg.set('HAVE_KILLPG', compiler.has_function('killpg'))
cfg.set('HAVE_LCHOWN', compiler.has_function('lchown'))
cfg.set('HAVE_LINKAT', compiler.has_function('linkat'))
cfg.set('HAVE_LOCKF', compiler.has_function('lockf'))
cfg.set('HAVE_LSTAT', compiler.has_function('lstat'))
cfg.set('HAVE_LUTIMES', compiler.has_function('lutimes'))
cfg.set('HAVE_MADVISE', compiler.has_function('madvise'))
cfg.set('HAVE_MBRTOWC', compiler.has_function('mbrtowc'))
cfg.set('HAVE_MEMRCHR', compiler.has_function('memrchr'))
cfg.set('HAVE_MKDIRAT', compiler.has_function('mkdirat') ? 1 : 0)
cfg.set('HAVE_MKFIFO', compiler.has_function('mkfifo'))
cfg.set('HAVE_MKFIFOAT', compiler.has_function('mkfifoat'))
cfg.set('HAVE_MKNOD', compiler.has_function('mknod'))
cfg.set('HAVE_MKNODAT', compiler.has_function('mknodat'))
cfg.set('HAVE_MKTIME', compiler.has_function('mktime'))
cfg.set('HAVE_MMAP', compiler.has_function('mmap'))
cfg.set('HAVE_MREMAP', compiler.has_function('mremap'))
cfg.set('HAVE_NICE', compiler.has_function('nice'))
cfg.set('HAVE_OPENAT', compiler.has_function('openat'))
cfg.set('HAVE_OPENDIR', compiler.has_function('opendir'))
cfg.set('HAVE_PATHCONF', compiler.has_function('pathconf'))
cfg.set('HAVE_PAUSE', compiler.has_function('pause'))
cfg.set('HAVE_PIPE', compiler.has_function('pipe'))
cfg.set('HAVE_PIPE2', compiler.has_function('pipe2'))
cfg.set('HAVE_PLOCK', compiler.has_function('plock'))
cfg.set('HAVE_POLL', compiler.has_function('poll'))
cfg.set('HAVE_POSIX_FADVISE', compiler.has_function('posix_fadvise'))
cfg.set('HAVE_POSIX_FALLOCATE', compiler.has_function('posix_fallocate'))
cfg.set('HAVE_POSIX_OPENPT', compiler.has_function('posix_openpt'))
cfg.set('HAVE_POSIX_SPAWN', compiler.has_function('posix_spawn'))
cfg.set('HAVE_POSIX_SPAWNP', compiler.has_function('posix_spawnp'))
cfg.set('HAVE_POSIX_SPAWN_FILE_ACTIONS_ADDCLOSEFROM_NP', compiler.has_function('posix_spawn_file_actions_addclosefrom_np'))
cfg.set('HAVE_PREAD', compiler.has_function('pread'))
cfg.set('HAVE_PREADV', compiler.has_function('preadv'))
cfg.set('HAVE_PREADV2', compiler.has_function('preadv2'))
cfg.set('HAVE_PROCESS_VM_READV', compiler.has_function('process_vm_readv'))
cfg.set('HAVE_PTHREAD_COND_TIMEDWAIT_RELATIVE_NP', compiler.has_function('pthread_cond_timedwait_relative_np'))
cfg.set('HAVE_PTHREAD_CONDATTR_SETCLOCK', compiler.has_function('pthread_condattr_setclock'))
cfg.set('HAVE_PTHREAD_INIT', compiler.has_function('pthread_init'))
cfg.set('HAVE_PTHREAD_KILL', compiler.has_function('pthread_kill'))
cfg.set('HAVE_PTHREAD_GETNAME_NP', compiler.has_function('pthread_getname_np'))
cfg.set('HAVE_PTHREAD_SETNAME_NP', compiler.has_function('pthread_setname_np'))
cfg.set('HAVE_PTSNAME', compiler.has_function('ptsname'))
cfg.set('HAVE_PTSNAME_R', compiler.has_function('ptsname_r'))
cfg.set('HAVE_PWRITE', compiler.has_function('pwrite'))
cfg.set('HAVE_PWRITEV', compiler.has_function('pwritev'))
cfg.set('HAVE_PWRITEV2', compiler.has_function('pwritev2'))
cfg.set('HAVE_READLINK', compiler.has_function('readlink'))
cfg.set('HAVE_READLINKAT', compiler.has_function('readlinkat'))
cfg.set('HAVE_READV', compiler.has_function('readv'))
cfg.set('HAVE_REALPATH', compiler.has_function('realpath'))
cfg.set('HAVE_RENAMEAT', compiler.has_function('renameat'))
cfg.set('HAVE_RTPSPAWN', compiler.has_function('rtpSpawn'))
cfg.set('HAVE_SCHED_GET_PRIORITY_MAX', compiler.has_function('sched_get_priority_max'))
cfg.set('HAVE_SCHED_RR_GET_INTERVAL', compiler.has_function('sched_rr_get_interval'))
cfg.set('HAVE_SCHED_SETAFFINITY', compiler.has_function('sched_setaffinity'))
cfg.set('HAVE_SCHED_SETPARAM', compiler.has_function('sched_setparam'))
cfg.set('HAVE_SCHED_SETSCHEDULER', compiler.has_function('sched_setscheduler'))
cfg.set('HAVE_SEM_CLOCKWAIT', compiler.has_function('sem_clockwait') ? 1 : 0)
cfg.set('HAVE_SEM_GETVALUE', compiler.has_function('sem_getvalue') ? 1 : 0)
cfg.set('HAVE_SEM_OPEN', compiler.has_function('sem_open') ? 1 : 0)
cfg.set('HAVE_SEM_TIMEDWAIT', compiler.has_function('sem_timedwait') ? 1 : 0)
cfg.set('HAVE_SEM_UNLINK', compiler.has_function('sem_unlink') ? 1 : 0)
cfg.set('HAVE_SENDFILE', compiler.has_function('sendfile'))
cfg.set('HAVE_SETEGID', compiler.has_function('setegid'))
cfg.set('HAVE_SETEUID', compiler.has_function('seteuid'))
cfg.set('HAVE_SETGID', compiler.has_function('setgid'))
cfg.set('HAVE_SETHOSTNAME', compiler.has_function('sethostname'))
cfg.set('HAVE_SETITIMER', compiler.has_function('setitimer'))
cfg.set('HAVE_SETLOCALE', compiler.has_function('setlocale'))
cfg.set('HAVE_SETPGID', compiler.has_function('setpgid'))
cfg.set('HAVE_SETPGRP', compiler.has_function('setpgrp'))
cfg.set('HAVE_SETPRIORITY', compiler.has_function('setpriority'))
cfg.set('HAVE_SETREGID', compiler.has_function('setregid'))
cfg.set('HAVE_SETRESGID', compiler.has_function('setresgid'))
cfg.set('HAVE_SETRESUID', compiler.has_function('setresuid'))
cfg.set('HAVE_SETREUID', compiler.has_function('setreuid'))
cfg.set('HAVE_SETSID', compiler.has_function('setsid'))
cfg.set('HAVE_SETUID', compiler.has_function('setuid'))
cfg.set('HAVE_SETVBUF', compiler.has_function('setvbuf'))
cfg.set('HAVE_SHUTDOWN', compiler.has_function('shutdown'))
cfg.set('HAVE_SIGACTION', compiler.has_function('sigaction'))
cfg.set('HAVE_SIGALTSTACK', compiler.has_function('sigaltstack'))
cfg.set('HAVE_SIGFILLSET', compiler.has_function('sigfillset'))
cfg.set('HAVE_SIGINTERRUPT', compiler.has_function('siginterrupt'))
cfg.set('HAVE_SIGPENDING', compiler.has_function('sigpending'))
cfg.set('HAVE_SIGRELSE', compiler.has_function('sigrelse'))
cfg.set('HAVE_SIGTIMEDWAIT', compiler.has_function('sigtimedwait'))
cfg.set('HAVE_SIGWAIT', compiler.has_function('sigwait'))
cfg.set('HAVE_SIGWAITINFO', compiler.has_function('sigwaitinfo'))
cfg.set('HAVE_SNPRINTF', compiler.has_function('snprintf'))
cfg.set('HAVE_SPLICE', compiler.has_function('splice'))
cfg.set('HAVE_STRFTIME', compiler.has_function('strftime'))
cfg.set('HAVE_STRLCPY', compiler.has_function('strlcpy'))
cfg.set('HAVE_STRSIGNAL', compiler.has_function('strsignal'))
cfg.set('HAVE_SYMLINKAT', compiler.has_function('symlinkat'))
cfg.set('HAVE_SYNC', compiler.has_function('sync'))
cfg.set('HAVE_SYSCONF', compiler.has_function('sysconf'))
cfg.set('HAVE_TCGETPGRP', compiler.has_function('tcgetpgrp'))
cfg.set('HAVE_TCSETPGRP', compiler.has_function('tcsetpgrp'))
cfg.set('HAVE_TEMPNAM', compiler.has_function('tempnam'))
cfg.set('HAVE_TIMEGM', compiler.has_function('timegm'))
cfg.set('HAVE_TIMES', compiler.has_function('times'))
cfg.set('HAVE_TMPFILE', compiler.has_function('tmpfile'))
cfg.set('HAVE_TMPNAM', compiler.has_function('tmpnam'))
cfg.set('HAVE_TMPNAM_R', compiler.has_function('tmpnam_r'))
cfg.set('HAVE_TRUNCATE', compiler.has_function('truncate'))
cfg.set('HAVE_TTYNAME_R', compiler.has_function('ttyname_r'))
cfg.set('HAVE_UMASK', compiler.has_function('umask'))
cfg.set('HAVE_UNAME', compiler.has_function('uname'))
cfg.set('HAVE_UNLINKAT', compiler.has_function('unlinkat'))
cfg.set('HAVE_UNLOCKPT', compiler.has_function('unlockpt'))
cfg.set('HAVE_UTIMENSAT', compiler.has_function('utimensat'))
cfg.set('HAVE_UTIMES', compiler.has_function('utimes'))
cfg.set('HAVE_VFORK', compiler.has_function('vfork'))
cfg.set('HAVE_WAIT', compiler.has_function('wait'))
cfg.set('HAVE_WAIT3', compiler.has_function('wait3'))
cfg.set('HAVE_WAIT4', compiler.has_function('wait4'))
cfg.set('HAVE_WAITID', compiler.has_function('waitid'))
cfg.set('HAVE_WAITPID', compiler.has_function('waitpid'))
cfg.set('HAVE_WCSCOLL', compiler.has_function('wcscoll'))
cfg.set('HAVE_WCSFTIME', compiler.has_function('wcsftime'))
cfg.set('HAVE_WCSXFRM', compiler.has_function('wcsxfrm'))
cfg.set('HAVE_WMEMCMP', compiler.has_function('wmemcmp'))
cfg.set('HAVE_WRITEV', compiler.has_function('writev'))
cfg.set('HAVE_GETENTROPY', compiler.has_function('getentropy'))
cfg.set('HAVE_GETGROUPS', compiler.has_function('getgroups'))
cfg.set('HAVE_SYSTEM', compiler.has_function('system'))

cfg.set('HAVE_DIRFD',compiler.has_function('dirfd', prefix: '#include <sys/types.h>\n#include <dirent.h>', args: feature_flags))

cfg.set('HAVE_CHROOT', compiler.has_function('chroot'))
cfg.set('HAVE_LINK', compiler.has_function('link'))
cfg.set('HAVE_SYMLINK', compiler.has_function('symlink'))
cfg.set('HAVE_FCHDIR', compiler.has_function('fchdir'))
cfg.set('HAVE_FSYNC', compiler.has_function('fsync'))
cfg.set('HAVE_FDATASYNC', compiler.has_function('fdatasync'))
cfg.set('HAVE_EPOLL', compiler.has_function('epoll_create', prefix: '#include <sys/epoll.h>'))
cfg.set('HAVE_EPOLL_CREATE1', compiler.has_function('epoll_create1', prefix: '#include <sys/epoll.h>'))
cfg.set('HAVE_KQUEUE', compiler.has_function('kqueue', prefix: '#include <sys/types.h>\n#include <sys/event.h>'))
cfg.set('HAVE_PRLIMIT', compiler.has_function('prlimit', prefix: '#include <sys/time.h>\n#include <sys/resource.h>', args: feature_flags))
cfg.set('HAVE_DYLD_SHARED_CACHE_CONTAINS_PATH', compiler.has_function('_dyld_shared_cache_contains_path', prefix: '#include <mach-o/dyld.h>'))
cfg.set('HAVE_MEMFD_CREATE', compiler.has_function('memfd_create', prefix: '@0@\n@1@'.format(have_sys_mman_h ? '#include <sys/mman.h>' : '', have_sys_memfd_h ? '#include <sys/memfd.h>' : ''), args: feature_flags))
cfg.set('HAVE_EVENTFD', compiler.has_function('eventfd', prefix: '#include <sys/eventfd.h>'))
cfg.set('HAVE_TIMERFD_CREATE', compiler.has_function('timerfd_create', prefix: '#include <sys/timerfd.h>'))
cfg.set('HAVE_CTERMID_R', compiler.has_function('ctermid_r'))
cfg.set('HAVE_FLOCK', compiler.has_function('flock', prefix: '#include <sys/file.h>'))
cfg.set('HAVE_GETPAGESIZE', compiler.has_function('getpagesize'))
cfg.set('HAVE_BROKEN_UNSETENV', not compiler.compiles('''
#include <stdlib.h>
int main(void) {
  return unsetenv("DUMMY");
}
''', args: feature_flags))
cfg.set('HAVE_CHFLAGS', compiler.has_function('chflags'))
cfg.set('HAVE_LCHFLAGS', compiler.has_function('lchflags'))

cfg.set('HAVE_ZLIB_H', zlib_dep.found())
if zlib_dep.found()
  cfg.set('HAVE_ZLIB_COPY', compiler.has_function('inflateCopy', prefix: '#include <zlib.h>', dependencies: zlib_dep))
endif
#cfg.set('HAVE_BZLIB_H', bzip_dep.found())
cfg.set('HAVE_LZMA_H', lzma_dep.found())

cfg.set('HAVE_HSTRERROR', compiler.has_function('hstrerror', prefix: '#include <netdb.h>', args: feature_flags))
cfg.set('HAVE_GETSERVBYNAME', compiler.has_function('getservbyname', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETSERVBYPORT', compiler.has_function('getservbyport', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETHOSTBYNAME', compiler.has_function('gethostbyname', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETHOSTBYADDR', compiler.has_function('gethostbyaddr', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETPROTOBYNAME', compiler.has_function('getprotobyname', prefix: '#include <netdb.h>'))

net_prefix = '''
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
'''
cfg.set('HAVE_INET_ATON', compiler.has_function('inet_aton', prefix: net_prefix, args: feature_flags))
cfg.set('HAVE_INET_NTOA', compiler.has_function('inet_ntoa', prefix: net_prefix, args: feature_flags))
cfg.set('HAVE_INET_PTON', compiler.has_function('inet_pton', prefix: net_prefix, args: feature_flags))
cfg.set('HAVE_GETPEERNAME', compiler.has_function('getpeername', prefix: net_prefix))
cfg.set('HAVE_GETSOCKNAME', compiler.has_function('getsockname', prefix: net_prefix))
cfg.set('HAVE_ACCEPT', compiler.has_function('accept', prefix: net_prefix))
cfg.set('HAVE_BIND', compiler.has_function('bind', prefix: net_prefix))
cfg.set('HAVE_CONNECT', compiler.has_function('connect', prefix: net_prefix))
cfg.set('HAVE_LISTEN', compiler.has_function('listen', prefix: net_prefix))
cfg.set('HAVE_RECVFROM', compiler.has_function('recvfrom', prefix: net_prefix))
cfg.set('HAVE_SENDTO', compiler.has_function('sendto', prefix: net_prefix))
cfg.set('HAVE_SETSOCKOPT', compiler.has_function('setsockopt', prefix: net_prefix))
cfg.set('HAVE_SOCKET', compiler.has_function('socket', prefix: net_prefix))

cfg.set('HAVE_SETGROUPS', compiler.has_function('setgroups', prefix: '#include <unistd.h>\n@0@'.format(have_grp_h ? '#include <grp.h>' : ''), args: feature_flags))

cfg.set('HAVE_OPENPTY', compiler.has_function('openpty'))
cfg.set('HAVE_LOGIN_TTY', compiler.has_function('login_tty'))
cfg.set('HAVE_FORKPTY', compiler.has_function('forkpty'))

cfg.set('HAVE_FSEEK64', compiler.has_function('fseek64'))
cfg.set('HAVE_FSEEKO', compiler.has_function('fseeko'))
cfg.set('HAVE_FSTATVFS', compiler.has_function('fstatvfs'))
cfg.set('HAVE_FTELL64', compiler.has_function('ftell64'))
cfg.set('HAVE_FTELLO', compiler.has_function('ftello'))
cfg.set('HAVE_STATVFS', compiler.has_function('statvfs'))
cfg.set('HAVE_DUP2', compiler.has_function('dup2'))

cfg.set('HAVE_GETPGRP', compiler.has_function('getpgrp', prefix: '#include <unistd.h>', args: feature_flags))
cfg.set('GETPGRP_HAVE_ARG', compiler.compiles('#include <unistd.h>\nint main(void) { getpgrp(0); return 0; }', args: feature_flags))
cfg.set('HAVE_SETPGRP', compiler.has_function('setpgrp', prefix: '#include <unistd.h>', args: feature_flags))
cfg.set('SETPGRP_HAVE_ARG', compiler.compiles('#include <unistd.h>\nint main(void) { setpgrp(0, 0); return 0; }', args: feature_flags))

cfg.set('HAVE_SETNS', compiler.has_function('setns'))
cfg.set('HAVE_UNSHARE', compiler.has_function('unshare'))

cfg.set('HAVE_CLOCK_GETTIME', compiler.has_function('clock_gettime', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_CLOCK_GETRES', compiler.has_function('clock_getres', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_CLOCK_SETTIME', compiler.has_function('clock_settime', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_CLOCK_NANOSLEEP', compiler.has_function('clock_nanosleep', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_NANOSLEEP', compiler.has_function('nanosleep', prefix: '#include <time.h>', args: feature_flags))

addr_prefix = '''
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>
'''
cfg.set('HAVE_GETADDRINFO', compiler.has_function('getaddrinfo', prefix: addr_prefix, args: feature_flags))
cfg.set('HAVE_GETNAMEINFO', compiler.has_function('getnameinfo', prefix: addr_prefix, args: feature_flags))

have_struct_tm = compiler.has_type('struct tm', prefix: '#include <sys/types.h>\n#include <time.h>')
cfg.set('TM_IN_SYS_TIME', not have_struct_tm and have_sys_time_h)
tm_struct_header = (not have_struct_tm and have_sys_time_h) ? 'sys/time.h' : 'time.h'
have_struct_tm_tm_zone = compiler.has_member('struct tm', 'tm_zone', prefix: '#include <sys/types.h>\n#include <@0@>'.format(tm_struct_header), args: feature_flags)
cfg.set('HAVE_STRUCT_TM_TM_ZONE', have_struct_tm_tm_zone)
cfg.set('HAVE_TM_ZONE', have_struct_tm_tm_zone)
cfg.set('HAVE_DECL_TZNAME', compiler.has_function('tzname', prefix: '#include <time.h>'))
have_tzname = compiler.has_header_symbol('time.h', 'tzname')
cfg.set('HAVE_TZNAME', have_tzname)

cfg.set('HAVE_STRUCT_STAT_ST_RDEV', compiler.has_member('struct stat', 'st_rdev', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_BLKSIZE', compiler.has_member('struct stat', 'st_blksize', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_FLAGS', compiler.has_member('struct stat', 'st_flags', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_GEN', compiler.has_member('struct stat', 'st_gen', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_BIRTHTIME', compiler.has_member('struct stat', 'st_birthtime', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_BLOCKS', compiler.has_member('struct stat', 'st_blocks', prefix: '#include <sys/stat.h>'))

cfg.set('HAVE_STRUCT_PASSWD_PW_GECOS', compiler.has_member('struct passwd', 'pw_gecos', prefix: '#include <sys/types.h>\n#include <pwd.h>'))
cfg.set('HAVE_STRUCT_PASSWD_PW_PASSWD', compiler.has_member('struct passwd', 'pw_passwd', prefix: '#include <sys/types.h>\n#include <pwd.h>'))

cfg.set('HAVE_SIGINFO_T_SI_BAND', compiler.has_member('siginfo_t', 'si_band', prefix: '#include <signal.h>', args: feature_flags))
cfg.set('HAVE_ALTZONE', compiler.has_header_symbol('time.h', 'altzone'))

socket_prefix = '''
#include <sys/types.h>
#include <sys/socket.h>
'''
cfg.set('HAVE_ADDRINFO', compiler.has_type('struct addrinfo', prefix: '#include <netdb.h>', args: feature_flags))
cfg.set('HAVE_SOCKADDR_STORAGE', compiler.has_type('struct sockaddr_storage', prefix: socket_prefix, args: feature_flags))
cfg.set('HAVE_SOCKADDR_ALG', compiler.has_type('struct sockaddr_alg', prefix: socket_prefix + '\n#include <linux/if_alg.h>', args: feature_flags))
cfg.set('HAVE_PROTOTYPES', compiler.compiles('''
int foo(int x) { return 0; }
int main(void) {
  return foo(10);
}
'''))
cfg.set('HAVE_SOCKETPAIR', compiler.has_function('socketpair', prefix: socket_prefix))
cfg.set('HAVE_SOCKADDR_SA_LEN', compiler.has_member('struct sockaddr', 'sa_len', prefix: socket_prefix))

cfg.set('HAVE_GETHOSTBYNAME_R', compiler.has_function('gethostbyname_r', prefix: '#include <netdb.h>', args: feature_flags))
cfg.set('HAVE_GETHOSTBYNAME_R_6_ARG', compiler.compiles('''
#include <netdb.h>

int main(void) {
  char *name;
  struct hostent *he, *res;
  char buffer[2048];
  int buflen = 2048;
  int h_errnop;
  (void) gethostbyname_r(name, he, buffer, buflen, &res, &h_errnop);
  return 0;
}
''', args: feature_flags))
cfg.set('HAVE_GETHOSTBYNAME_R_5_ARG', compiler.compiles('''
#include <netdb.h>

int main(void) {
  char *name;
  struct hostent *he;
  char buffer[2048];
  int buflen = 2048;
  int h_errnop;
  (void) gethostbyname_r(name, he, buffer, buflen, &h_errnop);
  return 0;
}
''', args: feature_flags))
cfg.set('HAVE_GETHOSTBYNAME_R_3_ARG', compiler.compiles('''
#include <netdb.h>

int main(void) {
  char *name;
  struct hostent *he;
  struct hostent_data data;
  (void) gethostbyname_r(name, he, &data);
  return 0;
}
''', args: feature_flags))

cfg.set('HAVE_GCC_ASM_FOR_X64', compiler.links('''
int main(void) {
  __asm__ __volatile__ ("movq %rcx, %rax");
  return 0;
}
'''))

# TODO: this doesn't actually work when you can't run host binaries
first = compiler.compute_int('((unsigned char*)&v)[0]', prefix: 'static const double v = -0.f;')
if first == 128
  cfg.set('DOUBLE_IS_BIG_ENDIAN_IEEE754', true)
elif first == 0
  if host_machine.cpu_family() == 'arm' # is this right?
    # Some ARM platforms use a mixed-endian representation for
    # doubles. While Python doesn't currently have full support
    # for these platforms (see e.g., issue 1762561), we can at
    # least make sure that float <-> string conversions work.
    # FLOAT_WORDS_BIGENDIAN doesn't actually detect this case,
    # but if it's not big or little, then it must be this?
    cfg.set('DOUBLE_IS_ARM_MIXED_ENDIAN_IEEE754', true)
  else
    cfg.set('DOUBLE_IS_LITTLE_ENDIAN_IEEE754', true)
  endif
elif first == -1
  warning('Unable to test double endianness, assuming same as int')
  if host_machine.endian() == 'big'
    cfg.set('DOUBLE_IS_BIG_ENDIAN_IEEE754', true)
  elif host_machine.endian() == 'little'
    cfg.set('DOUBLE_IS_LITTLE_ENDIAN_IEEE754', true)
  endif
else
  error('Unknown floating point format')
endif

have_gcc_asm_for_x87 = compiler.links('''
int main(void) {
  unsigned short cw;
  __asm__ __volatile__ ("fnstcw %0" : "=m" (cw));
  __asm__ __volatile__ ("fldcw %0" : : "m" (cw));
  return 0;
}
''')
cfg.set('HAVE_GCC_ASM_FOR_X87', have_gcc_asm_for_x87)
cfg.set('HAVE_GCC_ASM_FOR_MC68881', compiler.links('''
int main(void) {
  unsigned int fpcr;
  __asm__ __volatile__ ("fmove.l %%fpcr,%0" : "=g" (fpcr));
  __asm__ __volatile__ ("fmove.l %0,%%fpcr" : : "g" (fpcr));
  return 0;
}
'''))

if meson.can_run_host_binaries()
  cfg.set('X87_DOUBLE_ROUNDING', compiler.run('''
#include <stdlib.h>
#include <math.h>
int main(void) {
  volatile double x, y, z;
  /* 1./(1-2**-53) -> 1+2**-52 (correct), 1.0 (double rounding) */
  x = 0.99999999999999989; /* 1-2**-53 */
  y = 1./x;
  if (y != 1.)
    exit(0);
  /* 1e16+2.99999 -> 1e16+2. (correct), 1e16+4. (double rounding) */
  x = 1e16;
  y = 2.99999;
  z = x + y;
  if (z != 1e16+4.)
    exit(0);
  /* both tests show evidence of double rounding */
  exit(1);
}
''').returncode() != 0)
else
  cfg.set('X87_DOUBLE_ROUNDING', false)
endif

cfg.set('HAVE_ACOSH', compiler.has_function('acosh'))
cfg.set('HAVE_ASINH', compiler.has_function('asinh'))
cfg.set('HAVE_ATANH', compiler.has_function('atanh'))
cfg.set('HAVE_ERF', compiler.has_function('erf'))
cfg.set('HAVE_ERFC', compiler.has_function('erfc'))
cfg.set('HAVE_EXPM1', compiler.has_function('expm1'))
cfg.set('HAVE_LOG1P', compiler.has_function('log1p'))
cfg.set('HAVE_LOG2', compiler.has_function('log2'))

if not meson.is_cross_build()
  cfg.set('POSIX_SEMAPHORES_NOT_ENABLED', compiler.run('''
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <semaphore.h>
#include <sys/stat.h>

int main(void) {
  sem_t *a = sem_open("/autoconf", O_CREAT, S_IRUSR|S_IWUSR, 0);
  if (a == SEM_FAILED) {
    perror("sem_open");
    return 1;
  }
  sem_close(a);
  sem_unlink("/autoconf");
  return 0;
}
''').returncode() != 0)

  cfg.set('HAVE_BROKEN_SEM_GETVALUE', (compiler.run('''
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <semaphore.h>
#include <sys/stat.h>

int main(void){
  sem_t *a = sem_open("/autocftw", O_CREAT, S_IRUSR|S_IWUSR, 0);
  int count;
  int res;
  if(a==SEM_FAILED){
    perror("sem_open");
    return 1;
  }
  res = sem_getvalue(a, &count);
  sem_close(a);
  sem_unlink("/autocftw");
  return res==-1 ? 1 : 0;
}
''').returncode() != 0) ? 1 : false)
else
  cfg.set('POSIX_SEMAPHORES_NOT_ENABLED', false)
  cfg.set('HAVE_BROKEN_SEM_GETVALUE', 1)
endif

cfg.set('HAVE_DECL_RTLD_LAZY', compiler.has_define('RTLD_LAZY', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_NOW', compiler.has_define('RTLD_NOW', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_GLOBAL', compiler.has_define('RTLD_GLOBAL', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_LOCAL', compiler.has_define('RTLD_LOCAL', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_NODELETE', compiler.has_define('RTLD_NODELETE', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_NOLOAD', compiler.has_define('RTLD_NOLOAD', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_DEEPBIND', compiler.has_define('RTLD_DEEPBIND', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_MEMBER', compiler.has_define('RTLD_MEMBER', prefix: '#include <dlfcn.h>') ? 1 : 0)

cfg.set('PYLONG_BITS_IN_DIGIT', get_option('bits-in-digit').to_int())

sizeof_wchar_t = compiler.sizeof('wchar_t', prefix: have_wchar_h ? '#include <wchar.h>' : '')
cfg.set('SIZEOF_WCHAR_T', sizeof_wchar_t)
cfg.set('HAVE_USABLE_WCHAR_T', sizeof_wchar_t >= 16)

cfg.set('WORDS_BIGENDIAN', host_machine.endian() == 'big')

cfg.set('HAVE_GETC_UNLOCKED', compiler.has_function('getc_unlocked', prefix: '#include <stdio.h>', args: feature_flags))

cfg.set('HAVE_READLINE_READLINE_H', readline_dep.found())
if readline_dep.found()
  cfg.set('HAVE_RL_COMPLETION_APPEND_CHARACTER', compiler.has_header_symbol('readline/readline.h', 'rl_completion_append_character', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPLETION_SUPPRESS_APPEND', compiler.has_header_symbol('readline/readline.h', 'rl_completion_suppress_append', dependencies: readline_dep))
  cfg.set('HAVE_RL_PRE_INPUT_HOOK', compiler.has_header_symbol('readline/readline.h', 'rl_pre_input_hook', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPLETION_DISPLAY_MATCHES_HOOK', compiler.has_header_symbol('readline/readline.h', 'rl_completion_display_matches_hook', dependencies: readline_dep))
  cfg.set('HAVE_RL_RESIZE_TERMINAL', compiler.has_header_symbol('readline/readline.h', 'rl_resize_terminal', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPLETION_MATCHES', compiler.has_header_symbol('readline/readline.h', 'rl_completion_matches', dependencies: readline_dep))
  cfg.set('HAVE_RL_CATCH_SIGNAL', compiler.has_header_symbol('readline/readline.h', 'rl_catch_signals', dependencies: readline_dep))
  cfg.set('HAVE_RL_APPEND_HISTORY', compiler.has_header_symbol('readline/history.h', 'append_history', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPDISP_FUNC_T', compiler.has_type('rl_compdisp_func_t', prefix: '#include <readline/readline.h>', dependencies: readline_dep))
  cfg.set('Py_RL_STARTUP_HOOK_TAKES_ARGS', compiler.compiles('''
#include <stdio.h> /* Must be first for Gnu Readline */
#include <readline/readline.h>
#include <readline/history.h>

extern int test_hook_func(const char *text, int state);
int main(void) {
  rl_startup_hook=test_hook_func;
  return 0;
}
''', dependencies: readline_dep))
endif

if not meson.is_cross_build()
  cfg.set('HAVE_BROKEN_NICE', compiler.run('''
#include <stdlib.h>
#include <unistd.h>
int main(void) {
  int val1 = nice(1);
  if (val1 != -1 && val1 == nice(2))
    exit(0);
  exit(1);
}
''', args: feature_flags).returncode() == 0)

  cfg.set('HAVE_BROKEN_POLL', compiler.run('''
#include <poll.h>
#include <unistd.h>
int main(void) {
  struct pollfd poll_struct = { 42, POLLIN|POLLPRI|POLLOUT, 0 };
  int poll_test;

  close (42);

  poll_test = poll(&poll_struct, 1, 0);
  if (poll_test < 0)
    return 0;
  else if (poll_test == 0 && poll_struct.revents != POLLNVAL)
    return 0;
  else
    return 1;
}
''').returncode() == 0)

  cfg.set('HAVE_WORKING_TZSET', compiler.run('''
#include <stdlib.h>
#include <time.h>
#include <string.h>

#if @0@
extern char *tzname[];
#endif

int main(void)
{
  /* Note that we need to ensure that not only does tzset(3)
     do 'something' with localtime, but it works as documented
     in the library reference and as expected by the test suite.
     This includes making sure that tzname is set properly if
     tm->tm_zone does not exist since it is the alternative way
     of getting timezone info.

     Red Hat 6.2 doesn't understand the southern hemisphere
     after New Year's Day.
  */

  time_t groundhogday = 1044144000; /* GMT-based */
  time_t midyear = groundhogday + (365 * 24 * 3600 / 2);

  putenv("TZ=UTC+0");
  tzset();
  if (localtime(&groundhogday)->tm_hour != 0)
    exit(1);
#if @0@
  /* For UTC, tzname[1] is sometimes "", sometimes "   " */
  if (strcmp(tzname[0], "UTC") ||
    (tzname[1][0] != 0 && tzname[1][0] != ' '))
    exit(1);
#endif

  putenv("TZ=EST+5EDT,M4.1.0,M10.5.0");
  tzset();
  if (localtime(&groundhogday)->tm_hour != 19)
    exit(1);
#if @0@
  if (strcmp(tzname[0], "EST") || strcmp(tzname[1], "EDT"))
    exit(1);
#endif

  putenv("TZ=AEST-10AEDT-11,M10.5.0,M3.5.0");
  tzset();
  if (localtime(&groundhogday)->tm_hour != 11)
    exit(1);
#if @0@
  if (strcmp(tzname[0], "AEST") || strcmp(tzname[1], "AEDT"))
    exit(1);
#endif

#if @1@
  if (strcmp(localtime(&groundhogday)->tm_zone, "AEDT"))
    exit(1);
  if (strcmp(localtime(&midyear)->tm_zone, "AEST"))
    exit(1);
#endif

  exit(0);
}
'''.format(have_tzname ? 1 : 0, have_struct_tm_tm_zone ? 1 : 0), args: feature_flags).returncode() == 0)
else
  cfg.set('HAVE_BROKEN_NICE', false)
  cfg.set('HAVE_BROKEN_POLL', false)
  cfg.set('HAVE_WORKING_TZSET', false)
endif

cfg.set('HAVE_STAT_TV_NSEC', compiler.has_member('struct stat', 'st_mtim.tv_nsec', prefix: '#include <sys/stat.h>', args: feature_flags))
cfg.set('HAVE_STAT_TV_NSEC2', compiler.has_member('struct stat', 'st_mtimespec.tv_nsec', prefix: '#include <sys/stat.h>', args: feature_flags))

if meson.can_run_host_binaries()
  cfg.set('Py_NORMALIZE_CENTURY', compiler.run('''
#include <time.h>
#include <string.h>

int main(void) {
  char year[5];
  struct tm date = {
    .tm_year = -1801,
    .tm_mon = 0,
    .tm_mday = 1
  };
  if (strftime(year, sizeof(year), "%Y", &date) && !strcmp(year, "0099"))
    return 1;
  return 0;
}
''').returncode() == 0)
else
  cfg.set('Py_NORMALIZE_CENTURY', true)
endif

if ncurses_dep.found()
  cfg.set('HAVE_NCURSESW', have_ncursesw)
  cfg.set('HAVE_PANELW', have_panelw)
  cfg.set('HAVE_NCURSES', not have_ncursesw)
  cfg.set('HAVE_PANEL', not have_panelw)

  cfg.set('HAVE_NCURSESW_CURSES_H', compiler.has_header('ncursesw/curses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSESW_NCURSES_H', compiler.has_header('ncursesw/ncurses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSESW_PANEL_H', compiler.has_header('ncursesw/panel.h', dependencies: ncurses_dep))


  cfg.set('HAVE_NCURSES_CURSES_H', compiler.has_header('ncurses/curses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSES_NCURSES_H', compiler.has_header('ncurses/ncurses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSES_PANEL_H', compiler.has_header('ncurses/panel.h', dependencies: ncurses_dep))

  cfg.set('HAVE_CURSES_H', compiler.has_header('curses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSES_H', compiler.has_header('ncurses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_PANEL_H', compiler.has_header('panel.h', dependencies: ncurses_dep))
  cfg.set('HAVE_TERM_H', compiler.has_header('term.h', dependencies: ncurses_dep))

  # TODO
  cfg.set('MVWDELCH_IS_EXPRESSION', true)
  cfg.set('WINDOW_HAS_FLAGS', false)
  cfg.set('HAVE_CURSES_IS_PAD', true)
  cfg.set('HAVE_CURSES_IS_TERM_RESIZED', true)
  cfg.set('HAVE_CURSES_RESIZE_TERM', true)
  cfg.set('HAVE_CURSES_RESIZETERM', true)
  cfg.set('HAVE_CURSES_IMMEDOK', true)
  cfg.set('HAVE_CURSES_SYNCOK', true)
  cfg.set('HAVE_CURSES_WCHGAT', true)
  cfg.set('HAVE_CURSES_FILTER', true)
  cfg.set('HAVE_CURSES_HAS_KEY', true)
  cfg.set('HAVE_CURSES_TYPEAHEAD', true)
  cfg.set('HAVE_CURSES_USE_ENV', true)
endif

if not meson.is_cross_build()
  fs = import('fs')
  cfg.set('HAVE_DEV_PTMX', fs.exists('/dev/ptmx'))
  cfg.set('HAVE_DEV_PTC', fs.exists('/dev/ptc'))
else
  warning('Cannot check for /dev/ptmx when cross compiling')
endif

have_socklen_t = compiler.has_type('socklen_t', prefix: '@0@\n@1@'.format(have_sys_types_h ? '#include <sys/types.h>' : '', have_sys_socket_h ? '#include <sys/socket.h>' : ''))
cfg.set('HAVE_SOCKLEN_T', have_socklen_t)
if not have_socklen_t
  cfg.set('socklen_t', 'int')
endif

if meson.can_run_host_binaries()
  cfg.set('HAVE_BROKEN_MBSTOWCS', compiler.run('''
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
int main(void) {
  size_t len = -1;
  const char *str = "text";
  len = mbstowcs(NULL, str, 0);
  return (len != 4);
}
''').returncode() != 0)
else
  cfg.set('HAVE_BROKEN_MBSTOWCS', false)
endif

if meson.can_run_host_binaries()
  cfg.set('HAVE_COMPUTED_GOTOS', compiler.run('''
int main(int argc, char **argv) {
  static void *targets[1] = { &&LABEL1 };
  goto LABEL2;
LABEL1:
  return 0;
LABEL2:
  goto *targets[0];
  return 1;
}
''').returncode() == 0)
else
  cfg.set('HAVE_COMPUTED_GOTOS', true) #?
endif

cfg.set('Py_TAIL_CALL_INTERP',false) #option?

if meson.can_run_host_binaries()
  cfg.set('HAVE_GLIBC_MEMMOVE_BUG', compiler.run('''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void foo(void *p, void *q) { memmove(p, q, 19); }
int main(void) {
  char a[32] = "123456789000000000";
  foo(&a[9], a);
  if (strcmp(a, "123456789123456789000000000") != 0)
    return 1;
  foo(a, &a[9]);
  if (strcmp(a, "123456789000000000") != 0)
    return 1;
  return 0;
}
''').returncode() != 0)

  if have_gcc_asm_for_x87
    cfg.set('HAVE_IPA_PURE_CONST_BUG', compiler.run('''
__attribute__((noinline)) int foo(int *p) {
  int r;
  __asm__ ( "movl $6, (%1)\n\t"
            "xorl %0, %0\n\t"
            : "=r" (r) : "r" (p) : "memory"
  );
  return r;
}
int main(void) {
  int p = 8;
  if ((foo(&p) ? : p) != 6)
    return 1;
  return 0;
}
''').returncode() != 0)
  endif
endif

cfg.set('HAVE_DIRENT_D_TYPE', compiler.has_member('struct dirent', 'd_type', prefix: '#include <dirent.h>'))

cfg.set('HAVE_GETRANDOM_SYSCALL', compiler.links('''
#include <stddef.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/random.h>

int main(void) {
  char buffer[1];
  const size_t buflen = sizeof(buffer);
  const int flags = GRND_NONBLOCK;
  /* ignore the result, Python checks for ENOSYS and EAGAIN at runtime */
  (void)syscall(SYS_getrandom, buffer, buflen, flags);
  return 0;
}
''', args: feature_flags))

cfg.set('HAVE_GETRANDOM', compiler.has_function('getrandom', prefix: '#include <sys/random.h>'))

cfg.set('HAVE_SHM_OPEN', compiler.has_function('shm_open', prefix: have_sys_mman_h ? '#include <sys/mman.h>' : ''))
cfg.set('HAVE_SHM_UNLINK', compiler.has_function('shm_unlink', prefix: have_sys_mman_h ? '#include <sys/mman.h>' : ''))

py_ssl_cipher_suite_map = { 'python': 1, 'openssl': 2 }
if get_option('ssl-default-suites') in py_ssl_cipher_suite_map
  cfg.set('PY_SSL_DEFAULT_CIPHERS', py_ssl_cipher_suite_map[get_option('ssl-default-suites')])
else
  cfg.set('PY_SSL_DEFAULT_CIPHERS', 0)
  cfg.set_quoted('PY_SSL_DEFAULT_CIPHER_STRING', get_option('ssl-default-suites'))
endif

cfg.set_quoted('PY_BUILTIN_HASHLIB_HASHES', ','.join(get_option('builtin-hashlib-hashes')))

cfg.set('_PYTHREAD_NAME_MAXLEN', 15) # TODO

hacl_can_compile_simd128 = false
hacl_can_compile_simd256 = false
if host_machine.system() != 'android' and host_machine.system() != 'wasi'
  hacl_simd128_args = compiler.get_supported_arguments('-msse', '-msse2', '-msse3', '-msse4.1', '-msse4.2')
  hacl_can_compile_simd128 = hacl_simd128_args.length() > 0
  hacl_simd256_args = compiler.get_supported_arguments('-mavx2')
  hacl_can_compile_simd256 = hacl_simd256_args.length() > 0
endif
cfg.set('HACL_CAN_COMPILE_SIMD128', hacl_can_compile_simd128 ? 1 : false)
cfg.set('HACL_CAN_COMPILE_SIMD256', hacl_can_compile_simd256 ? 1 : false)

pyconfig = configure_file(output: 'pyconfig.h', configuration: cfg)

if not libmpdec_dep.found()
  subdir('Modules/_decimal/libmpdec')
endif
if not expat_dep.found()
  subdir('Modules/expat')
endif

subdir('Include')
subdir('Objects')
subdir('Parser')
subdir('Python')
subdir('Modules')
subdir('Python/frozen_modules')
private_inc += include_directories('Python')

libpython_lib = library('python', frozen_tgts, 'Python' / 'frozen.c', 'Modules' / 'getpath.c',
  c_args: [ '-DPy_BUILD_CORE' ],
  include_directories: [ inc, private_inc ],
  link_whole: [ python_objects_lib, python_parser_lib, python_python_lib_omit_frozen, python_modules_lib ],
  dependencies: [
    python_modules_dep,
    libm_dep,
    liblog_dep
  ],
  install: true
)

libpython_dep = declare_dependency(
  include_directories: [inc, root_inc],
  link_with: libpython_lib
)

# the dynamic modules need libpython
subdir('Modules/Dynamic')
subdir('Programs')

subdir('Lib')
