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
