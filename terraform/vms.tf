resource "opennebula_virtual_machine" "r1" {
  name        = format("%s-%s", var.user-id, "lab1-r1")
  template_id = data.opennebula_template.deb.id
  nic {
    network_id = data.opennebula_virtual_network.nat.id
  }
  nic {
    network_id = data.opennebula_virtual_network.man.id
  }
  nic {
    network_id      = resource.opennebula_virtual_network.srv-lan.id
    ip              = "192.168.13.1"
    security_groups = resource.opennebula_virtual_network.srv-lan.security_groups
  }
  nic {
    network_id      = resource.opennebula_virtual_network.lan1.id
    ip              = "192.168.7.1"
    security_groups = resource.opennebula_virtual_network.lan1.security_groups
  }
  depends_on = [opennebula_virtual_network_address_range.srv-lan-gw, opennebula_virtual_network_address_range.lan1-gw]
}

resource "opennebula_virtual_machine" "srv" {
  count       = 2
  name        = format("%s-%s", var.user-id, "lab1-srv${count.index + 1}")
  template_id = data.opennebula_template.deb.id
  nic {
    network_id = data.opennebula_virtual_network.man.id
  }
  nic {
    network_id      = resource.opennebula_virtual_network.srv-lan.id
    ip              = "192.168.13.${count.index + 10}"
    security_groups = resource.opennebula_virtual_network.lan1.security_groups
  }
  depends_on = [opennebula_virtual_machine.r1, opennebula_virtual_network_address_range.srv-lan]
}

resource "opennebula_virtual_machine" "pc" {
  name        = format("%s-%s", var.user-id, "lab1-pc")
  template_id = data.opennebula_template.deb.id
  nic {
    network_id = data.opennebula_virtual_network.man.id
  }
  nic {
    network_id      = resource.opennebula_virtual_network.lan1.id
    ip              = "192.168.7.10"
    security_groups = resource.opennebula_virtual_network.lan1.security_groups
  }
  depends_on = [opennebula_virtual_machine.r1, opennebula_virtual_network_address_range.lan1]
}
