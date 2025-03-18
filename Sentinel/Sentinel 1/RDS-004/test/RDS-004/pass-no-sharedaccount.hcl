module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-no-sharedaccount.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
