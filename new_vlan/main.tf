terraform {
  required_providers {
    opennebula = {
      source  = "OpenNebula/opennebula"
      version = "~> 1.0"
    }
  }
}

provider "opennebula" {
  endpoint = "http://localhost:2633/RPC2"
  username = "oneadmin"
  password = "qwe"
  insecure = true
}

resource "opennebula_virtual_network" "example" {
  name            = "virtual-network"
  type            = "802.1Q"
  vlan_id         = "100"
  dns             = "172.16.100.1"
  gateway         = "172.16.100.1"
  security_groups = [0]
  clusters        = [0]
  network_address = "172.16.100.0"
  network_mask    = "255.255.255.0"
  physical_device = "ens18"
}
resource "opennebula_virtual_network_address_range" "example0" {
  virtual_network_id = opennebula_virtual_network.example.id
  ar_type            = "IP4"
  size               = 64
  ip4                = "172.16.100.128"
}

resource "opennebula_virtual_network_address_range" "example1" {
  virtual_network_id = opennebula_virtual_network.example.id
  ar_type            = "IP4"
  size               = 64
  ip4                = "172.16.200.128"
}

resource "opennebula_virtual_network_address_range" "example2" {
  virtual_network_id = opennebula_virtual_network.example.id
  ar_type            = "IP4"
  size               = 64
  ip4                = "172.16.250.128"
}
