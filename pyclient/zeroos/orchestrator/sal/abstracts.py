class Mountable:
    """
    Abstract implementation for devices that are mountable.
    Device should have attributes devicename and mountpoint
    """

    def mount(self, target, options=['defaults']):
        """
        @param target: Mount point
        @param options: Optional mount options
        """
        if self.mountpoint == target:
            return

        self._client.bash('mkdir -p {}'.format(target))

        self._client.disk.mount(
            source=self.devicename,
            target=target,
            options=options,
        )

        self.mountpoint = target

    def umount(self):
        """
        Unmount disk
        """
        if self.mountpoint:
            self._client.disk.umount(
                source=self.mountpoint,
            )
        self.mountpoint = None
