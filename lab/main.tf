terraform {
  required_providers {
    opennebula = {
      source  = "OpenNebula/opennebula"
      version = "1.0.1"
    }
  }
}

provider "opennebula" {
  endpoint = "http://localhost:2633/RPC2"
  username = "oneadmin"
  password = "qwe"
  insecure = true
}

variable "user-id" {
  type    = string
  default = "test"
}

data "opennebula_virtual_network" "nat" {
  name = "NAT"
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

data "opennebula_template" "deb" {
  name       = "test"
  has_cpu    = true
  has_vcpu   = true
  has_memory = true
}

resource "opennebula_virtual_machine" "r1" {
  name        = format("%s-%s", var.user-id, "lab1-r1")
  template_id = data.opennebula_template.deb.id
  nic {
    network_id = data.opennebula_virtual_network.nat.id
  }
  nic {
    network_id = resource.opennebula_virtual_network.srv-lan.id
    ip         = "192.168.13.1"
  }
  nic {
    network_id = resource.opennebula_virtual_network.lan1.id
    ip         = "192.168.7.1"
  }
}

resource "opennebula_virtual_machine" "srv" {
  count       = 2
  name        = format("%s-%s", var.user-id, "lab1-srv${count.index + 1}")
  template_id = data.opennebula_template.deb.id
  nic {
    network_id = resource.opennebula_virtual_network.srv-lan.id
  }
}

resource "opennebula_virtual_machine" "pc" {
  name        = format("%s-%s", var.user-id, "lab1-pc")
  template_id = data.opennebula_template.deb.id
  nic {
    network_id = resource.opennebula_virtual_network.lan1.id
  }
}
