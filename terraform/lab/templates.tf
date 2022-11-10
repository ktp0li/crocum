data "opennebula_template" "deb" {
  name       = "test"
  has_cpu    = true
  has_vcpu   = true
  has_memory = true
}
