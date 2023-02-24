#!/usr/bin/env bash
set -e
directory=$1
repository=$2
version=$3

cd ~/.tscan-deps
if [ ! -d $directory ];
then
    git clone $repository
fi
cd $directory
old_commit_hash=$(git rev-parse HEAD)
if [[ $version != $old_commit_hash ]];
then
    echo "Resetting to $version"
    git pull
    git reset --hard $version
else
    echo "No need to reset: $old_commit_hash"
fi

commit_hash=$(git rev-parse HEAD)
# only build if something changed
if [[ $commit_hash != $old_commit_hash ]]; then
    echo "Building $1..."
    bash bootstrap.sh
    ./configure $OPENMPFLAG
    make
else
    echo "Skip building $1: nothing changed"
fi
# always install - the VM is blank
sudo make install
