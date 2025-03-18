module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-associate-public-ip-address-is-set-to-true.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
