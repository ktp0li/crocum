def test_nat(host):
    rules = ['-A POSTROUTING -s 192.168.13.0/24 -o ens18 -j MASQUERADE',
             '-A POSTROUTING -s 192.168.7.0/24 -o ens18 -j MASQUERADE']
    nat = host.iptables.rules('nat', 'POSTROUTING')
    count = all(item in nat for item in rules)
    assert count


def test_internet(host):
    google = host.addr("8.8.8.8")
    assert google.is_reachable


def test_dns(host):
    yandex = host.addr('ya.ru')
    assert yandex.is_resolvable


def test_ens19_address(host):
    address = '192.168.13.1'
    ens19 = host.interface("ens19").addresses
    assert (address in ens19)


def test_ens20_address(host):
    address = '192.168.7.1'
    ens20 = host.interface("ens20").addresses
    assert (address in ens20)


def test_dhcprelay_installed(host):
    dhcp = host.package("isc-dhcp-relay")
    assert dhcp.is_installed


def test_dhcprelay_running_and_enabled(host):
    dhcp = host.service("isc-dhcp-relay")
    assert (dhcp.is_running and dhcp.is_enabled)


def test_dhcprelay_dhcp_servers(host):
    dhcp_serv = "192.168.13.11"
    conf = host.file("/etc/default/isc-dhcp-relay")
    assert (conf.contains(f'^SERVERS="{dhcp_serv}"$'))

def test_dhcprelay_listening_ifaces(host):
    conf = host.file("/etc/default/isc-dhcp-relay")
    assert (conf.contains(r'^INTERFACES="ens19\|ens20 ens19\|ens20"$'))
