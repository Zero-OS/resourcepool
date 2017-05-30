aptupdate() {
    force=$1
    lastupdate=$(stat /var/cache/apt/pkgcache.bin | grep Modify | awk '{print $2}')
    today=$(date +%Y-%m-%d)
    if [ "$lastupdate" != "$today" ]; then
        force=y
    fi
    if [ -n "$force" ]; then
        apt-get update
    fi

}

aptinstall() {
    name=$1
    if ! dpkg-query -s "$name" &> /dev/null; then
        aptupdate
        apt-get install -y $name
    fi
}

copypkg() {
   pkgname=$1
   target=$2
   for file in $(dpkg -L $pkgname); do
      if [ -d "$file" ]; then
         continue
      fi
      dirname=$(dirname $file)
      if [[ "$dirname" == /usr/share/man* ]]; then
         continue
      fi
      if [[ "$dirname" == /usr/share/doc* ]]; then
         continue
      fi
      targetdir="${target}${dirname}"
      mkdir -p "$targetdir"
      cp $file "$targetdir"
      if file "$file" | grep dynamic; then
         lddcopy "$file" "$target"
      fi
   done
}

ensure_lddcopy() {
   aptinstall git
   if ! which lddcopy; then
      pushd /tmp
      git clone --depth=1 https://github.com/maxux/lddcopy.git
      cp /tmp/lddcopy/lddcopy.sh /usr/local/bin/lddcopy
      chmod +x /usr/local/bin/lddcopy
      popd
   fi
}

ensure_go() {
   aptinstall curl
   aptinstall git
   if ! which go; then
      curl https://storage.googleapis.com/golang/go1.8.linux-amd64.tar.gz > /tmp/go1.8.linux-amd64.tar.gz
      tar -C /usr/local -xzf /tmp/go1.8.linux-amd64.tar.gz
      export PATH=$PATH:/usr/local/go/bin
   fi
   mkdir -p /gopath
   export GOPATH=/gopath

}
