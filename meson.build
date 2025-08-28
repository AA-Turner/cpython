project('cpython', 'c',
  version: '3.14.0',
  default_options: ['warning_level=1', 'c_std=c11'],
  meson_version: '>= 1.3.0'
)

version_components = meson.project_version().split('.')
py_release = '@0@.@1@'.format(version_components[0], version_components[1])

with_pydebug = get_option('buildtype') == 'debug'

root_inc = include_directories('.')

cc = meson.get_compiler('c')

libm_dep = cc.find_library('m', required: false)
librt_dep = cc.find_library('rt', required: false)

libmpdec_dep = cc.find_library('mpdec', required: get_option('system-libmpdec'))

bzip_dep = dependency('bzip2')
lzma_dep = dependency('liblzma')
zlib_dep = dependency('zlib')

libdbm_dep = dependency('', required: false)
dbm_libs = {
  'ndbm': { 'lib': 'ndbm', 'cflags': '-DUSE_NDBM', 'headers': [ 'ndbm.h' ] },
  'gdbm': { 'lib': 'gdbm_compat', 'cflags': '-DUSE_GDBM_COMPAT', 'headers': [ 'gdbm/ndbm.h', 'gdbm-ndbm.h' ] },
  'bdb': { 'lib': 'db', 'cflags': '-DUSE_BERKDB', 'headers': [ 'db.h' ] }
}
foreach dbm_lib : get_option('dbm-lib-order')
  dep = cc.find_library(dbm_libs[dbm_lib]['lib'], required: false)
  has_header = false
  foreach header : dbm_libs[dbm_lib]['headers']
    if cc.has_header(header, dependencies: dep)
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
libgdbm_dep = cc.find_library('gdbm', required: false)

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
uuid_dep = dependency('uuid', version: '>= 2.20', required: false)

tcl_dep = dependency('tcl', version: '>= 8.5.12', required: false)
tk_dep = dependency('tk', version: '>= 8.5.12', required: false)

feature_flags = [
  '-D_NETBSD_SOURCE',
  '-D__BSD_VISIBLE',
  '-D_DARWIN_C_SOURCE',
  '-D_XOPEN_SOURCE=700',
  '-D_XOPEN_SOURCE_EXTENDED',
  '-D_POSIX_C_SOURCE=200809L',
  '-D_ALL_SOURCE',
  '-D_DARWIN_C_SOURCE',
  '-D_GNU_SOURCE',
  '-D_HPUX_ALT_XOPEN_SOCKET_API',
  '-D_NETBSD_SOURCE',
  '-D_OPENBSD_SOURCE',
  '-D_POSIX_PTHREAD_SEMANTICS',
]

# these sadly don't count for the compiler check methods
add_project_arguments(feature_flags, language: 'c')

cfg = configuration_data()
cfg.set('STDC_HEADERS', 1)
cfg.set('HAVE_STDIO_H', cc.has_header('stdio.h'))
cfg.set('HAVE_STDLIB_H', cc.has_header('stdlib.h'))
cfg.set('HAVE_STRING_H', cc.has_header('string.h'))
cfg.set('HAVE_INTTYPES_H', cc.has_header('inttypes.h'))
cfg.set('HAVE_STDINT_H', cc.has_header('stdint.h'))
cfg.set('HAVE_STRINGS_H', cc.has_header('strings.h'))
cfg.set('HAVE_SYS_STAT_H', cc.has_header('sys/stat.h'))
have_sys_types_h = cc.has_header('sys/types.h')
cfg.set('HAVE_SYS_TYPES_H', have_sys_types_h)
cfg.set('HAVE_UNISTD_H', cc.has_header('sys/unistd.h'))
have_wchar_h = cc.has_header('wchar.h')
cfg.set('HAVE_WCHAR_H', have_wchar_h)
cfg.set('HAVE_MINIX_CONFIG_H', cc.has_header('minix/config.h'))

cfg.set('PY_SUPPORT_TIER', 0) # Building python with meson is currently not officially supported
cfg.set('Py_GIL_DISABLED', not get_option('gil'))
cfg.set('Py_DEBUG', with_pydebug)
abiflags = (get_option('gil') ? '' : 't') + (with_pydebug ? 'd' : '')
abi = '@0@-@1@'.format(host_machine.cpu_family(), host_machine.system())
soabi = '@0@-@1@@2@-@3@'.format(meson.project_name(), py_release.replace('.', ''), abiflags, abi)
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
  cfg.set('ANDROID_API_LEVEL', cc.get_define('__ANDROID_API__'))
  liblog_dep = cc.find_library('log')
endif

