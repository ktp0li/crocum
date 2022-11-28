data "opennebula_virtual_network" "nat" {
  name = "NAT"
}
data "opennebula_virtual_network" "man" {
  name = "management"
}

resource "opennebula_virtual_network" "srv-lan" {
  name              = format("%s-%s", var.user-id, "lab1-srv-lan")
  type              = "802.1Q"
  dns               = "8.8.8.8"
  gateway           = "192.168.13.1"
  network_address   = "192.168.13.0"
  network_mask      = "255.255.255.0"
  automatic_vlan_id = true
  physical_device   = "ens18"
}
resource "opennebula_virtual_network_address_range" "srv-lan" {
  virtual_network_id = opennebula_virtual_network.srv-lan.id
  ar_type            = "IP4"
  size               = 200
  ip4                = "192.168.13.10"
}
resource "opennebula_virtual_network_address_range" "srv-lan-gw" {
  virtual_network_id = opennebula_virtual_network.srv-lan.id
  ar_type            = "IP4"
  size               = 1
  ip4                = "192.168.13.1"
}

resource "opennebula_virtual_network" "lan1" {
  name              = format("%s-%s", var.user-id, "lab1-lan1")
  type              = "802.1Q"
  dns               = "8.8.8.8"
  gateway           = "192.168.7.1"
  network_address   = "192.168.7.0"
  network_mask      = "255.255.255.0"
  automatic_vlan_id = true
  physical_device   = "ens18"
}
resource "opennebula_virtual_network_address_range" "lan1" {
  virtual_network_id = opennebula_virtual_network.lan1.id
  ar_type            = "IP4"
  size               = 200
  ip4                = "192.168.7.10"
}
resource "opennebula_virtual_network_address_range" "lan1-gw" {
  virtual_network_id = opennebula_virtual_network.lan1.id
  ar_type            = "IP4"
  size               = 1
  ip4                = "192.168.7.1"
}
