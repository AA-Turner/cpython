set -euxo pipefail

./configure --config-cache --with-pydebug
make -j4
./python ./crasher.py
