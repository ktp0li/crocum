terraform {
  required_providers {
    opennebula = {
      source  = "OpenNebula/opennebula"
      version = "1.0.1"
    }
  }
}

provider "opennebula" {
  endpoint = var.endpoint
  username = var.username
  password = var.password
  insecure = true
}

data "opennebula_virtual_network" "nat" {
  name = "NAT"
}

data "opennebula_template" "nat" {
  name = "test"
  has_cpu = true
  has_vcpu = true
  has_memory = true
}

#data "opennebula_template" "deb" {
#  name = "Debian11"
#}

resource "opennebula_virtual_machine" "nat" {
  name        = "test"
  template_id = data.opennebula_template.nat.id
  nic {
    network_id = data.opennebula_virtual_network.nat.id
  }
}

