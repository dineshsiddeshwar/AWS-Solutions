module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-associate-public-ip-address-is-missing.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
