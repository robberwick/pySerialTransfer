import os
import pty
import pytest
from pytest_mock import mocker
from pySerialTransfer.pySerialTransfer import (
    SerialTransfer,
    serial_ports,
    InvalidSerialPort,
)


class TestSerialPorts(object):
    def test_serial_ports(self, mocker):
        """serial_ports() should return a list of the serial ports available on the system, as reported by
        serial.tools.list_ports.com_ports()"""
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[
                mocker.Mock(device="/dev/this_is_a_serial_device"),
                mocker.Mock(device="/dev/this_is_another_serial_device"),
            ],
        )

        assert serial_ports() == [
            "/dev/this_is_a_serial_device",
            "/dev/this_is_another_serial_device",
        ]


class TestSerialTransfer(object):
    def test_serial_port_basic(self, mocker):
        """Passing a vald serial port should result in a SerialTransfer object with the correct port_name"""
        serial_port_list = ["/dev/this_is_a_serial_device"]
        test_port = "/dev/this_is_a_serial_device"
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[mocker.Mock(device=item) for item in serial_port_list],
        )
        st = SerialTransfer(test_port)
        assert st.port_name == test_port

    def test_serial_port_shorthand(self, mocker):
        """It should be possible to pass a serial device using the shorthand name i.e. ttyUSB0 instead of /dev/ttyUSB0"""

        serial_port_list = ["/dev/this_is_a_serial_device"]
        test_port = "this_is_a_serial_device"
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[mocker.Mock(device=item) for item in serial_port_list],
        )
        st = SerialTransfer(test_port)
        assert st.port_name == serial_port_list[0]
        assert st.connection.port == st.port_name

    def test_invalid_serial_port_restricted_by_default(self, mocker):
        serial_port_list = ["this_is_a_serial_device"]
        test_port = "my_serial_port"
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[mocker.Mock(device=item) for item in serial_port_list],
        )
        with pytest.raises(InvalidSerialPort) as e:
            st = SerialTransfer(test_port)

        assert (
            str(e.value)
            == "Invalid serial port specified.\
                    Valid options are {ports},  but {port} was provided".format(
                **{"ports": serial_port_list, "port": test_port}
            )
        )

    def test_invalid_serial_port_unrestricted(self, mocker):
        serial_port_list = ["this_is_a_serial_device"]
        test_port = "my_serial_port"
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[mocker.Mock(device=item) for item in serial_port_list],
        )
        st = SerialTransfer(test_port, restrict_ports=False)
        assert st.port_name == test_port
        assert st.connection.port == st.port_name

    def test_baud_rate_default(self, mocker):
        serial_port_list = ["my_serial_port"]
        test_port = "my_serial_port"
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[mocker.Mock(device=item) for item in serial_port_list],
        )
        st = SerialTransfer(test_port)
        assert st.connection.baudrate == 115200

    def test_baud_rate_configurable(self, mocker):
        """Test that is is possible to set the baud rate via the SerialTransfer constructor"""
        serial_port_list = ["my_serial_port"]
        test_port = "my_serial_port"
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[mocker.Mock(device=item) for item in serial_port_list],
        )

        expected_baud_rate = 9600
        st = SerialTransfer(test_port, expected_baud_rate)
        assert st.connection.baudrate == expected_baud_rate

    def test_available(self, mocker):
        serial_port_list = ["my_serial_port"]
        test_port = "my_serial_port"
        mocker.patch(
            "serial.tools.list_ports.comports",
            return_value=[mocker.Mock(device=item) for item in serial_port_list],
        )
        mocked_serial = mocker.patch("serial.Serial", autospec=True)
        mocked_serial.return_value.open.return_value = True
        mocked_serial.return_value.in_waiting = True
        mocked_serial.return_value.read.return_value = b"\x7E\xFF\x00\x81"
        st = SerialTransfer(test_port)
        assert st.connection.read() == "parp"

        assert st.connection.open() == True

    # def test_invalid_serial_port_unrestricted(self, mocker):
    #     mocker.patch(
    #         "serial.tools.list_ports.comports",
    #         return_value=[mocker.Mock(device="this_is_a_serial_device")],
    #     )
    #     _, slave = pty.openpty()
    #     slave_name = os.ttyname(slave)
    #     with pytest.raises(InvalidSerialPort):
    #         st = SerialTransfer(slave_name)
