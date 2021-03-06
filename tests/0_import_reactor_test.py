# -*- coding: utf-8 -*-
"""
Why this file start with 0?
This test file should be run as first because it tests that twisted reactor
is not initialized at fido import time. Since some other tests later will
explicitly import reactor (initializing it), we must run this file as first.
"""
import psutil
import sys

from subprocess import PIPE
from subprocess import Popen


class TestTwistedReactorNotInitImportTime(object):
    """
    This class is trying to test that fido is (and stays) daemonization-safe.
    Fido is still not fork safe and forking is discouraged.
    """

    @staticmethod
    def count_pipes():
        """
        This helper runs lsof for the current process and counts how many pipes
        are open. When twisted reactor is initialized, at least a new pipe is
        created for the eventpoll.
        """
        pipes = 0

        pid = psutil.Process().pid
        subproc = Popen(['lsof', '-p', str(pid)], stdout=PIPE)
        lsof_lines = subproc.communicate()[0].decode().split('\n')

        for line in lsof_lines:
            if 'PIPE' in line:
                pipes = pipes + 1

        return pipes

    def test_twisted_reactor_not_imported_after_fetch_import(self):
        """
        Test that:
        - reactor is not imported (and initialized) as a result of
            importing fido modules and methods.
        - no new pipes are created (eventpoll would create a new pipe)
        """

        assert 'twisted.internet.reactor' not in sys.modules
        pipes_before = self.count_pipes()

        import fido  # noqa
        from fido.fido import fetch  # noqa

        assert 'twisted.internet.reactor' not in sys.modules
        assert self.count_pipes() == pipes_before
