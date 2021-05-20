from ovsdb.application import OVSDBClient


def test_ovn_echo(ovn_northd_client: OVSDBClient):
    ovn_northd_client.echo()


def test_ovn_list_dbs(ovn_northd_client: OVSDBClient):
    dbs = ovn_northd_client.list_dbs()
    assert 'OVN_Northbound' in dbs
    assert '_Server' in dbs


def test_ovn_get_schema(ovn_northd_client: OVSDBClient):
    schema = ovn_northd_client.get_schema('OVN_Northbound')
    for k in ['cksum', 'name', 'version', 'tables']:
        assert k in schema.keys()
