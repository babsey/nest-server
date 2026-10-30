import unittest

from nest_server.mpi import state


class TestMpiState(unittest.TestCase):
    def setUp(self):
        self._original = state.mpi_comm
        state.mpi_comm = None

    def tearDown(self):
        state.mpi_comm = self._original

    def test_default_has_no_comm(self):
        self.assertIsNone(state.get_mpi_comm())
        self.assertFalse(state.has_mpi_comm())

    def test_set_and_get_comm(self):
        comm = object()
        state.set_mpi_comm(comm)
        self.assertIs(state.get_mpi_comm(), comm)
        self.assertTrue(state.has_mpi_comm())

    def test_set_comm_overrides_previous(self):
        first, second = object(), object()
        state.set_mpi_comm(first)
        state.set_mpi_comm(second)
        self.assertIs(state.get_mpi_comm(), second)

    def test_reset_comm_to_none(self):
        state.set_mpi_comm(object())
        state.set_mpi_comm(None)
        self.assertIsNone(state.get_mpi_comm())
        self.assertFalse(state.has_mpi_comm())

    def test_comm_fallback_type_without_mpi4py(self):
        # Without mpi4py installed `Comm` falls back to `object`.
        self.assertTrue(isinstance(state.Comm, type))


if __name__ == "__main__":
    unittest.main()