cfg.set('HAVE_ALLOCA_H', cc.has_header('alloca.h'))
cfg.set('HAVE_ASM_TYPES_H', cc.has_header('asm/types.h'))
cfg.set('HAVE_BLUETOOTH_H', cc.has_header('bluetooth.h'))
cfg.set('HAVE_CONIO_H', cc.has_header('conio.h'))
cfg.set('HAVE_DIRECT_H', cc.has_header('direct.h'))
cfg.set('HAVE_DLFCN_H', cc.has_header('dlfcn.h'))
have_endian_h = cc.has_header('endian.h')
cfg.set('HAVE_ENDIAN_H', have_endian_h)
cfg.set('HAVE_ERRNO_H', cc.has_header('errno.h'))
cfg.set('HAVE_FCNTL_H', cc.has_header('fcntl.h'))
have_grp_h = cc.has_header('grp.h')
cfg.set('HAVE_GRP_H', have_grp_h)
cfg.set('HAVE_IO_H', cc.has_header('io.h'))
cfg.set('HAVE_LANGINFO_H', cc.has_header('langinfo.h'))
cfg.set('HAVE_LIBINTL_H', cc.has_header('libintl.h'))
cfg.set('HAVE_LIBUTIL_H', cc.has_header('libutil.h'))
cfg.set('HAVE_LINUX_AUXVEC_H', cc.has_header('linux/auxvec.h'))
cfg.set('HAVE_SYS_AUXV_H', cc.has_header('sys/auxv.h'))
cfg.set('HAVE_LINUX_FS_H', cc.has_header('linux/fs.h'))
cfg.set('HAVE_LINUX_LIMITS_H', cc.has_header('linux/limits.h'))
cfg.set('HAVE_LINUX_MEMFD_H', cc.has_header('linux/memfd.h'))
cfg.set('HAVE_LINUX_NETFILTER_IPV4_H', cc.has_header('linux/netfilter_ipv4.h'))
cfg.set('HAVE_LINUX_RANDOM_H', cc.has_header('linux/random.h'))
cfg.set('HAVE_LINUX_SOUNDCARD_H', cc.has_header('linux/soundcard.h'))
cfg.set('HAVE_LINUX_SCHED_H', cc.has_header('linux/sched.h'))
cfg.set('HAVE_LINUX_TIPC_H', cc.has_header('linux/tipc.h'))
cfg.set('HAVE_LINUX_WAIT_H', cc.has_header('linux/wait.h'))
cfg.set('HAVE_NETDB_H', cc.has_header('netdb.h'))
cfg.set('HAVE_NET_ETHERNET_H', cc.has_header('net/ethernet.h'))
cfg.set('HAVE_NETINET_IN_H', cc.has_header('netinet/in.h'))
cfg.set('HAVE_NETPACKET_PACKET_H', cc.has_header('netpacket/packet.h'))
cfg.set('HAVE_POLL_H', cc.has_header('poll.h'))
cfg.set('HAVE_PROCESS_H', cc.has_header('process.h'))
cfg.set('HAVE_PTHREAD_H', cc.has_header('pthread.h'))
cfg.set('HAVE_PTY_H', cc.has_header('pty.h'))
cfg.set('HAVE_SCHED_H', cc.has_header('sched.h'))
cfg.set('HAVE_SETJMP_H', cc.has_header('setjmp.h'))
cfg.set('HAVE_SHADOW_H', cc.has_header('shadow.h'))
cfg.set('HAVE_SIGNAL_H', cc.has_header('signal.h'))
cfg.set('HAVE_SPAWN_H', cc.has_header('spawn.h'))
cfg.set('HAVE_STROPTS_H', cc.has_header('stdopts.h'))
cfg.set('HAVE_SYS_AUDIOIO_H', cc.has_header('sys/audioio.h'))
cfg.set('HAVE_SYS_BSDTTY_H', cc.has_header('bsd/bsdtty.h'))
cfg.set('HAVE_SYS_DEVPOLL_H', cc.has_header('sys/devpoll.h'))
have_sys_endian_h = cc.has_header('sys/endian.h')
cfg.set('HAVE_SYS_ENDIAN_H', have_sys_endian_h)
cfg.set('HAVE_SYS_EPOLL_H', cc.has_header('sys/epoll.h'))
cfg.set('HAVE_SYS_EVENT_H', cc.has_header('sys/event.h'))
cfg.set('HAVE_SYS_EVENTFD_H', cc.has_header('sys/eventfd.h'))
cfg.set('HAVE_SYS_FILE_H', cc.has_header('sys/file.h'))
cfg.set('HAVE_SYS_IOCTL_H', cc.has_header('sys/ioctl.h'))
cfg.set('HAVE_SYS_KERN_CONTROL_H', cc.has_header('sys/kern_control.h'))
cfg.set('HAVE_SYS_LOADAVG_H', cc.has_header('sys/loadavg.h'))
cfg.set('HAVE_SYS_LOCK_H', cc.has_header('sys/lock.h'))
have_sys_memfd_h = cc.has_header('sys/memfd.h')
cfg.set('HAVE_SYS_MEMFD_H', have_sys_memfd_h)
cfg.set('HAVE_SYS_MKDEV_H', cc.has_header('sys/mkdev.h'))
have_sys_mman_h = cc.has_header('sys/mman.h')
cfg.set('HAVE_SYS_MMAN_H', cc.has_header('sys/mman.h'))
cfg.set('HAVE_SYS_MODEM_H', cc.has_header('sys/modem.h'))
cfg.set('HAVE_SYS_PARAM_H', cc.has_header('sys/param.h'))
cfg.set('HAVE_SYS_PIDFD_H', cc.has_header('sys/pidfd.h'))
cfg.set('HAVE_SYS_POLL_H', cc.has_header('sys/poll.h'))
cfg.set('HAVE_SYS_RANDOM_H', cc.has_header('sys/random.h'))
cfg.set('HAVE_SYS_RESOURCE_H', cc.has_header('sys/resource.h'))
cfg.set('HAVE_SYS_SELECT_H', cc.has_header('sys/select.h'))
cfg.set('HAVE_SYS_SENDFILE_H', cc.has_header('sys/sendfile.h'))
have_sys_socket_h = cc.has_header('sys/socket.h')
cfg.set('HAVE_SYS_SOCKET_H', cc.has_header('sys/socket.h'))
cfg.set('HAVE_SYS_SOUNDCARD_H', cc.has_header('sys/soundcard.h'))
cfg.set('HAVE_SYS_STAT_H', cc.has_header('sys/stat.h'))
cfg.set('HAVE_SYS_STATVFS_H', cc.has_header('sys/statvfs.h'))
cfg.set('HAVE_SYS_SYS_DOMAIN_H', cc.has_header('sys/sys_domain.h'))
cfg.set('HAVE_SYS_SYSCALL_H', cc.has_header('sys/syscall.h'))
cfg.set('HAVE_SYS_SYSMACROS_H', cc.has_header('sys/sysmacros.h'))
cfg.set('HAVE_SYS_TERMIO_H', cc.has_header('sys/termio.h'))
have_sys_time_h = cc.has_header('sys/time.h')
cfg.set('HAVE_SYS_TIME_H', have_sys_time_h)
cfg.set('HAVE_SYS_TIMES_H', cc.has_header('sys/times.h'))
cfg.set('HAVE_SYS_TIMERFD_H', cc.has_header('sys/timerfd.h'))
cfg.set('HAVE_SYS_TYPES_H', cc.has_header('sys/types.h'))
cfg.set('HAVE_SYS_UIO_H', cc.has_header('sys/uio.h'))
cfg.set('HAVE_SYS_UN_H', cc.has_header('sys/un.h'))
cfg.set('HAVE_SYS_UTSNAME_H', cc.has_header('sys/utsname.h'))
cfg.set('HAVE_SYS_WAIT_H', cc.has_header('sys/wait.h'))
cfg.set('HAVE_SYS_XATTR_H', cc.has_header('sys/xattr.h'))
cfg.set('HAVE_SYSEXITS_H', cc.has_header('sysexits.h'))
cfg.set('HAVE_SYSLOG_H', cc.has_header('syslog.h'))
cfg.set('HAVE_TERMIOS_H', cc.has_header('termios.h'))
cfg.set('HAVE_UTIL_H', cc.has_header('util.h'))
cfg.set('HAVE_UTIME_H', cc.has_header('utime.h'))
cfg.set('HAVE_UTMP_H', cc.has_header('utmp.h'))

foreach header : [
  { 'def': 'HAVE_DIRENT_H', 'header': 'dirent.h' },
  { 'def': 'HAVE_SYS_NDIR_H', 'header': 'sys/ndir.h' },
  { 'def': 'HAVE_SYS_DIR_H', 'header': 'sys/dir.h' },
  { 'def': 'HAVE_NDIR_H', 'header': 'ndir.h' }
]
  if cc.has_type('DIR*', prefix: '#include <@0@>'.format(header['header']))
    cfg.set(header['def'], true)
    break
  endif
endforeach

major_in_mkdev = cc.has_header('sys/mkdev.h')
cfg.set('MAJOR_IN_MKDEV', major_in_mkdev)
major_in_sysmacros = cc.has_header('sys/sysmacros.h')
cfg.set('MAJOR_IN_SYSMACROS', major_in_sysmacros)

# bluetooth/bluetooth.h has been known to not compile with -std=c99.
# http://permalink.gmane.org/gmane.linux.bluez.kernel/22294
cfg.set('HAVE_BLUETOOTH_BLUETOOTH_H', cc.has_header('bluetooth/bluetooth.h')) # TODO

cfg.set('HAVE_NET_IF_H', cc.has_header('net/if.h'))

cfg.set('HAVE_LINUX_NETLINK_H', cc.has_header('linux/netlink.h'))
cfg.set('HAVE_NETLINK_NETLINK_H', cc.has_header('netlink/netlink.h'))

cfg.set('HAVE_LINUX_QRTR_H', cc.has_header('linux/qrtr.h'))
cfg.set('HAVE_LINUX_VM_SOCKETS_H', cc.has_header('linux/vm_sockets.h'))

cfg.set('HAVE_LINUX_CAN_H', cc.has_header('linux/can.h'))
cfg.set('HAVE_LINUX_CAN_BCM_H', cc.has_header('linux/can/bcm.h'))
cfg.set('HAVE_LINUX_CAN_J1939_H', cc.has_header('linux/can/j1939.h'))
cfg.set('HAVE_LINUX_CAN_RAW_H', cc.has_header('linux/can/raw.h'))

cfg.set('HAVE_NETCAN_CAN_H', cc.has_header('netcan/can.h'))

if cc.has_type('clock_t', prefix: '#include <time.h>')
  cfg.set('HAVE_CLOCK_T', true)
else
  cfg.set('clock_t', 'long')
endif

