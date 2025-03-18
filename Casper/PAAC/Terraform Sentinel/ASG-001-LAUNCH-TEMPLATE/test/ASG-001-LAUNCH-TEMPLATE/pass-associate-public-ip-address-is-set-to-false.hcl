module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-associate-public-ip-address-is-set-to-false.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
