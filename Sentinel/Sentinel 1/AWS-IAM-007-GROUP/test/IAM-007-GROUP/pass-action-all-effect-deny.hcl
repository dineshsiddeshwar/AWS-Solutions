module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-action-all-effect-deny.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
