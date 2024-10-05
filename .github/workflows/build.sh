set -eux

./configure --config-cache --with-pydebug
make -j4
./python ./crasher.py
if [ $? -eq 139 ]; then
  exit 1
else
  exit 0
fi
