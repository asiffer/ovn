import time

from ovn.models import DHCPOptions, LogicalRouter, LogicalSwitch


class TestLogicalSwitch:
    def test_create(self):
        obj = LogicalSwitch()
        obj.save()

    def test_init(self):
        obj = LogicalSwitch(name="LogicalSwitch_to_test")
        obj.save()

    def test_update(self):
        obj = LogicalSwitch()
        obj.save()
        obj.name = "LogicalSwitch2_to_test"
        obj.save()

    def test_add_and_remove(self):
        obj = LogicalSwitch(name="LogicalSwitch_to_delete")
        obj.save()
        obj.delete()

    def test_add_port(self):
        obj = LogicalSwitch(name="LogicalSwitch_to_test")
        obj.save()
        port = obj.create_port(
            name="LogicalPort0", addresses=set(["80:fa:5b:06:72:b7 10.0.0.4"])
        )
        print(port)

    def test_plug_with_logical_router_port(self):
        router = LogicalRouter(name="router0")
        router.save()

        switch = LogicalSwitch(name="switch0")
        switch.save()

        routerport = router.create_port(
            name="routerport0",
            mac="00:11:22:33:44:55",
            networks="192.168.100.0/24",
        )

        time.sleep(0.5)

        switchport = switch.create_port(name="switchport0")
        switchport.plug(routerport)

    def test_plug_with_router(self):
        router = LogicalRouter(name="router0")
        router.save()

        switch = LogicalSwitch(name="switch0")
        switch.save()

        switch.plug(
            router,
            mac="00:11:22:33:44:55",
            networks="192.168.100.1/24",
        )

    def test_delete_all(self):
        for obj in LogicalSwitch.list():
            obj.delete()


class TestLogicalRouter:
    def test_create(self):
        obj = LogicalRouter()
        obj.save()

    def test_init(self):
        obj = LogicalRouter(name="LogicalRouter_to_test")
        obj.save()

    def test_update(self):
        obj = LogicalRouter()
        obj.save()
        obj.name = "LogicalRouter2_to_test"
        obj.save()

    def test_add_and_remove(self):
        obj = LogicalRouter(name="LogicalRouter_to_delete")
        obj.save()
        obj.delete()

    def test_add_port(self):
        obj = LogicalRouter(name="LogicalSRouter_to_test")
        obj.save()
        port = obj.create_port(
            name="LogicalPort0",
            mac="aa:bb:cc:dd:ee:ff",
            networks="10.10.10.10/16",
        )
        print(port)

    def test_delete_all(self):
        for obj in LogicalRouter.list():
            obj.delete()


class TestDHCPOptions:
    def test_create(self):
        obj = DHCPOptions()
        obj.save()

    def test_init(self):
        options = {
            "server_id": "10.0.50.1",
            "server_mac": "aa:bb:aa:bb:aa:bb",
            "lease_time": "3600000",
        }
        obj = DHCPOptions(cidr="10.0.50.0/24", options=options)
        obj.save()

    def test_update(self):
        obj = DHCPOptions()
        obj.save()
        obj.cidr = "10.0.50.0/24"
        obj.save()

    def test_add_and_remove(self):
        options = {
            "server_id": "10.0.0.1",
            "server_mac": "aa:bb:aa:bb:aa:bb",
            "lease_time": "3600000",
        }
        obj = DHCPOptions(cidr="10.0.0.0/24", options=options)
        obj.save()
        obj.delete()

    def test_with_switch(self):
        # create options
        server_mac = "aa:bb:aa:bb:aa:bb"
        server_ip = "172.0.42.1"
        options = {
            "server_id": server_ip,
            "server_mac": server_mac,
            "lease_time": "3600",
        }
        cidr = "172.0.42.0/24"
        dhcpv4_options = DHCPOptions(cidr=cidr, options=options)
        dhcpv4_options.save()

        # create a switch
        switch = LogicalSwitch(
            name="switch_with_auto_dhcp", other_config={"subnet": cidr}
        )
        switch.save()

        # create a router
        router = LogicalRouter(name="router_with_auto_dhcp")
        router.save()

        # sp0 = switch.create_port(
        #     name="sp0",
        #     dhcpv4_options=dhcpv4_options._uuid,
        #     addresses=set(["dynamic"]),
        # )

        sp1 = switch.create_port(
            name="sp1", addresses=set([f"{server_mac} 172.0.42.5"])
        )
        # rp = router.create_port(
        #     name="rp0",
        #     mac=server_mac,
        #     networks="172.0.42.1/24",
        # )

        time.sleep(0.5)
        sp1.fetch()
        print(sp1)
        # switch.fetch()
        # router.fetch()
        # sp.plug(rp)
        # sp, rp = switch.plug(
        #     router,
        #     # mac=mac,
        #     # networks="172.0.42.1/24",
        # )
        # sp.dhcpv4_options = obj._uuid
        # sp.addresses = set(["dynamic"])
        # sp.save()
        # print(sp)
        # time.sleep(1)
        # sp.fetch()
        # rp.fetch()
        # print(sp)
        # print(rp)
        # router.delete()
        # switch.delete()

    def test_delete_all(self):
        for obj in DHCPOptions.list():
            obj.delete()
