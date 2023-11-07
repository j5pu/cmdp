# shellcheck shell=sh disable=SC2015,SC2034
TEST_MACOS="$(uname -a | grep -i darwin 2>/dev/null)"
TEST_LOGNAME="$( if test -n "${TEST_MACOS}"; then stat -f "%Su" /dev/console; else logname 2>/dev/null || echo "root"; fi)"
TEST_LOGNAMEHOME="$( eval echo ~"${TEST_LOGNAME}" )"
TEST_ROOTHOME="$( eval echo ~root )"

if test -n "${TEST_MACOS}"; then
  TEST_LOGGEDINUSER="$( echo "show State:/Users/ConsoleUser" | scutil | awk '/Name :/ && ! /loginwindow/ {print $3}' )"
  TEST_LOGNAMEREALNAME="$( dscl . -read /Users/"${TEST_LOGNAME}" RealName RealName | sed -n 's/^ //g;2p' )"
else
  TEST_LOGGEDINUSER="$( whoami )"
  TEST_LOGNAMEREALNAME="$( id -nu )"
fi

TEST_MULTILINE="
First
Second
Last
"