cfg.set('HAVE_MAKEDEV', cc.compiles('''
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

cfg.set('HAVE_DEVICE_MACROS', cc.compiles('''
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

cfg.set('HAVE_HTOLE64', cc.compiles('''
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

if not cc.has_type('mode_t', prefix: '#include <sys/types.h>')
  cfg.set('mode_t', 'int')
endif

if not cc.has_type('off_t', prefix: '#include <sys/types.h>')
  cfg.set('off_t', 'long int')
endif

if not cc.has_type('pid_t', prefix: '#include <sys/types.h>')
  if cc.compiles('''
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

if not cc.has_type('size_t', prefix: '#include <stddef.h>')
  cfg.set('size_t', '(unsigned int)')
endif

if not cc.has_type('uid_t', prefix: '#include <sys/types.h>')
  cfg.set('uid_t', 'int')
endif

if not cc.has_type('gid_t', prefix: '#include <sys/types.h>')
  cfg.set('gid_t', 'int')
endif

cfg.set('HAVE_SSIZE_T', cc.has_type('ssize_t', prefix: '#include <sys/types.h>') ? 1 : 0)

have_uint128_t = cc.has_type('__uint128_t')
cfg.set('HAVE___UINT128_T', have_uint128_t)
cfg.set('HAVE_GCC_UINT128_T', have_uint128_t)

cfg.set('SIZEOF_INT', cc.sizeof('int'))
size_long = cc.sizeof('long')
cfg.set('SIZEOF_LONG', size_long)
cfg.set('ALIGNOF_LONG', cc.alignment('long'))
size_long_long = cc.sizeof('long long')
cfg.set('SIZEOF_LONG_LONG', size_long_long)
cfg.set('SIZEOF_VOID_P', cc.sizeof('void*'))
cfg.set('SIZEOF_SHORT', cc.sizeof('short'))
cfg.set('SIZEOF_FLOAT', cc.sizeof('float'))
cfg.set('SIZEOF_DOUBLE', cc.sizeof('double'))
cfg.set('SIZEOF_FPOS_T', cc.sizeof('fpos_t'))
cfg.set('SIZEOF_SIZE_T', cc.sizeof('size_t'))
cfg.set('ALIGNOF_SIZE_T', cc.alignment('size_t'))
cfg.set('SIZEOF_PID_T', cc.sizeof('pid_t', prefix: '#include <sys/types.h>'))
cfg.set('SIZEOF_UINTPTR_T', cc.sizeof('uintptr_t', prefix: '#include <stdint.h>'))
cfg.set('ALIGNOF_MAX_ALIGN_T', cc.alignment('max_align_t'))
if cc.has_type('long double')
  cfg.set('HAVE_LONG_DOUBLE', true)
  cfg.set('SIZEOF_LONG_DOUBLE', cc.sizeof('long double'))
endif
cfg.set('SIZEOF__BOOL', cc.sizeof('_Bool'))
size_off_t = cc.sizeof('off_t', prefix: '#include <sys/types.h>')
cfg.set('SIZEOF_OFF_T', size_off_t)

cfg.set('HAVE_LARGEFILE_SUPPORT', size_off_t > size_long and size_long_long >= size_off_t)

cfg.set('SIZEOF_TIME_T', cc.sizeof('time_t', prefix: '#include <time.h>'))
if cc.has_type('pthread_t', prefix: '#include <pthread.h>')
  cfg.set('SIZEOF_PTHREAD_T', cc.sizeof('pthread_t', prefix: '#include <pthread.h>'))
  cfg.set('SIZEOF_PTHREAD_KEY_T', cc.sizeof('pthread_key_t', prefix: '#include <pthread.h>'))

  # Issue #25658: POSIX hasn't defined that pthread_key_t is compatible with int.
  # This checking will be unnecessary after removing deprecated TLS API.
  # The cast to long int works around a bug in the HP C Compiler
  # version HP92453-01 B.11.11.23709.GP, which incorrectly rejects
  # declarations like 'int a3[[(sizeof (unsigned char)) >= 0]];'.
  # This bug is HP SR number 8606223364.
  cfg.set('PTHREAD_KEY_T_IS_COMPATIBLE_WITH_INT', cc.compiles('''
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

sendfile_lib = cc.find_library('sendfile', required: false)
if sendfile_lib.found()
  cfg.set('HAVE_LIBSENDFILE', cc.links('''
#ifdef __cplusplus
extern "C"
#endif
char sendfile(void);
int main(void) {
  return sendfile();
}
'''))
endif

dl_lib = cc.find_library('dl', required: false)
if dl_lib.found()
  cfg.set('HAVE_LIBDL', cc.links('''
#ifdef __cplusplus
extern "C"
#endif
char dlopen(void);
int main(void) {
  return dlopen();
}
'''))
endif

dld_lib = cc.find_library('dld', required: false)
if dld_lib.found()
  cfg.set('HAVE_LIBDLD', cc.links('''
#ifdef __cplusplus
extern "C"
#endif
char shl_load(void);
int main(void) {
  return shl_load();
}
'''))
endif

have_uuid = cc.has_header('uuid.h') or uuid_dep.found()
cfg.set('HAVE_UUID_H', have_uuid)
if have_uuid
  cfg.set('HAVE_UUID_GENERATE_TIME_SAFE', cc.links('''
#ifdef __cplusplus
extern "C"
#endif
char uuid_generate_time_safe(void);
int main(void) {
  return uuid_generate_time_safe();
}
''', dependencies: uuid_dep))
endif

intl_lib = cc.find_library('intl', required: false)
cfg.set('HAVE_LIBINTL', cc.links('''
#ifdef __cplusplus
extern "C"
#endif
char textdomain(void);
int main(void) {
  return textdomain();
}
''', dependencies: intl_lib))

if meson.can_run_host_binaries()
  cfg.set('Py_HAVE_C_COMPLEX', cc.run('''
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
  cfg.set('HAVE_ALIGNED_REQUIRED', cc.run('''
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
    cfg.set('HAVE_FFI_PREP_CIF_VAR', cc.has_function('ffi_prep_cif_var', prefix: '#include <ffi.h>', dependencies: ffi_dep) ? 1 : 0)
    cfg.set('HAVE_FFI_PREP_CLOSURE_LOC', cc.has_function('ffi_prep_closure_loc', prefix: '#include <ffi.h>', dependencies: ffi_dep) ? 1 : 0)
    cfg.set('HAVE_FFI_CLOSURE_ALLOC', cc.has_function('ffi_closure_alloc', prefix: '#include <ffi.h>', dependencies: ffi_dep) ? 1 : 0)

    # Check for libffi with real complex double support.
    # # This is a workaround, since FFI_TARGET_HAS_COMPLEX_TYPE was defined in libffi v3.2.1,
    # # but real support was provided only in libffi v3.3.0.
    # # See https://github.com/python/cpython/issues/125206 for more details.
    if meson.can_run_host_binaries()
      cfg.set('Py_FFI_SUPPORT_C_COMPLEX', cc.run('''
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

if sqlite3_dep.found() and cc.has_header('sqlite3.h', dependencies: sqlite3_dep)
  needed_funcs = [ 'sqlite3_bind_double', 'sqlite3_column_decltype', 'sqlite3_column_double', 'sqlite3_complete', 'sqlite3_progress_handler', 'sqlite3_result_double', 'sqlite3_set_authorizer', 'sqlite3_trace_v2', 'sqlite3_value_double' ]
  have_sqlite3 = true
  foreach func : needed_funcs
    if not cc.has_function(func, prefix: '#include <sqlite3.h>', dependencies: sqlite3_dep)
      have_sqlite3 = false
      break
    endif
  endforeach
  cfg.set('HAVE_LIBSQLITE3', have_sqlite3)
  cfg.set('PY_SQLITE_HAVE_SERIALIZE', cc.has_function('sqlite3_serialize', prefix: '#include <sqlite3.h>', dependencies: sqlite3_dep))
  cfg.set('PY_SQLITE_ENABLE_LOAD_EXTENSION', cc.has_function('sqlite3_load_extension', prefix: '#include <sqlite3.h>', dependencies: sqlite3_dep, required: get_option('loadable-sqlite-extensions')))
endif

if libgdbm_dep.found()
  cfg.set('HAVE_GDBM_H', cc.has_header('gdbm.h', dependencies: libgdbm_dep))
endif
if libdbm_dep.found()
  cfg.set('HAVE_NDBM_H', cc.has_header('ndbm.h', dependencies: libdbm_dep))
  cfg.set('HAVE_GDBM_NDBM_H', cc.has_header('gdbm/ndbm.h', dependencies: libdbm_dep))
  cfg.set('HAVE_GDBM_DASH_NDBM_H', cc.has_header('gdbm-ndbm.h', dependencies: libdbm_dep))
  cfg.set('HAVE_DB_H', cc.has_header('db.h', dependencies: libdbm_dep))
endif


cfg.set('_REENTRANT', 1)
cfg.set('PTHREAD_SYSTEM_SCHED_SUPPORTED', true) # TODO
have_sigmask = cc.has_function('pthread_sigmask', prefix: '#include <pthread.h>\n#include <signal.h>', args: feature_flags)
cfg.set('HAVE_PTHREAD_SIGMASK', have_sigmask)
if have_sigmask and host_machine.system() == 'cygwin'
  cfg.set('HAVE_BROKEN_PTHREAD_SIGMASK', true)
endif
cfg.set('HAVE_PTHREAD_GETCPUCLOCKID', cc.has_function('pthread_getcpuclockid', prefix: '#include <pthread.h>', args: feature_flags))

cfg.set('ENABLE_IPV6',
  cc.has_define('AF_INET6', prefix: '#include <sys/types.h>\n#include <sys/socket.h>') and # required in has_define would be nice
  cc.has_member('struct sockaddr_in6', 'sin6_scope_id', prefix: '#include <sys/types.h>\n#include <netinet/in.h>', required: get_option('ipv6'))
)
cfg.set('HAVE_LINUX_CAN_RAW_FD_FRAMES', cc.has_header_symbol('linux/can/raw.h', 'CAN_RAW_FD_FRAMES'))
cfg.set('HAVE_LINUX_CAN_RAW_JOIN_FILTERS', cc.has_header_symbol('linux/can/raw.h', 'CAN_RAW_JOIN_FILTERS'))

cfg.set('WITH_DOC_STRINGS', get_option('doc-strings'))

cfg.set('HAVE_STD_ATOMIC', cc.links('''
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

cfg.set('HAVE_BUILTIN_ATOMIC', cc.links('''
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

cfg.set('HAVE_DLOPEN', cc.has_function('dlopen'))
# TODO: dynload_file
cfg.set('HAVE_DYNAMIC_LOADING', true)

cfg.set('HAVE_ACCEPT4', cc.has_function('accept4'))
cfg.set('HAVE_ALARM', cc.has_function('alarm'))
cfg.set('HAVE_BIND_TEXTDOMAIN_CODESET', cc.has_function('bind_textdomain_codeset'))
cfg.set('HAVE_CHMOD', cc.has_function('chmod'))
cfg.set('HAVE_CHOWN', cc.has_function('chown'))
cfg.set('HAVE_CLOCK', cc.has_function('clock'))
cfg.set('HAVE_CLOSEFROM', cc.has_function('closefrom'))
cfg.set('HAVE_CLOSE_RANGE', cc.has_function('close_range'))
cfg.set('HAVE_CONFSTR', cc.has_function('confstr'))
cfg.set('HAVE_COPY_FILE_RANGE', cc.has_function('copy_file_range'))
cfg.set('HAVE_CTERMID', cc.has_function('ctermid'))
cfg.set('HAVE_DLADDR', cc.has_function('dladdr'))
cfg.set('HAVE_DUP', cc.has_function('dup'))
cfg.set('HAVE_DUP3', cc.has_function('dup3'))
cfg.set('HAVE_EXECV', cc.has_function('execv'))
have_explicit_bzero = cc.has_function('explicit_bzero')
cfg.set('HAVE_EXPLICIT_BZERO', have_explicit_bzero)
cfg.set('HAVE_EXPLICIT_MEMSET', cc.has_function('explicit_memset'))
cfg.set('HAVE_FACCESSAT', cc.has_function('faccessat'))
cfg.set('HAVE_FCHMOD', cc.has_function('fchmod'))
cfg.set('HAVE_FCHMODAT', cc.has_function('fchmodat'))
cfg.set('HAVE_FCHOWN', cc.has_function('fchown'))
cfg.set('HAVE_FCHOWNAT', cc.has_function('fchownat'))
cfg.set('HAVE_FDOPENDIR', cc.has_function('fdopendir'))
cfg.set('HAVE_FDWALK', cc.has_function('fdwalk'))
cfg.set('HAVE_FEXECVE', cc.has_function('fexecve'))
cfg.set('HAVE_FORK', cc.has_function('fork'))
cfg.set('HAVE_FORK1', cc.has_function('fork1'))
cfg.set('HAVE_FPATHCONF', cc.has_function('fpathconf'))
cfg.set('HAVE_FSTATAT', cc.has_function('fstatat'))
cfg.set('HAVE_FTIME', cc.has_function('ftime'))
cfg.set('HAVE_FTRUNCATE', cc.has_function('ftruncate'))
cfg.set('HAVE_FUTIMENS', cc.has_function('futimens'))
cfg.set('HAVE_FUTIMES', cc.has_function('futimes'))
cfg.set('HAVE_FUTIMESAT', cc.has_function('futimesat'))
cfg.set('HAVE_GAI_STRERROR', cc.has_function('gai_strerror'))
cfg.set('HAVE_GETEGID', cc.has_function('getegid'))
cfg.set('HAVE_GETEUID', cc.has_function('geteuid'))
cfg.set('HAVE_GETGID', cc.has_function('getgid'))
cfg.set('HAVE_GETGRENT', cc.has_function('getgrent'))
cfg.set('HAVE_GETGRGID', cc.has_function('getgrgid'))
cfg.set('HAVE_GETGRGID_R', cc.has_function('getgrgid_r'))
cfg.set('HAVE_GETGRNAM_R', cc.has_function('getgrnam_r'))
cfg.set('HAVE_GETGROUPLIST', cc.has_function('getgrouplist'))
cfg.set('HAVE_GETHOSTNAME', cc.has_function('gethostname'))
cfg.set('HAVE_GETITIMER', cc.has_function('getitimer'))
cfg.set('HAVE_GETLOADAVG', cc.has_function('getloadavg'))
cfg.set('HAVE_GETLOGIN', cc.has_function('getlogin'))
cfg.set('HAVE_GETPEERNAME', cc.has_function('getpeername'))
cfg.set('HAVE_GETPGID', cc.has_function('getpgid'))
cfg.set('HAVE_GETPID', cc.has_function('getpid'))
cfg.set('HAVE_GETPPID', cc.has_function('getppid'))
cfg.set('HAVE_GETPRIORITY', cc.has_function('getpriority'))
cfg.set('HAVE__GETPTY', cc.has_function('_getpty'))
cfg.set('HAVE_GETPWENT', cc.has_function('getpwent'))
cfg.set('HAVE_GETPWNAM_R', cc.has_function('getpwnam_r'))
cfg.set('HAVE_GETPWUID', cc.has_function('getpwuid'))
cfg.set('HAVE_GETPWUID_R', cc.has_function('getpwuid_r'))
cfg.set('HAVE_GETRESGID', cc.has_function('getresgid'))
cfg.set('HAVE_GETRESUID', cc.has_function('getresuid'))
cfg.set('HAVE_GETRUSAGE', cc.has_function('getrusage'))
cfg.set('HAVE_GETSID', cc.has_function('getsid'))
cfg.set('HAVE_GETSPENT', cc.has_function('getspent'))
cfg.set('HAVE_GETSPNAM', cc.has_function('getspnam'))
cfg.set('HAVE_GETUID', cc.has_function('getuid'))
cfg.set('HAVE_GETWD', cc.has_function('getwd'))
cfg.set('HAVE_GRANTPT', cc.has_function('grantpt'))
cfg.set('HAVE_IF_NAMEINDEX', cc.has_function('if_nameindex'))
cfg.set('HAVE_INITGROUPS', cc.has_function('initgroups'))
cfg.set('HAVE_KILL', cc.has_function('kill'))
cfg.set('HAVE_KILLPG', cc.has_function('killpg'))
cfg.set('HAVE_LCHOWN', cc.has_function('lchown'))
cfg.set('HAVE_LINKAT', cc.has_function('linkat'))
cfg.set('HAVE_LOCKF', cc.has_function('lockf'))
cfg.set('HAVE_LSTAT', cc.has_function('lstat'))
cfg.set('HAVE_LUTIMES', cc.has_function('lutimes'))
cfg.set('HAVE_MADVISE', cc.has_function('madvise'))
cfg.set('HAVE_MBRTOWC', cc.has_function('mbrtowc'))
cfg.set('HAVE_MEMRCHR', cc.has_function('memrchr'))
cfg.set('HAVE_MKDIRAT', cc.has_function('mkdirat') ? 1 : 0)
cfg.set('HAVE_MKFIFO', cc.has_function('mkfifo'))
cfg.set('HAVE_MKFIFOAT', cc.has_function('mkfifoat'))
cfg.set('HAVE_MKNOD', cc.has_function('mknod'))
cfg.set('HAVE_MKNODAT', cc.has_function('mknodat'))
cfg.set('HAVE_MKTIME', cc.has_function('mktime'))
cfg.set('HAVE_MMAP', cc.has_function('mmap'))
cfg.set('HAVE_MREMAP', cc.has_function('mremap'))
cfg.set('HAVE_NICE', cc.has_function('nice'))
cfg.set('HAVE_OPENAT', cc.has_function('openat'))
cfg.set('HAVE_OPENDIR', cc.has_function('opendir'))
cfg.set('HAVE_PATHCONF', cc.has_function('pathconf'))
cfg.set('HAVE_PAUSE', cc.has_function('pause'))
cfg.set('HAVE_PIPE', cc.has_function('pipe'))
cfg.set('HAVE_PIPE2', cc.has_function('pipe2'))
cfg.set('HAVE_PLOCK', cc.has_function('plock'))
cfg.set('HAVE_POLL', cc.has_function('poll'))
cfg.set('HAVE_POSIX_FADVISE', cc.has_function('posix_fadvise'))
cfg.set('HAVE_POSIX_FALLOCATE', cc.has_function('posix_fallocate'))
cfg.set('HAVE_POSIX_OPENPT', cc.has_function('posix_openpt'))
cfg.set('HAVE_POSIX_SPAWN', cc.has_function('posix_spawn'))
cfg.set('HAVE_POSIX_SPAWNP', cc.has_function('posix_spawnp'))
cfg.set('HAVE_POSIX_SPAWN_FILE_ACTIONS_ADDCLOSEFROM_NP', cc.has_function('posix_spawn_file_actions_addclosefrom_np'))
cfg.set('HAVE_PREAD', cc.has_function('pread'))
cfg.set('HAVE_PREADV', cc.has_function('preadv'))
cfg.set('HAVE_PREADV2', cc.has_function('preadv2'))
cfg.set('HAVE_PROCESS_VM_READV', cc.has_function('process_vm_readv'))
cfg.set('HAVE_PTHREAD_COND_TIMEDWAIT_RELATIVE_NP', cc.has_function('pthread_cond_timedwait_relative_np'))
cfg.set('HAVE_PTHREAD_CONDATTR_SETCLOCK', cc.has_function('pthread_condattr_setclock'))
cfg.set('HAVE_PTHREAD_INIT', cc.has_function('pthread_init'))
cfg.set('HAVE_PTHREAD_KILL', cc.has_function('pthread_kill'))
cfg.set('HAVE_PTHREAD_GETNAME_NP', cc.has_function('pthread_getname_np'))
cfg.set('HAVE_PTHREAD_SETNAME_NP', cc.has_function('pthread_setname_np'))
cfg.set('HAVE_PTSNAME', cc.has_function('ptsname'))
cfg.set('HAVE_PTSNAME_R', cc.has_function('ptsname_r'))
cfg.set('HAVE_PWRITE', cc.has_function('pwrite'))
cfg.set('HAVE_PWRITEV', cc.has_function('pwritev'))
cfg.set('HAVE_PWRITEV2', cc.has_function('pwritev2'))
cfg.set('HAVE_READLINK', cc.has_function('readlink'))
cfg.set('HAVE_READLINKAT', cc.has_function('readlinkat'))
cfg.set('HAVE_READV', cc.has_function('readv'))
cfg.set('HAVE_REALPATH', cc.has_function('realpath'))
cfg.set('HAVE_RENAMEAT', cc.has_function('renameat'))
cfg.set('HAVE_RTPSPAWN', cc.has_function('rtpSpawn'))
cfg.set('HAVE_SCHED_GET_PRIORITY_MAX', cc.has_function('sched_get_priority_max'))
cfg.set('HAVE_SCHED_RR_GET_INTERVAL', cc.has_function('sched_rr_get_interval'))
cfg.set('HAVE_SCHED_SETAFFINITY', cc.has_function('sched_setaffinity'))
cfg.set('HAVE_SCHED_SETPARAM', cc.has_function('sched_setparam'))
cfg.set('HAVE_SCHED_SETSCHEDULER', cc.has_function('sched_setscheduler'))
cfg.set('HAVE_SEM_CLOCKWAIT', cc.has_function('sem_clockwait') ? 1 : 0)
cfg.set('HAVE_SEM_GETVALUE', cc.has_function('sem_getvalue') ? 1 : 0)
cfg.set('HAVE_SEM_OPEN', cc.has_function('sem_open') ? 1 : 0)
cfg.set('HAVE_SEM_TIMEDWAIT', cc.has_function('sem_timedwait') ? 1 : 0)
cfg.set('HAVE_SEM_UNLINK', cc.has_function('sem_unlink') ? 1 : 0)
cfg.set('HAVE_SENDFILE', cc.has_function('sendfile'))
cfg.set('HAVE_SETEGID', cc.has_function('setegid'))
cfg.set('HAVE_SETEUID', cc.has_function('seteuid'))
cfg.set('HAVE_SETGID', cc.has_function('setgid'))
cfg.set('HAVE_SETHOSTNAME', cc.has_function('sethostname'))
cfg.set('HAVE_SETITIMER', cc.has_function('setitimer'))
cfg.set('HAVE_SETLOCALE', cc.has_function('setlocale'))
cfg.set('HAVE_SETPGID', cc.has_function('setpgid'))
cfg.set('HAVE_SETPGRP', cc.has_function('setpgrp'))
cfg.set('HAVE_SETPRIORITY', cc.has_function('setpriority'))
cfg.set('HAVE_SETREGID', cc.has_function('setregid'))
cfg.set('HAVE_SETRESGID', cc.has_function('setresgid'))
cfg.set('HAVE_SETRESUID', cc.has_function('setresuid'))
cfg.set('HAVE_SETREUID', cc.has_function('setreuid'))
cfg.set('HAVE_SETSID', cc.has_function('setsid'))
cfg.set('HAVE_SETUID', cc.has_function('setuid'))
cfg.set('HAVE_SETVBUF', cc.has_function('setvbuf'))
cfg.set('HAVE_SHUTDOWN', cc.has_function('shutdown'))
cfg.set('HAVE_SIGACTION', cc.has_function('sigaction'))
cfg.set('HAVE_SIGALTSTACK', cc.has_function('sigaltstack'))
cfg.set('HAVE_SIGFILLSET', cc.has_function('sigfillset'))
cfg.set('HAVE_SIGINTERRUPT', cc.has_function('siginterrupt'))
cfg.set('HAVE_SIGPENDING', cc.has_function('sigpending'))
cfg.set('HAVE_SIGRELSE', cc.has_function('sigrelse'))
cfg.set('HAVE_SIGTIMEDWAIT', cc.has_function('sigtimedwait'))
cfg.set('HAVE_SIGWAIT', cc.has_function('sigwait'))
cfg.set('HAVE_SIGWAITINFO', cc.has_function('sigwaitinfo'))
cfg.set('HAVE_SNPRINTF', cc.has_function('snprintf'))
cfg.set('HAVE_SPLICE', cc.has_function('splice'))
cfg.set('HAVE_STRFTIME', cc.has_function('strftime'))
cfg.set('HAVE_STRLCPY', cc.has_function('strlcpy'))
cfg.set('HAVE_STRSIGNAL', cc.has_function('strsignal'))
cfg.set('HAVE_SYMLINKAT', cc.has_function('symlinkat'))
cfg.set('HAVE_SYNC', cc.has_function('sync'))
cfg.set('HAVE_SYSCONF', cc.has_function('sysconf'))
cfg.set('HAVE_TCGETPGRP', cc.has_function('tcgetpgrp'))
cfg.set('HAVE_TCSETPGRP', cc.has_function('tcsetpgrp'))
cfg.set('HAVE_TEMPNAM', cc.has_function('tempnam'))
cfg.set('HAVE_TIMEGM', cc.has_function('timegm'))
cfg.set('HAVE_TIMES', cc.has_function('times'))
cfg.set('HAVE_TMPFILE', cc.has_function('tmpfile'))
cfg.set('HAVE_TMPNAM', cc.has_function('tmpnam'))
cfg.set('HAVE_TMPNAM_R', cc.has_function('tmpnam_r'))
cfg.set('HAVE_TRUNCATE', cc.has_function('truncate'))
cfg.set('HAVE_TTYNAME_R', cc.has_function('ttyname_r'))
cfg.set('HAVE_UMASK', cc.has_function('umask'))
cfg.set('HAVE_UNAME', cc.has_function('uname'))
cfg.set('HAVE_UNLINKAT', cc.has_function('unlinkat'))
cfg.set('HAVE_UNLOCKPT', cc.has_function('unlockpt'))
cfg.set('HAVE_UTIMENSAT', cc.has_function('utimensat'))
cfg.set('HAVE_UTIMES', cc.has_function('utimes'))
cfg.set('HAVE_VFORK', cc.has_function('vfork'))
cfg.set('HAVE_WAIT', cc.has_function('wait'))
cfg.set('HAVE_WAIT3', cc.has_function('wait3'))
cfg.set('HAVE_WAIT4', cc.has_function('wait4'))
cfg.set('HAVE_WAITID', cc.has_function('waitid'))
cfg.set('HAVE_WAITPID', cc.has_function('waitpid'))
cfg.set('HAVE_WCSCOLL', cc.has_function('wcscoll'))
cfg.set('HAVE_WCSFTIME', cc.has_function('wcsftime'))
cfg.set('HAVE_WCSXFRM', cc.has_function('wcsxfrm'))
cfg.set('HAVE_WMEMCMP', cc.has_function('wmemcmp'))
cfg.set('HAVE_WRITEV', cc.has_function('writev'))
cfg.set('HAVE_GETENTROPY', cc.has_function('getentropy'))
cfg.set('HAVE_GETGROUPS', cc.has_function('getgroups'))
cfg.set('HAVE_SYSTEM', cc.has_function('system'))

cfg.set('HAVE_DIRFD',cc.has_function('dirfd', prefix: '#include <sys/types.h>\n#include <dirent.h>', args: feature_flags))

cfg.set('HAVE_CHROOT', cc.has_function('chroot'))
cfg.set('HAVE_LINK', cc.has_function('link'))
cfg.set('HAVE_SYMLINK', cc.has_function('symlink'))
cfg.set('HAVE_FCHDIR', cc.has_function('fchdir'))
cfg.set('HAVE_FSYNC', cc.has_function('fsync'))
cfg.set('HAVE_FDATASYNC', cc.has_function('fdatasync'))
cfg.set('HAVE_EPOLL', cc.has_function('epoll_create', prefix: '#include <sys/epoll.h>'))
cfg.set('HAVE_EPOLL_CREATE1', cc.has_function('epoll_create1', prefix: '#include <sys/epoll.h>'))
cfg.set('HAVE_KQUEUE', cc.has_function('kqueue', prefix: '#include <sys/types.h>\n#include <sys/event.h>'))
cfg.set('HAVE_PRLIMIT', cc.has_function('prlimit', prefix: '#include <sys/time.h>\n#include <sys/resource.h>', args: feature_flags))
cfg.set('HAVE_DYLD_SHARED_CACHE_CONTAINS_PATH', cc.has_function('_dyld_shared_cache_contains_path', prefix: '#include <mach-o/dyld.h>'))
cfg.set('HAVE_MEMFD_CREATE', cc.has_function('memfd_create', prefix: '@0@\n@1@'.format(have_sys_mman_h ? '#include <sys/mman.h>' : '', have_sys_memfd_h ? '#include <sys/memfd.h>' : ''), args: feature_flags))
cfg.set('HAVE_EVENTFD', cc.has_function('eventfd', prefix: '#include <sys/eventfd.h>'))
cfg.set('HAVE_TIMERFD_CREATE', cc.has_function('timerfd_create', prefix: '#include <sys/timerfd.h>'))
cfg.set('HAVE_CTERMID_R', cc.has_function('ctermid_r'))
cfg.set('HAVE_FLOCK', cc.has_function('flock', prefix: '#include <sys/file.h>'))
cfg.set('HAVE_GETPAGESIZE', cc.has_function('getpagesize'))
cfg.set('HAVE_BROKEN_UNSETENV', not cc.compiles('''
#include <stdlib.h>
int main(void) {
  return unsetenv("DUMMY");
}
''', args: feature_flags))
cfg.set('HAVE_CHFLAGS', cc.has_function('chflags'))
cfg.set('HAVE_LCHFLAGS', cc.has_function('lchflags'))

cfg.set('HAVE_ZLIB_H', zlib_dep.found())
if zlib_dep.found()
  cfg.set('HAVE_ZLIB_COPY', cc.has_function('inflateCopy', prefix: '#include <zlib.h>', dependencies: zlib_dep))
endif
cfg.set('HAVE_BZLIB_H', bzip_dep.found())
cfg.set('HAVE_LZMA_H', lzma_dep.found())

cfg.set('HAVE_HSTRERROR', cc.has_function('hstrerror', prefix: '#include <netdb.h>', args: feature_flags))
cfg.set('HAVE_GETSERVBYNAME', cc.has_function('getservbyname', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETSERVBYPORT', cc.has_function('getservbyport', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETHOSTBYNAME', cc.has_function('gethostbyname', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETHOSTBYADDR', cc.has_function('gethostbyaddr', prefix: '#include <netdb.h>'))
cfg.set('HAVE_GETPROTOBYNAME', cc.has_function('getprotobyname', prefix: '#include <netdb.h>'))

net_prefix = '''
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
'''
cfg.set('HAVE_INET_ATON', cc.has_function('inet_aton', prefix: net_prefix, args: feature_flags))
cfg.set('HAVE_INET_NTOA', cc.has_function('inet_ntoa', prefix: net_prefix, args: feature_flags))
cfg.set('HAVE_INET_PTON', cc.has_function('inet_pton', prefix: net_prefix, args: feature_flags))
cfg.set('HAVE_GETPEERNAME', cc.has_function('getpeername', prefix: net_prefix))
cfg.set('HAVE_GETSOCKNAME', cc.has_function('getsockname', prefix: net_prefix))
cfg.set('HAVE_ACCEPT', cc.has_function('accept', prefix: net_prefix))
cfg.set('HAVE_BIND', cc.has_function('bind', prefix: net_prefix))
cfg.set('HAVE_CONNECT', cc.has_function('connect', prefix: net_prefix))
cfg.set('HAVE_LISTEN', cc.has_function('listen', prefix: net_prefix))
cfg.set('HAVE_RECVFROM', cc.has_function('recvfrom', prefix: net_prefix))
cfg.set('HAVE_SENDTO', cc.has_function('sendto', prefix: net_prefix))
cfg.set('HAVE_SETSOCKOPT', cc.has_function('setsockopt', prefix: net_prefix))
cfg.set('HAVE_SOCKET', cc.has_function('socket', prefix: net_prefix))

cfg.set('HAVE_SETGROUPS', cc.has_function('setgroups', prefix: '#include <unistd.h>\n@0@'.format(have_grp_h ? '#include <grp.h>' : ''), args: feature_flags))

cfg.set('HAVE_OPENPTY', cc.has_function('openpty'))
cfg.set('HAVE_LOGIN_TTY', cc.has_function('login_tty'))
cfg.set('HAVE_FORKPTY', cc.has_function('forkpty'))

cfg.set('HAVE_FSEEK64', cc.has_function('fseek64'))
cfg.set('HAVE_FSEEKO', cc.has_function('fseeko'))
cfg.set('HAVE_FSTATVFS', cc.has_function('fstatvfs'))
cfg.set('HAVE_FTELL64', cc.has_function('ftell64'))
cfg.set('HAVE_FTELLO', cc.has_function('ftello'))
cfg.set('HAVE_STATVFS', cc.has_function('statvfs'))
cfg.set('HAVE_DUP2', cc.has_function('dup2'))

cfg.set('HAVE_GETPGRP', cc.has_function('getpgrp', prefix: '#include <unistd.h>', args: feature_flags))
cfg.set('GETPGRP_HAVE_ARG', cc.compiles('#include <unistd.h>\nint main(void) { getpgrp(0); return 0; }', args: feature_flags))
cfg.set('HAVE_SETPGRP', cc.has_function('setpgrp', prefix: '#include <unistd.h>', args: feature_flags))
cfg.set('SETPGRP_HAVE_ARG', cc.compiles('#include <unistd.h>\nint main(void) { setpgrp(0, 0); return 0; }', args: feature_flags))

cfg.set('HAVE_SETNS', cc.has_function('setns'))
cfg.set('HAVE_UNSHARE', cc.has_function('unshare'))

cfg.set('HAVE_CLOCK_GETTIME', cc.has_function('clock_gettime', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_CLOCK_GETRES', cc.has_function('clock_getres', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_CLOCK_SETTIME', cc.has_function('clock_settime', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_CLOCK_NANOSLEEP', cc.has_function('clock_nanosleep', prefix: '#include <time.h>', args: feature_flags))
cfg.set('HAVE_NANOSLEEP', cc.has_function('nanosleep', prefix: '#include <time.h>', args: feature_flags))

addr_prefix = '''
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>
'''
cfg.set('HAVE_GETADDRINFO', cc.has_function('getaddrinfo', prefix: addr_prefix, args: feature_flags))
cfg.set('HAVE_GETNAMEINFO', cc.has_function('getnameinfo', prefix: addr_prefix, args: feature_flags))

have_struct_tm = cc.has_type('struct tm', prefix: '#include <sys/types.h>\n#include <time.h>')
cfg.set('TM_IN_SYS_TIME', not have_struct_tm and have_sys_time_h)
tm_struct_header = (not have_struct_tm and have_sys_time_h) ? 'sys/time.h' : 'time.h'
have_struct_tm_tm_zone = cc.has_member('struct tm', 'tm_zone', prefix: '#include <sys/types.h>\n#include <@0@>'.format(tm_struct_header), args: feature_flags)
cfg.set('HAVE_STRUCT_TM_TM_ZONE', have_struct_tm_tm_zone)
cfg.set('HAVE_TM_ZONE', have_struct_tm_tm_zone)
cfg.set('HAVE_DECL_TZNAME', cc.has_function('tzname', prefix: '#include <time.h>'))
have_tzname = cc.has_header_symbol('time.h', 'tzname')
cfg.set('HAVE_TZNAME', have_tzname)

cfg.set('HAVE_STRUCT_STAT_ST_RDEV', cc.has_member('struct stat', 'st_rdev', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_BLKSIZE', cc.has_member('struct stat', 'st_blksize', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_FLAGS', cc.has_member('struct stat', 'st_flags', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_GEN', cc.has_member('struct stat', 'st_gen', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_BIRTHTIME', cc.has_member('struct stat', 'st_birthtime', prefix: '#include <sys/stat.h>'))
cfg.set('HAVE_STRUCT_STAT_ST_BLOCKS', cc.has_member('struct stat', 'st_blocks', prefix: '#include <sys/stat.h>'))

cfg.set('HAVE_STRUCT_PASSWD_PW_GECOS', cc.has_member('struct passwd', 'pw_gecos', prefix: '#include <sys/types.h>\n#include <pwd.h>'))
cfg.set('HAVE_STRUCT_PASSWD_PW_PASSWD', cc.has_member('struct passwd', 'pw_passwd', prefix: '#include <sys/types.h>\n#include <pwd.h>'))

cfg.set('HAVE_SIGINFO_T_SI_BAND', cc.has_member('siginfo_t', 'si_band', prefix: '#include <signal.h>', args: feature_flags))
cfg.set('HAVE_ALTZONE', cc.has_header_symbol('time.h', 'altzone'))

socket_prefix = '''
#include <sys/types.h>
#include <sys/socket.h>
'''
cfg.set('HAVE_ADDRINFO', cc.has_type('struct addrinfo', prefix: '#include <netdb.h>', args: feature_flags))
cfg.set('HAVE_SOCKADDR_STORAGE', cc.has_type('struct sockaddr_storage', prefix: socket_prefix, args: feature_flags))
cfg.set('HAVE_SOCKADDR_ALG', cc.has_type('struct sockaddr_alg', prefix: socket_prefix + '\n#include <linux/if_alg.h>', args: feature_flags))
cfg.set('HAVE_PROTOTYPES', cc.compiles('''
int foo(int x) { return 0; }
int main(void) {
  return foo(10);
}
'''))
cfg.set('HAVE_SOCKETPAIR', cc.has_function('socketpair', prefix: socket_prefix))
cfg.set('HAVE_SOCKADDR_SA_LEN', cc.has_member('struct sockaddr', 'sa_len', prefix: socket_prefix))

cfg.set('HAVE_GETHOSTBYNAME_R', cc.has_function('gethostbyname_r', prefix: '#include <netdb.h>', args: feature_flags))
cfg.set('HAVE_GETHOSTBYNAME_R_6_ARG', cc.compiles('''
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
cfg.set('HAVE_GETHOSTBYNAME_R_5_ARG', cc.compiles('''
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
cfg.set('HAVE_GETHOSTBYNAME_R_3_ARG', cc.compiles('''
#include <netdb.h>

int main(void) {
  char *name;
  struct hostent *he;
  struct hostent_data data;
  (void) gethostbyname_r(name, he, &data);
  return 0;
}
''', args: feature_flags))

cfg.set('HAVE_GCC_ASM_FOR_X64', cc.links('''
int main(void) {
  __asm__ __volatile__ ("movq %rcx, %rax");
  return 0;
}
'''))

# TODO: this doesn't actually work when you can't run host binaries
first = cc.compute_int('((unsigned char*)&v)[0]', prefix: 'static const double v = -0.f;')
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

have_gcc_asm_for_x87 = cc.links('''
int main(void) {
  unsigned short cw;
  __asm__ __volatile__ ("fnstcw %0" : "=m" (cw));
  __asm__ __volatile__ ("fldcw %0" : : "m" (cw));
  return 0;
}
''')
cfg.set('HAVE_GCC_ASM_FOR_X87', have_gcc_asm_for_x87)
cfg.set('HAVE_GCC_ASM_FOR_MC68881', cc.links('''
int main(void) {
  unsigned int fpcr;
  __asm__ __volatile__ ("fmove.l %%fpcr,%0" : "=g" (fpcr));
  __asm__ __volatile__ ("fmove.l %0,%%fpcr" : : "g" (fpcr));
  return 0;
}
'''))

if meson.can_run_host_binaries()
  cfg.set('X87_DOUBLE_ROUNDING', cc.run('''
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

cfg.set('HAVE_ACOSH', cc.has_function('acosh'))
cfg.set('HAVE_ASINH', cc.has_function('asinh'))
cfg.set('HAVE_ATANH', cc.has_function('atanh'))
cfg.set('HAVE_ERF', cc.has_function('erf'))
cfg.set('HAVE_ERFC', cc.has_function('erfc'))
cfg.set('HAVE_EXPM1', cc.has_function('expm1'))
cfg.set('HAVE_LOG1P', cc.has_function('log1p'))
cfg.set('HAVE_LOG2', cc.has_function('log2'))

if not meson.is_cross_build()
  cfg.set('POSIX_SEMAPHORES_NOT_ENABLED', cc.run('''
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

  cfg.set('HAVE_BROKEN_SEM_GETVALUE', (cc.run('''
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

cfg.set('HAVE_DECL_RTLD_LAZY', cc.has_define('RTLD_LAZY', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_NOW', cc.has_define('RTLD_NOW', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_GLOBAL', cc.has_define('RTLD_GLOBAL', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_LOCAL', cc.has_define('RTLD_LOCAL', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_NODELETE', cc.has_define('RTLD_NODELETE', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_NOLOAD', cc.has_define('RTLD_NOLOAD', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_DEEPBIND', cc.has_define('RTLD_DEEPBIND', prefix: '#include <dlfcn.h>') ? 1 : 0)
cfg.set('HAVE_DECL_RTLD_MEMBER', cc.has_define('RTLD_MEMBER', prefix: '#include <dlfcn.h>') ? 1 : 0)

cfg.set('PYLONG_BITS_IN_DIGIT', get_option('bits-in-digit').to_int())

sizeof_wchar_t = cc.sizeof('wchar_t', prefix: have_wchar_h ? '#include <wchar.h>' : '')
cfg.set('SIZEOF_WCHAR_T', sizeof_wchar_t)
cfg.set('HAVE_USABLE_WCHAR_T', sizeof_wchar_t >= 16)

cfg.set('WORDS_BIGENDIAN', host_machine.endian() == 'big')

cfg.set('HAVE_GETC_UNLOCKED', cc.has_function('getc_unlocked', prefix: '#include <stdio.h>', args: feature_flags))

cfg.set('HAVE_READLINE_READLINE_H', readline_dep.found())
if readline_dep.found()
  cfg.set('HAVE_RL_COMPLETION_APPEND_CHARACTER', cc.has_header_symbol('readline/readline.h', 'rl_completion_append_character', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPLETION_SUPPRESS_APPEND', cc.has_header_symbol('readline/readline.h', 'rl_completion_suppress_append', dependencies: readline_dep))
  cfg.set('HAVE_RL_PRE_INPUT_HOOK', cc.has_header_symbol('readline/readline.h', 'rl_pre_input_hook', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPLETION_DISPLAY_MATCHES_HOOK', cc.has_header_symbol('readline/readline.h', 'rl_completion_display_matches_hook', dependencies: readline_dep))
  cfg.set('HAVE_RL_RESIZE_TERMINAL', cc.has_header_symbol('readline/readline.h', 'rl_resize_terminal', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPLETION_MATCHES', cc.has_header_symbol('readline/readline.h', 'rl_completion_matches', dependencies: readline_dep))
  cfg.set('HAVE_RL_CATCH_SIGNAL', cc.has_header_symbol('readline/readline.h', 'rl_catch_signals', dependencies: readline_dep))
  cfg.set('HAVE_RL_APPEND_HISTORY', cc.has_header_symbol('readline/history.h', 'append_history', dependencies: readline_dep))
  cfg.set('HAVE_RL_COMPDISP_FUNC_T', cc.has_type('rl_compdisp_func_t', prefix: '#include <readline/readline.h>', dependencies: readline_dep))
  cfg.set('Py_RL_STARTUP_HOOK_TAKES_ARGS', cc.compiles('''
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
  cfg.set('HAVE_BROKEN_NICE', cc.run('''
#include <stdlib.h>
#include <unistd.h>
int main(void) {
  int val1 = nice(1);
  if (val1 != -1 && val1 == nice(2))
    exit(0);
  exit(1);
}
''', args: feature_flags).returncode() == 0)

  cfg.set('HAVE_BROKEN_POLL', cc.run('''
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

  cfg.set('HAVE_WORKING_TZSET', cc.run('''
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

cfg.set('HAVE_STAT_TV_NSEC', cc.has_member('struct stat', 'st_mtim.tv_nsec', prefix: '#include <sys/stat.h>', args: feature_flags))
cfg.set('HAVE_STAT_TV_NSEC2', cc.has_member('struct stat', 'st_mtimespec.tv_nsec', prefix: '#include <sys/stat.h>', args: feature_flags))

if meson.can_run_host_binaries()
  cfg.set('Py_NORMALIZE_CENTURY', cc.run('''
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

  cfg.set('HAVE_NCURSESW_CURSES_H', cc.has_header('ncursesw/curses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSESW_NCURSES_H', cc.has_header('ncursesw/ncurses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSESW_PANEL_H', cc.has_header('ncursesw/panel.h', dependencies: ncurses_dep))


  cfg.set('HAVE_NCURSES_CURSES_H', cc.has_header('ncurses/curses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSES_NCURSES_H', cc.has_header('ncurses/ncurses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSES_PANEL_H', cc.has_header('ncurses/panel.h', dependencies: ncurses_dep))

  cfg.set('HAVE_CURSES_H', cc.has_header('curses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_NCURSES_H', cc.has_header('ncurses.h', dependencies: ncurses_dep))
  cfg.set('HAVE_PANEL_H', cc.has_header('panel.h', dependencies: ncurses_dep))
  cfg.set('HAVE_TERM_H', cc.has_header('term.h', dependencies: ncurses_dep))

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

have_socklen_t = cc.has_type('socklen_t', prefix: '@0@\n@1@'.format(have_sys_types_h ? '#include <sys/types.h>' : '', have_sys_socket_h ? '#include <sys/socket.h>' : ''))
cfg.set('HAVE_SOCKLEN_T', have_socklen_t)
if not have_socklen_t
  cfg.set('socklen_t', 'int')
endif

if meson.can_run_host_binaries()
  cfg.set('HAVE_BROKEN_MBSTOWCS', cc.run('''
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
  cfg.set('HAVE_COMPUTED_GOTOS', cc.run('''
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
  cfg.set('HAVE_GLIBC_MEMMOVE_BUG', cc.run('''
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
    cfg.set('HAVE_IPA_PURE_CONST_BUG', cc.run('''
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

cfg.set('HAVE_DIRENT_D_TYPE', cc.has_member('struct dirent', 'd_type', prefix: '#include <dirent.h>'))

cfg.set('HAVE_GETRANDOM_SYSCALL', cc.links('''
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

cfg.set('HAVE_GETRANDOM', cc.has_function('getrandom', prefix: '#include <sys/random.h>'))

cfg.set('HAVE_SHM_OPEN', cc.has_function('shm_open', prefix: have_sys_mman_h ? '#include <sys/mman.h>' : ''))
cfg.set('HAVE_SHM_UNLINK', cc.has_function('shm_unlink', prefix: have_sys_mman_h ? '#include <sys/mman.h>' : ''))

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
  hacl_simd128_args = cc.get_supported_arguments('-msse', '-msse2', '-msse3', '-msse4.1', '-msse4.2')
  hacl_can_compile_simd128 = hacl_simd128_args.length() > 0
  hacl_simd256_args = cc.get_supported_arguments('-mavx2')
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
  link_whole: [ python_objects_lib, python_parser_lib, python_python_lib_omit_frozen ],
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
