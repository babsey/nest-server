import unittest
from unittest import mock

from nest_server.mpi.main import (
    master_receive_gather,
    master_send_bcast,
    worker_receive_bcast,
    worker_send_gather,
)


def make_comm(rank: int) -> mock.Mock:
    comm = mock.Mock()
    comm.Get_rank.return_value = rank
    return comm


class TestMasterSendBcast(unittest.TestCase):
    def test_broadcasts_call_name_and_data(self):
        comm = make_comm(0)
        log = mock.Mock()

        result = master_send_bcast(log, comm, "Create", ["iaf_psc_alpha"], {"n": 2})

        self.assertIsNone(result)
        self.assertEqual(
            comm.bcast.call_args_list,
            [
                mock.call("Create", root=0),
                mock.call((["iaf_psc_alpha"], {"n": 2}), root=0),
            ],
        )
        self.assertEqual(log.call_count, 2)
        for log_call in log.call_args_list:
            self.assertEqual(log_call.args[0], "Create")

    def test_fails_on_worker_rank(self):
        comm = make_comm(1)
        with self.assertRaises(AssertionError):
            master_send_bcast(mock.Mock(), comm, "Create", [], {})
        comm.bcast.assert_not_called()


class TestMasterReceiveGather(unittest.TestCase):
    def test_gathers_responses(self):
        comm = make_comm(0)
        comm.gather.return_value = [1, 2, 3]
        log = mock.Mock()

        result = master_receive_gather(log, comm, "GetKernelStatus", 1)

        self.assertEqual(result, [1, 2, 3])
        comm.gather.assert_called_once_with(1, root=0)
        self.assertEqual(log.call_count, 2)
        self.assertIn("[1, 2, 3]", log.call_args_list[-1].args[1])

    def test_fails_on_worker_rank(self):
        comm = make_comm(2)
        with self.assertRaises(AssertionError):
            master_receive_gather(mock.Mock(), comm, "GetKernelStatus", None)
        comm.gather.assert_not_called()


class TestWorkerReceiveBcast(unittest.TestCase):
    def test_receives_call_name_and_data(self):
        comm = make_comm(1)
        comm.bcast.side_effect = ["Create", (["iaf_psc_alpha"], {"n": 2})]
        log = mock.Mock()

        call_name, args, kwargs = worker_receive_bcast(log, comm)

        self.assertEqual(call_name, "Create")
        self.assertEqual(args, ["iaf_psc_alpha"])
        self.assertEqual(kwargs, {"n": 2})
        self.assertEqual(comm.bcast.call_args_list, [mock.call(None, root=0)] * 2)
        self.assertEqual(log.call_count, 3)
        self.assertEqual(log.call_args_list[0].args[0], "spinwait")

    def test_fails_on_master_rank(self):
        comm = make_comm(0)
        with self.assertRaises(AssertionError):
            worker_receive_bcast(mock.Mock(), comm)
        comm.bcast.assert_not_called()


class TestWorkerSendGather(unittest.TestCase):
    def test_sends_response(self):
        comm = make_comm(3)
        log = mock.Mock()

        result = worker_send_gather(log, comm, "Simulate", {"a": 1})

        self.assertIsNone(result)
        comm.gather.assert_called_once_with({"a": 1}, root=0)
        log.assert_called_once()

    def test_fails_on_master_rank(self):
        comm = make_comm(0)
        with self.assertRaises(AssertionError):
            worker_send_gather(mock.Mock(), comm, "Simulate", None)
        comm.gather.assert_not_called()


class TestMasterWorkerRoundTrip(unittest.TestCase):
    """Simulate the bcast protocol between master and worker with a shared channel."""

    def test_round_trip(self):
        channel = []

        master = make_comm(0)
        master.bcast.side_effect = lambda obj, root: channel.append(obj) or obj

        worker = make_comm(1)
        worker.bcast.side_effect = lambda obj, root: channel.pop(0)

        master_send_bcast(mock.Mock(), master, "SetStatus", [[1, 2]], {"params": {"V_m": -70.0}})
        call_name, args, kwargs = worker_receive_bcast(mock.Mock(), worker)

        self.assertEqual(call_name, "SetStatus")
        self.assertEqual(args, [[1, 2]])
        self.assertEqual(kwargs, {"params": {"V_m": -70.0}})
        self.assertEqual(channel, [])


if __name__ == "__main__":
    unittest.main()
