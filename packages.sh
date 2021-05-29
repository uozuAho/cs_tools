#!/bin/bash
#
# Print all packages and versions referenced by all C# projects
# under the given directory.

set -eu

ROOT=$1

grep -rih --include *.csproj "PackageReference" $ROOT \
  | sed -E 's/.*Include="(.*)"\sVersion="(.*)".*/\1 \2/' \
  | sort \
  | uniq
