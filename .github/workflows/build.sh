set -eux

./configure --config-cache --with-pydebug
make -j4
! ./python ./crasher.py
